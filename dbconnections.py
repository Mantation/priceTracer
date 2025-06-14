import mysql.connector
from mysql.connector import pooling

@property
def uniqueId(self):
    return self._name

@uniqueId.setter
def uniqueId(self, name):
        self.name = name

dbconnection = {
    "table": "",
    "price": "",
    "items": "",
}

pointer = "local"

def init_db(site="amazon", point_to="local"):
    if point_to == "local":
        
        if site == "amazon":
            dbconnection["items"] = "amazon_items"
            dbconnection["price"] = "amazon_prices"
            primary_host = "localhost"
        else: 
            dbconnection["items"] = "takealot_items"
            dbconnection["price"] = "takealot_prices"
            primary_host = "localhost"

        host = "154.0.168.118"
        mydb = mysql.connector.connect(
                host= "154.0.168.118",
                user="weoblyak_admin",
                password="Khwezla@2014",
                database="weoblyak_weOblij",
                port=3306
            )
    else:
        primary_host = "154.0.168.118"
        if site == "amazon":
            dbconnection["items"] = "amazon_items"
            dbconnection["price"] = "amazon_prices"
            primary_host = "154.0.168.118"
        else: 
            dbconnection["items"] = "takealot_items"
            dbconnection["price"] = "takealot_prices"
            primary_host = "154.0.168.118"

        mydb = mysql.connector.connect(
                host= "154.0.168.118",
                user="weoblyak_admin",
                password="Khwezla@2014",
                database="weoblyak_weOblij",
                port=3306
            )

    print("connected!")


    return mydb

def showAllItems(database, img):
    mydb = database
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM "+dbconnection["items"])
    myresult = mycursor.fetchall()

    for row in myresult:
        if row is not None:
            print(row)
            print(row[2])
            print("<><><><><><><><><><>")

def pricesWithinTheWeek(database, uniqueId):
    inWeek = False
    mydb = database
    mycursor = mydb.cursor()
    x = None
    sql = "SELECT * FROM "+dbconnection["price"]+" WHERE item_id = %s AND WEEK(date, 1) = WEEK(CURDATE(), 1) AND YEAR(date) = YEAR(CURDATE())"
    val = (uniqueId,)
    mycursor.execute(sql,val)
    myresult = mycursor.fetchall()
    for row in myresult:
        if row is not None:
            inWeek = True
            break

    return inWeek

def itemExists(database, link):
    Found = False
    mydb = database
    mycursor = mydb.cursor()
    sql = "SELECT * FROM "+dbconnection["items"]+" WHERE item_link = %s"
    val = (link,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()

    for row in myresult:
        if row is not None:
            Found = True
            break

    return Found

def itemImageExists(database, image):
    Found = False
    mydb = database
    mycursor = mydb.cursor()
    sql = "SELECT * FROM "+dbconnection["items"]+" WHERE item_image = %s"
    val = (image,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()

    for row in myresult:
        if row is not None:
            Found = True
            break

    return Found

def getUniqueitemId(database, link):
    uniqueId = 0
    mydb = database
    mycursor = mydb.cursor()
    sql = "SELECT * FROM "+dbconnection["items"]+" WHERE item_link = %s LIMIT 1"
    val = (link,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()

    for row in myresult:
        if row is not None:
            uniqueId = row[0]
            break
    
    return uniqueId
    
def loadItem(database, item_array):
    last_id = 0
    mydb = database
    mycursor = mydb.cursor()
    # Define the INSERT statement
    sql = "INSERT INTO "+dbconnection["items"]+" (id,item_category,item_subcategory,item_type,item_description, item_image, item_link) VALUES (%s, %s,%s, %s, %s,%s, %s)"
    val = (0, item_array[0],item_array[1],item_array[2],item_array[3],item_array[4],item_array[5])


    # Execute the INSERT statement
    mycursor.execute(sql, val)

    # Commit the transaction
    mydb.commit()

    last_id = mycursor.lastrowid

    # Check if the insert was successful
    if mycursor.rowcount > 0:
        print("Insert was successful.")
        print(mycursor.rowcount, "record inserted.")
    else:
        print("Insert failed.")

    return last_id

def loadPrice(database, item_array):
    mydb = database
    mycursor = mydb.cursor()
    # Define the INSERT statement
    sql = "INSERT INTO "+dbconnection["price"]+" (id,item_id, item_price, date, time) VALUES (%s, %s,%s,%s,%s)"
    val = (0, item_array[0],item_array[1],item_array[2],item_array[3])

    # Execute the INSERT statement
    mycursor.execute(sql, val)

    # Commit the transaction
    mydb.commit()

    # Check if the insert was successful
    if mycursor.rowcount > 0:
        print("Insert was successful.")
        print(mycursor.rowcount, "record inserted.")
    else:
        print("Insert failed.")

#print(pricesWithinTheWeek(init_db()))

#init_db(site="takealot",point_to=pointer)

def showAllItems(connection_pool):
    conn = connection_pool.get_connection()
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM takealot_items")
    myresult = mycursor.fetchall()

    for row in myresult:
        if row is not None:
            print(row)
            print(row[2])
            print("<><><><><><><><><><>")