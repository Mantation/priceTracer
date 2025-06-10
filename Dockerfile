# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN apt-get update && apt-get install -y    \
    apt-utils       \
    wget    \
    gnupg   \
    gpg     \
    unzip   \
    curl    \
    xvfb    \
    libxi6  \
    libgconf-2-4    \
    libnss3     \
    libxss1     \
    libappindicator1    \
    #libindicator7       \
    fonts-liberation    \
    libasound2      \
    libatk-bridge2.0-0  \
    libgtk-3-0  \
    libx11-xcb1     \
    libxcomposite1  \
    libxcursor1     \
    libxdamage1     \
    libxrandr2      \
    libgbm1         \
    libpango1.0-0   \
    libpangocairo-1.0-0     \
    libatk1.0-0     \
    libatspi2.0-0       \
    libgtk-3-0
# Install dependencies

# Add Google Chrome repository key
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg

# Add Google Chrome repository
RUN sh -c 'echo "deb [signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'

# Install Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# Install ChromeDriver
RUN wget -N https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip -P /tmp && \
    unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .
# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Install pytest
RUN pip install pytest

# Create a new user and switch to that user
RUN adduser --disabled-password --gecos '' newuser && \
    chown -R newuser:newuser /app

USER newuser

# Kill any running Chrome instances
RUN pkill -f chrome || true

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME PATH="/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin:/usr/local/bin/chromedriver:/usr/bin/google-chrome-stable"

# Run app.py when the container launches
#CMD ["xvfb-run", "-a", "pytest"]
CMD ["python", "takealot.py"]
