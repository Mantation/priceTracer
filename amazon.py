from mysql.connector import OperationalError
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import StaleElementReferenceException,TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller
from datetime import datetime
import os
import tempfile
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import dbconnection

amzn = {
    "item_category": "",
    "item_subcategory": "",
    "item_type": "",
}

def submenuNavigator(driver, compareText):
    outer_div = driver.find_element(By.ID, "s-refinements")
    innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
    inner_ul = innerDiv[0].find_element(By.TAG_NAME, "ul")
    inner_lis = inner_ul.find_elements(By.TAG_NAME, "li")
    for inner_li in inner_lis:
        print(inner_li.text)
    try:
        a = inner_li.find_element(By.TAG_NAME, "a")
        print("clicking "+a.text)
        if a.is_displayed():
            driver.execute_script("arguments[0].click();", a)
            time.sleep(5)
            ###############################################################################
            outer_div_ = driver.find_element(By.ID, "s-refinements")
            innerDiv_ = outer_div_.find_elements(By.TAG_NAME, "div")
            inner_ul_ = innerDiv_[0].find_element(By.TAG_NAME, "ul")
            inner_lis_ = inner_ul_.find_elements(By.TAG_NAME, "li")
            newcounter_ = 0
            for inner_li_ in inner_lis_:
                if newcounter_ > 1:
                    time.sleep(5)
                    #sub_li.click()
                    try:
                        a = inner_li_.find_element(By.TAG_NAME, "a")
                        if a.is_displayed():
                            if a.text.lower() == compareText:
                                driver.execute_script("arguments[0].click();", a)
                                time.sleep(5)
                        else:
                            print("Element is not attached to the DOM.")
                                                        
                    except StaleElementReferenceException:
                        print("Element is stale and not found in the DOM.")
                        #a.click()
                newcounter_+=1
        else:
            print("Element is not attached to the DOM.")
                                        
    except StaleElementReferenceException:
        print("Element is stale and not found in the DOM.")
                                    #a.click()

def elementExists(element):
    exists = False
    try:
        if element:
             exists = True
             print("Element Exists.")
        else:
            exists = False
            print("Element doesn't exist")
                                
    except NoSuchElementException:
        print("Element doesn't exist.")
        exists = False

    return exists

def elementDisplayed(element):
    exists = False
    try:
        if element.is_displayed():
             exists = True
             print("Element Exists.")
        else:
            exists = False
            print("Element doesn't exist")
                                
    except NoSuchElementException:
        print("Element doesn't exist.")
        exists = False

    return exists

def getLastPage(driver):
    maxNum = 1
        
    aTags = driver.find_elements(By.CLASS_NAME, "s-pagination-item")
    if len(aTags) == 7:
        maxNum = aTags[5].get_attribute("innerText")
    elif len(aTags) == 6:
        maxNum = aTags[4].get_attribute("innerText")
    elif len(aTags) == 5:
        maxNum = aTags[3].get_attribute("innerText")
    elif len(aTags) == 4:
        maxNum = aTags[2].get_attribute("innerText")
    elif len(aTags) == 3:
        maxNum = aTags[1].get_attribute("innerText")

    return str(maxNum)

def getBrowserLink(driver):
    current_url = driver.current_url
    return current_url

def changeBrowserLinkParams(driver,params):
    current_url = getBrowserLink(driver)

def loopThroughProducts(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
        print("error has occured page on departmentCategories, refreshing page")
        driver.refresh()
    except TimeoutException:
        print("Page on departmentCategories displaying correctly, proceeding.....")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 's-desktop-width-max')))
    mainCover = driver.find_elements(By.CLASS_NAME, "s-desktop-width-max")
    MainDiv = mainCover[1].find_elements(By.CLASS_NAME, "sg-col-inner")
    MainSlot = MainDiv[0].find_elements(By.CLASS_NAME, "s-main-slot")
    innerDivs = MainSlot[0].find_elements(By.TAG_NAME, "div")
    total = len(innerDivs)

    for i in range(1, total):
        if innerDivs[i].get_attribute("data-asin") is not None and innerDivs[i].get_attribute("data-asin"):
            aTags = innerDivs[i].find_elements(By.TAG_NAME, "a")
            driver.execute_script("arguments[0].setAttribute('target', '_new')", aTags[0])
            time.sleep(2)
            driver.execute_script("arguments[0].click();", aTags[0])
            #ActionChains(driver).key_down(Keys.CONTROL).click(aTags[0]).key_up(Keys.CONTROL).perform()
            time.sleep(2)
            driver.switch_to.window(driver.window_handles[1])

            # Switch to the new tab
            num_tabs = len(driver.window_handles)
            if num_tabs > 1:
                getItemsInfo(driver)

        if i == total:
            navigateBackOnCategories(driver, "Ribs")

def loopThroughitems(driver):
    count = 0
    for i in range(2, 30):
        items = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div['+str(i)+']')))

        #items = driver.find_element(By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div['+str(i)+']')
        item_class = items.get_attribute("class")
        if "sg-col-4-of-24" not in item_class:
            break
        else:
            print(items.get_attribute("class"))
            print(items.get_attribute("data-component-id"))
            print(items.get_attribute("data-asin"))
            time.sleep(2)
            clickItem = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div['+str(i)+']')))
            #items.click()
            ActionChains(driver).key_down(Keys.CONTROL).click(items).key_up(Keys.CONTROL).perform()
            time.sleep(2)
            driver.switch_to.window(driver.window_handles[1])
            #clickItem.click()
            time.sleep(2)
            try:
                if elementExists(driver.find_element(By.ID, "productTitle")):
                    try:
                        item_title = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, 'productTitle')))
                    except TimeoutException:
                        driver.execute_script("window.stop();")
                else:
                    #clickItem.click()
                    ActionChains(driver).key_down(Keys.CONTROL).click(clickItem).key_up(Keys.CONTROL).perform()
                    time.sleep(2)
                    driver.switch_to.window(driver.window_handles[1])
            except NoSuchElementException:
                time.sleep(5)
                num_tabs = len(driver.window_handles)
                if num_tabs > 1:
                    driver.switch_to.window(driver.window_handles[1])
                else:
                    newitem = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div['+str(i)+']')))
                    ActionChains(driver).key_down(Keys.CONTROL).click(newitem).key_up(Keys.CONTROL).perform()
                    driver.switch_to.window(driver.window_handles[1])
                    if elementExists(driver.find_element(By.ID, "productTitle")):
                        try:
                            item_title = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.ID, 'productTitle')))
                        except TimeoutException:
                            driver.execute_script("window.stop();")  
                    else:
                        ActionChains(driver).key_down(Keys.CONTROL).click(newitem).key_up(Keys.CONTROL).perform()
                        driver.switch_to.window(driver.window_handles[1])
                
                        
            # Switch to the new tab
            num_tabs = len(driver.window_handles)
            if num_tabs > 1:
                item_info_collected = getItemsInfo(driver)
                if not item_info_collected:
                    newitem = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div['+str(count - 1)+']')))
                    ActionChains(driver).key_down(Keys.CONTROL).click(newitem).key_up(Keys.CONTROL).perform()
                    driver.switch_to.window(driver.window_handles[1])
                    getItemsInfo(driver)

        count+=1

def getItemsInfo(driver):
    item_info_gathered = True
    try:
        item_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'productTitle')))
    except TimeoutException:
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Click here to go back to the Amazon home page")))
            back_home = driver.find_element(By.LINK_TEXT, "Click here to go back to the Amazon home page")
            item_info_gathered = False
        except TimeoutException:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "Click here to return to the Amazon home page")))
                return_home = driver.find_element(By.LINK_TEXT, "Click here to return to the Amazon home page")
                item_info_gathered = False
            except TimeoutException:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
                    driver.refresh()
                except TimeoutException:
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "a-logo")))
                        driver.refresh()
                        logo = driver.find_elements(By.CLASS_NAME, "a-logo")
                        if len(logo)>0:
                            input("Press Enter to continue...")
                        else:
                            item_info_gathered = True
                    except TimeoutException:
                        item_info_gathered = False
    
    try:
        item_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'productTitle')))
        item_info_gathered = True
    except TimeoutException:
        item_info_gathered = False

    if item_info_gathered:
        try:
            item_imgDiv = driver.find_element(By.ID, "imgTagWrapperId")
            item_imgSearch = item_imgDiv.find_element(By.TAG_NAME, "img")
        except NoSuchElementException:
            item_imgSearch = driver.find_element(By.ID, "landingImage")
        item_img = item_imgSearch.get_attribute("src")
        item_amount = "unavailable"
        try:
            item_price = driver.find_element(By.CLASS_NAME, "aok-offscreen") 
            item_amount = item_price.get_attribute("innerText").encode("utf-8")
        except NoSuchElementException:
            print("Price is not available for this item.")
        item_title = driver.find_element(By.ID, 'productTitle')
        item_link = driver.current_url
        print(item_title.get_attribute("innerText").encode("utf-8"))
        print(item_img)
        print(item_amount)
        print(item_link)

        #Add data to the DB
        items_array = [amzn["item_category"],amzn["item_subcategory"],amzn["item_type"],item_title.get_attribute("innerText").encode("utf-8"), item_img,item_link]
        #dbs = dbconnection.init_db("amazon",point_to=dbconnection.pointer)
        dbs = dbconnection.init_db("amazon",point_to="cloud")
        uniqueId = 0
        if not dbconnection.itemImageExists(dbs, item_img):
            uniqueId = dbconnection.loadItem(dbs,items_array)
        else:
            uniqueId = dbconnection.getUniqueitemId(dbs,item_link)
        try:
            if not dbconnection.pricesWithinTheWeek(dbs, uniqueId):
                now = datetime.now()
                date = now.strftime("%Y-%m-%d")
                time = now.strftime("%H:%M:%S")
                prices_array = [uniqueId,item_amount,date,time]
                dbconnection.loadPrice(dbs, prices_array)
        except OperationalError:
            dbs = dbconnection.init_db("amazon",point_to="cloud")
            if not dbconnection.pricesWithinTheWeek(dbs, uniqueId):
                now = datetime.now()
                date = now.strftime("%Y-%m-%d")
                time = now.strftime("%H:%M:%S")
                prices_array = [uniqueId,item_amount,date,time]
                dbconnection.loadPrice(dbs, prices_array)
            
        
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        firstItem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[2]')))
        
    else:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        firstItem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[2]')))
        
    return item_info_gathered
    
def getItemDetails(driver):
    try:
        if elementExists(driver.find_element(By.ID, "apb-desktop-browse-search-see-all")):
            resultsPagination = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'apb-desktop-browse-search-see-all')))
            allResults = driver.find_element(By.ID, "apb-desktop-browse-search-see-all")
            if elementExists(allResults):
                if elementDisplayed(allResults):
                    allResults.click()
                    time.sleep(5)
                    last_page = getLastPage(driver)
                    next_is_enabled = True
                    paginations = driver.find_elements(By.CLASS_NAME, "s-pagination-item")
                    if len(paginations) == 0:
                        next_is_enabled = False
                        loopThroughProducts(driver)
                    #for pages in range(1,int(last_page)+1):
                    first_entry = True
                    while next_is_enabled:
                        count = 0
                        for page_item in paginations:
                            try:
                                WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
                                print("error has occured page, refreshing page")
                                driver.refresh()
                            except TimeoutException:
                                print("Page displaying correctly, proceeding.....")
                            if not first_entry:
                                #paginations[count].get_attribute("innerText")
                                WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, "s-pagination-item")))
                                try:
                                    Next = page_item.get_attribute("innerText")
                                    if Next == "Next":
                                        if "s-pagination-disabled" not in page_item.get_attribute("class"):
                                            next_is_enabled = True
                                            try:
                                                driver.execute_script("arguments[0].click();", page_item)
                                            except StaleElementReferenceException:
                                                driver.execute_script("arguments[0].click();", paginations[count])
                                            time.sleep(5)
                                            loopThroughProducts(driver)
                                                #break
                                                #aTags[pages].click()
                                        else:
                                            next_is_enabled = False
                                except StaleElementReferenceException:
                                    paginations = driver.find_elements(By.CLASS_NAME, "s-pagination-item")
                                    pageNum = 0
                                    try:
                                        Next = paginations[count].get_attribute("innerText")
                                        pageNum = count
                                    except IndexError:
                                        Next = paginations[6].get_attribute("innerText")
                                        pageNum = 6
                                    
                                    if Next == "Next":
                                        if "s-pagination-disabled" not in paginations[pageNum].get_attribute("class"):
                                            next_is_enabled = True
                                            try:
                                                driver.execute_script("arguments[0].click();", page_item)
                                            except StaleElementReferenceException:
                                                driver.execute_script("arguments[0].click();", paginations[pageNum])
                                            time.sleep(5)
                                            loopThroughProducts(driver)
                                                #break
                                                #aTags[pages].click()
                                        else:
                                            next_is_enabled = False
                                
                                
                            else:
                                first_entry = False
                                loopThroughProducts(driver)

                            count+=1
                            #loopThroughProducts(driver)
                            #loopThroughitems(driver)
                    
                    navigateBackOnCategories(driver, "navigating back")
                else:
                    loopThroughProducts(driver)
            else:
                loopThroughProducts(driver)
        else:
            loopThroughProducts(driver)
                                
    except NoSuchElementException:
        print("See all results button unavailable.")
        last_page = getLastPage(driver)
        next_is_enabled = True
        paginations = driver.find_elements(By.CLASS_NAME, "s-pagination-item")
        if len(paginations) == 0:
            next_is_enabled = False
            loopThroughProducts(driver)
        
        #for pages in range(1,int(last_page)+1):
        
        first_entry = True
        while next_is_enabled:
            count = 0
            for page_item in paginations:
                if not first_entry:
                    #paginations[count].get_attribute("innerText")
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "s-pagination-item")))
                    try:
                        Next = page_item.get_attribute("innerText")
                        if Next == "Next":
                            if "s-pagination-disabled" not in page_item.get_attribute("class"):
                                next_is_enabled = True
                                try:
                                    driver.execute_script("arguments[0].click();", page_item)
                                except StaleElementReferenceException:
                                    driver.execute_script("arguments[0].click();", paginations[count])
                                time.sleep(5)
                                loopThroughProducts(driver)
                                                        #break
                                                        #aTags[pages].click()
                            else:
                                next_is_enabled = False
                    except StaleElementReferenceException:
                        paginations = driver.find_elements(By.CLASS_NAME, "s-pagination-item")
                        pageNum = 0
                        try:
                            Next = paginations[count].get_attribute("innerText")
                            pageNum = count
                        except IndexError:
                            Next = paginations[6].get_attribute("innerText")
                            pageNum = 6
                        Next = paginations[pageNum].get_attribute("innerText")
                        if Next == "Next":
                            if "s-pagination-disabled" not in paginations[pageNum].get_attribute("class"):
                                next_is_enabled = True
                                try:
                                    driver.execute_script("arguments[0].click();", page_item)
                                except StaleElementReferenceException:
                                    driver.execute_script("arguments[0].click();", paginations[pageNum])
                                time.sleep(5)
                                loopThroughProducts(driver)
                                                        #break
                                                        #aTags[pages].click()
                            else:
                                next_is_enabled = False
                                        
                                        
                else:
                    first_entry = False
                    loopThroughProducts(driver)

                count+=1
                                    #loopThroughProducts(driver)
                                    #loopThroughitems(driver)
                    
        navigateBackOnCategories(driver, "navigating back")
         
def navigateBackOnDepartment(driver,index):
    scrollToTop(driver)
    time.sleep(5)
    department = driver.find_element(By.ID, "departments")
    ul = department.find_element(By.TAG_NAME, "ul")
    lis = ul.find_elements(By.TAG_NAME, "li")
    count = 0
    for li in lis:
        if count == index:
            li_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((li)))
            li.get_attribute("innerText")   
            li_element.get_attribute("innerText") 
            #driver.execute_script("arguments[0].click();", li)
            #lis[index].click()
            #li_element.click()
            #driver.execute_script("arguments[0].click();", li_element)
            try:
                element_name = li_element.get_attribute("innerText").strip()
                print("Sub Menu clicking on >> "+li.get_attribute("innerText"))
                print("Sub Menu clicking on >> "+lis[index].get_attribute("innerText"))
                print("Sub Menu clicking on >> "+li_element.get_attribute("innerText"))
                driver.find_element(By.LINK_TEXT, element_name).send_keys(Keys.ENTER)
                #driver.find_element(By.LINK_TEXT, element_name).click()
                li.click()
                lis[index].click()
                li_element.click()
                driver.execute_script("arguments[0].click();", li)
                driver.execute_script("arguments[0].click();", lis[index])
                driver.execute_script("arguments[0].click();", li_element)
            except ElementClickInterceptedException:
                # Handle the exception
                print("ElementClickInterceptedException caught. Handling it...")
                
                # Option 1: Scroll to the element and retry
                driver.execute_script("arguments[0].scrollIntoView(true);", li)
                print("Sub Menu clicking on >> "+li.get_attribute("innerText") )
                li.click()
                
                # Option 2: Use JavaScript to click the element
                # driver.execute_script("arguments[0].click();", element)
            
        count+=1

def NavigateBackOnRefinement(driver,index):
    scrollToTop(driver)
    time.sleep(5)
    refinement = driver.find_element(By.ID, "s-refinements")
    div = refinement.find_elements(By.TAG_NAME, "div")
    ul = div[0].find_element(By.TAG_NAME, "ul")
    lis = ul.find_elements(By.TAG_NAME, "li")
    count = 0
    for li in lis:
        if count == index:
            li_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((li)))
            li.get_attribute("innerText")   
            li_element.get_attribute("innerText") 
            
            try:
                element_name = li_element.get_attribute("innerText").strip()
                print("Core Menu clicking on >> "+li.get_attribute("innerText"))
                print("Core Menu clicking on >> "+lis[index].get_attribute("innerText"))
                print("Core Menu clicking on >> "+li_element.get_attribute("innerText"))
                driver.find_element(By.LINK_TEXT, element_name).send_keys(Keys.ENTER)
                #driver.find_element(By.LINK_TEXT, element_name).click()
                li.click()
                lis[index].click()
                li_element.click()
                driver.execute_script("arguments[0].click();", li)
                driver.execute_script("arguments[0].click();", lis[index])
                driver.execute_script("arguments[0].click();", li_element)
            except ElementClickInterceptedException:
                # Handle the exception
                print("ElementClickInterceptedException caught. Handling it...")
                
                # Option 1: Scroll to the element and retry
                driver.execute_script("arguments[0].scrollIntoView(true);", li)
                print("Core Menu clicking on >> "+li.get_attribute("innerText") )
                li.click()
        count+=1

def getFreshLiTagFromList(driver,index):
    scrollToTop(driver)
    #department = driver.find_element(By.ID, "departments")
    #driver.get(getBrowserLink(driver))
    department = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'departments')))
    ul = department.find_element(By.TAG_NAME, "ul")
    lis = ul.find_elements(By.TAG_NAME, "li")
    count = 0
    for li in lis:
        print(li.get_attribute("innerText"))
        if count == index:
            a = li.find_element(By.TAG_NAME, "a")
            print(a.get_attribute("innerText"))
            print("Trying to relocate the element")
            if a.is_displayed():
                driver.execute_script("arguments[0].click();", a)
                time.sleep(5)
                ###################################################################
                getItemDetails(driver)
                navigateBackOnDepartment(driver,3)
                break
            #WebDriverWait(driver, 10).until(EC.presence_of_element_located((li)))
            #liElement = lis[index]
            #liElement.click()
            #return lis[index]
            #result = li
            #break
        count+=1
    #return liElement

def getFreshATagFromList(driver,index,listName="dept"):
    scrollToTop(driver)
    #department = driver.find_element(By.ID, "departments")
    #driver.get(getBrowserLink(driver))
    lis = ""
    if listName == "dept":
        department = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'departments')))
        ul = department.find_element(By.TAG_NAME, "ul")
        lis = ul.find_elements(By.TAG_NAME, "li")
    elif listName == "refine":
        refinement = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 's-refinements')))
        #refinement = driver.find_element(By.ID, "s-refinements")
        div = refinement.find_elements(By.TAG_NAME, "div")
        ul = div[0].find_element(By.TAG_NAME, "ul")
        lis = ul.find_elements(By.TAG_NAME, "li")

    #department = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'departments')))
    #ul = department.find_element(By.TAG_NAME, "ul")
    #lis = ul.find_elements(By.TAG_NAME, "li")
    count = 0
    for li in lis:
        print(li.get_attribute("innerText"))
        if count == index:
            a = li.find_element(By.TAG_NAME, "a")
            print(a.get_attribute("innerText"))
            print("Trying to relocate the element")
            if a.is_displayed():
                #driver.execute_script("arguments[0].click();", a)
                time.sleep(5)
                ###################################################################
                return a
            #WebDriverWait(driver, 10).until(EC.presence_of_element_located((li)))
            #liElement = lis[index]
            #liElement.click()
            #return lis[index]
            #result = li
            #break
        count+=1
    #return liElement

def getFreshLiTagTextFromList(driver,index,listName="dept"):
    scrollToTop(driver)
    #department = driver.find_element(By.ID, "departments")
    #driver.get(getBrowserLink(driver))
    lis = ""
    if listName == "dept":
        department = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'departments')))
        ul = department.find_element(By.TAG_NAME, "ul")
        lis = ul.find_elements(By.TAG_NAME, "li")
    elif listName == "refine":
        refinement = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 's-refinements')))
        #refinement = driver.find_element(By.ID, "s-refinements")
        div = refinement.find_elements(By.TAG_NAME, "div")
        ul = div[0].find_element(By.TAG_NAME, "ul")
        lis = ul.find_elements(By.TAG_NAME, "li")
    elif listName == "hmenu":
        div = driver.find_element(By.ID, "hmenu-content")
        ul = div.find_elements(By.TAG_NAME, "ul")
        lis = ul[4].find_elements(By.TAG_NAME, "li")

    #department = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'departments')))
    #ul = department.find_element(By.TAG_NAME, "ul")
    #lis = ul.find_elements(By.TAG_NAME, "li")
    count = 0
    for li in lis:
        print(li.get_attribute("innerText"))
        if count == index:
            return li.get_attribute("innerText")
        count+=1
    #return liElement

def scrollToTop(driver):
    driver.execute_script("window.scrollTo(0, 0);")

def submenuItems(driver,item):
    time.sleep(5)
    print("Item is "+item)
    sub_div = driver.find_element(By.ID, "hmenu-content")
    sub_ul = sub_div.find_elements(By.CLASS_NAME, "hmenu-visible")
    WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME,"hmenu-visible")))
    if len(sub_ul) > 1:
        lis = sub_ul[1].find_elements(By.TAG_NAME, "li")
    else:
        lis = sub_ul[0].find_elements(By.TAG_NAME, "li")
    count = 0
    for li in lis:
        #Atag = lis[0].find_elements(By.TAG_NAME, "a")
        try:
            Atags = li.find_elements(By.TAG_NAME, "a")
            if len(Atags) > 0:
                if "hmenu-item" in Atags[0].get_attribute("class") and "all" not in Atags[0].get_attribute("innerText").lower():
                    if "main menu" not in Atags[0].get_attribute("innerText").lower():
                        itemRef = Atags[0].get_attribute("innerText")
                        print("Now navigating to "+Atags[0].get_attribute("innerText"))
                        amzn["item_subcategory"] = Atags[0].get_attribute("innerText")
                        driver.execute_script("arguments[0].click();", Atags[0])
                        departmentCategories(driver, itemRef)
        except StaleElementReferenceException:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID,"nav-hamburger-menu")))
            menu = driver.find_element(By.ID,"nav-hamburger-menu")
            time.sleep(5)
            menu.click()
            time.sleep(5)
            sub_div = driver.find_element(By.ID, "hmenu-content")
            sub_ul = sub_div.find_elements(By.CLASS_NAME, "hmenu-visible")
            WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME,"hmenu-visible")))
            if len(sub_ul) > 1:
                lis = sub_ul[1].find_elements(By.TAG_NAME, "li")
            else:
                lis = sub_ul[0].find_elements(By.TAG_NAME, "li")
            Atags = lis[count].find_elements(By.TAG_NAME, "a")
            if len(Atags) > 0:
                if "hmenu-item" in Atags[0].get_attribute("class") and "all" not in Atags[0].get_attribute("innerText").lower():
                    if "main menu" not in Atags[0].get_attribute("innerText").lower():
                        itemRef = Atags[0].get_attribute("innerText")
                        print("Now navigating to "+Atags[0].get_attribute("innerText"))
                        amzn["item_subcategory"] = Atags[0].get_attribute("innerText")
                        driver.execute_script("arguments[0].click();", Atags[0])
                        departmentCategories(driver, itemRef)

        #todo return back to nav bar menu
        #if len(lis) == count +1:
        #    print(item)
            #navigateBackOnRefinements(driver, item)
        count+=1

def departmentCategories(driver,item):
    print("Welcome "+item)
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
        print("error has occured page on departmentCategories, refreshing page")
        driver.refresh()
    except TimeoutException:
        print("Page on departmentCategories displaying correctly, proceeding.....")
    time.sleep(5)
    WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID,"s-refinements")))
    outer_div = driver.find_element(By.ID, "s-refinements")
    innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
    inner_ul = innerDiv[0].find_elements(By.TAG_NAME, "ul")
    if len(inner_ul) > 0:
        inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
    else:
        dept = driver.find_element(By.ID, "departments")
        inner_ul = dept.find_elements(By.TAG_NAME, "ul")
        inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")

    clicked_tag = ""
    count = 0
    countInnerLinks = 0
    hasInnerLinks = False

    for inner_li in inner_lis:
        print("Options are "+inner_li.get_attribute("innerText"))
        if "apb-browse-refinements-indent-2" in inner_li.get_attribute("class") or "s-navigation-indent-2" in inner_li.get_attribute("class"):
            countInnerLinks+=1
        
        if countInnerLinks > 0:
            hasInnerLinks = True
            break

    if hasInnerLinks:
        for inner_li in inner_lis:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
                print("error has occured page on departmentCategories, refreshing page")
                driver.refresh()
            except TimeoutException:
                print("Page on departmentCategories displaying correctly, proceeding.....")
            try:
                if len(inner_lis) > count:
                    Atags = inner_li.find_elements(By.TAG_NAME, "a")
                    if len(Atags) > 0 and count > 9:
                        inner_li.get_attribute("innerText")
                        if "apb-browse-refinements-indent-2" in inner_li.get_attribute("class") or  "s-navigation-indent-2" in inner_lis[count].get_attribute("class"):
                            itemRef = Atags[0].get_attribute("innerText")
                            clicked_tag = itemRef
                            print("Now navigating to "+Atags[0].get_attribute("innerText"))
                            amzn["item_type"] = itemRef
                            driver.execute_script("arguments[0].click();", Atags[0])
                            departmentSubCategories(driver, clicked_tag)
                            #navigateBackOnCategories(driver, clicked_tag)
            except StaleElementReferenceException:
                outer_div = driver.find_element(By.ID, "s-refinements")
                innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
                inner_ul = innerDiv[0].find_elements(By.TAG_NAME, "ul")
                if len(inner_ul) > 0:
                    inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
                else:
                    dept = driver.find_element(By.ID, "departments")
                    inner_ul = dept.find_elements(By.TAG_NAME, "ul")
                    inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
                if len(inner_lis) > count:
                    Atags = inner_lis[count].find_elements(By.TAG_NAME, "a")
                    if len(Atags) > 0 and count > 9:
                        inner_lis[count].get_attribute("innerText")
                        if "apb-browse-refinements-indent-2" in inner_lis[count].get_attribute("class") or  "s-navigation-indent-2" in inner_lis[count].get_attribute("class"):
                            itemRef = Atags[0].get_attribute("innerText")
                            clicked_tag = itemRef
                            print("Now navigating to "+Atags[0].get_attribute("innerText"))
                            amzn["item_type"] = itemRef
                            driver.execute_script("arguments[0].click();", Atags[0])
                            departmentSubCategories(driver, clicked_tag)
                            #navigateBackOnCategories(driver, clicked_tag)

            if len(inner_lis) == count +1:
                navigateBackOnRefinements(driver, item)
                break
            count+=1
    else:
        getItemDetails(driver)
        #navigateBackOnRefinements(driver, item)
        #navigateBackOnCategories(driver, item)

def departmentSubCategories(driver,item):
    print("SubCat Welcome "+item)
    time.sleep(5)
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
        print("error has occured page departmentSubCategories, refreshing page")
        driver.refresh()
    except TimeoutException:
        print("Page on departmentSubCategories displaying correctly, proceeding.....")

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID,"s-refinements")))
    outer_div = driver.find_element(By.ID, "s-refinements")
    innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
    inner_ul = innerDiv[0].find_elements(By.TAG_NAME, "ul")
    if len(inner_ul) > 0:
        inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
    else:
        dept = driver.find_element(By.ID, "departments")
        inner_ul = dept.find_elements(By.TAG_NAME, "ul")
        inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
    
    count = 0
    clicked_tag = ""
    countInnerLinks = 0
    hasInnerLinks = False

    for inner_li in inner_lis:
        print("Options are "+inner_li.get_attribute("innerText"))
        if "apb-browse-refinements-indent-2" in inner_li.get_attribute("class") or "s-navigation-indent-2" in inner_li.get_attribute("class"):
            countInnerLinks+=1
        
        if countInnerLinks > 0:
            hasInnerLinks = True
            break

    if hasInnerLinks:
        for inner_li in inner_lis:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
                print("error has occured page departmentSubCategories, refreshing page")
                driver.refresh()
            except TimeoutException:
                print("Page on departmentSubCategories displaying correctly, proceeding.....")
            try:
                if inner_li.get_attribute("class") is not None:
                    try:
                        Atags = inner_li.find_elements(By.TAG_NAME, "a")
                        print(inner_li.get_attribute("innerText"))
                    except StaleElementReferenceException:
                        #input("Press Enter to continue...")
                        Atags = inner_lis[count].find_elements(By.TAG_NAME, "a")
                        print(inner_li[count].get_attribute("innerText"))
                    #if len(Atags) > 0 and count > 6:
                    if len(Atags) > 0:
                        if "apb-browse-refinements-indent-2" in inner_li.get_attribute("class") or "s-navigation-indent-2" in inner_li.get_attribute("class"):
                            itemRef = Atags[0].get_attribute("innerText")
                            clicked_tag = itemRef
                            print("Now navigating to "+Atags[0].get_attribute("innerText"))
                            amzn["item_type"] = itemRef
                            driver.execute_script("arguments[0].click();", Atags[0])
                            departmentSubCategoriesOptions(driver, clicked_tag)
                            #navigateBackOnCategories(driver, clicked_tag)
            except StaleElementReferenceException:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
                    print("error has occured page, refreshing page")
                    driver.refresh()
                except TimeoutException:
                    print("Page displaying correctly, proceeding.....")
                outer_div = driver.find_element(By.ID, "s-refinements")
                innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
                inner_ul = innerDiv[0].find_elements(By.TAG_NAME, "ul")
                #if len(inner_ul) == 0:
                if len(inner_ul) > 0:
                    inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
                else:
                    dept = driver.find_element(By.ID, "departments")
                    inner_ul = dept.find_elements(By.TAG_NAME, "ul")
                    inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
                #filter-n
                #inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
                if inner_lis[count].get_attribute("class") is not None:
                    if len(inner_lis) > count:
                        Atags = inner_lis[count].find_elements(By.TAG_NAME, "a")
                        #if len(Atags) > 0 and count > 6:
                        if len(Atags) > 0:
                            if "apb-browse-refinements-indent-2" in inner_lis[count].get_attribute("class") or "s-navigation-indent-2" in inner_lis[count].get_attribute("class"):
                                inner_lis[count].get_attribute("class")
                                itemRef = Atags[0].get_attribute("innerText")
                                clicked_tag = itemRef
                                print("Now navigating to "+Atags[0].get_attribute("innerText"))
                                amzn["item_type"] = itemRef
                                driver.execute_script("arguments[0].click();", Atags[0])
                                departmentSubCategoriesOptions(driver, clicked_tag)
                                #navigateBackOnCategories(driver, clicked_tag)

            if len(inner_lis) == count +1:
                navigateBackOnRefinements(driver, item)
                break
            count+=1
    else:
        getItemDetails(driver)
        #navigateBackOnRefinements(driver, item)
        #navigateBackOnCategories(driver, item)

def departmentSubCategoriesOptions(driver,item):
    print("SubCat Option welcome "+item)
    time.sleep(5)
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
        print("error has occured page departmentSubCategoriesOptions, refreshing page")
        driver.refresh()
    except TimeoutException:
        print("Page on departmentSubCategoriesOptions displaying correctly, proceeding.....")
    
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID,"s-refinements")))
    outer_div = driver.find_element(By.ID, "s-refinements")
    innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
    inner_ul = innerDiv[0].find_elements(By.TAG_NAME, "ul")
    if len(inner_ul) > 0:
        inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
    else:
        dept = driver.find_element(By.ID, "departments")
        inner_ul = dept.find_elements(By.TAG_NAME, "ul")
        inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")

    count = 0
    clicked_tag = ""
    countInnerLinks = 0
    hasInnerLinks = False

    for inner_li in inner_lis:
        print("Options are "+inner_li.get_attribute("innerText"))
        if "apb-browse-refinements-indent-2" in inner_li.get_attribute("class") or "s-navigation-indent-2" in inner_li.get_attribute("class"):
            countInnerLinks+=1
        
        if countInnerLinks > 0:
            hasInnerLinks = True
            break

    if hasInnerLinks:
        for inner_li in inner_lis:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
                print("error has occured page departmentSubCategoriesOptions, refreshing page")
                driver.refresh()
            except TimeoutException:
                print("Page on departmentSubCategoriesOptions displaying correctly, proceeding.....")
            try:
                if inner_li.get_attribute("class") is not None:
                    try:
                        Atags = inner_li.find_elements(By.TAG_NAME, "a")
                        print(inner_li.get_attribute("innerText"))
                    except StaleElementReferenceException:
                        #input("Press Enter to continue...")
                        Atags = inner_lis[count].find_elements(By.TAG_NAME, "a")
                        print(inner_li[count].get_attribute("innerText"))
                if len(Atags) > 0:
                    if "apb-browse-refinements-indent-2" in inner_li.get_attribute("class") or "s-navigation-indent-2" in inner_li.get_attribute("class"):
                        itemRef = Atags[0].get_attribute("innerText")
                        clicked_tag = itemRef
                        print("Now navigating to "+Atags[0].get_attribute("innerText"))
                        amzn["item_type"] = itemRef
                        driver.execute_script("arguments[0].click();", Atags[0])
                        departmentSubCategoriesXtraOptions(driver, clicked_tag)
            except StaleElementReferenceException:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
                    print("error has occured page, refreshing page")
                    driver.refresh()
                except TimeoutException:
                    print("Page displaying correctly, proceeding.....")
                outer_div = driver.find_element(By.ID, "s-refinements")
                innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
                inner_ul = innerDiv[0].find_elements(By.TAG_NAME, "ul")

                if len(inner_ul) > 0:
                    inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
                else:
                    dept = driver.find_element(By.ID, "departments")
                    inner_ul = dept.find_elements(By.TAG_NAME, "ul")
                    inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")

                if inner_lis[count].get_attribute("class") is not None:
                    if len(inner_lis) > count:
                        Atags = inner_lis[count].find_elements(By.TAG_NAME, "a")
                        if len(Atags) > 0:
                            if "apb-browse-refinements-indent-2" in inner_lis[count].get_attribute("class") or "s-navigation-indent-2" in inner_lis[count].get_attribute("class"):
                                itemRef = Atags[0].get_attribute("innerText")
                                clicked_tag = itemRef
                                print("Now navigating to "+Atags[0].get_attribute("innerText"))
                                amzn["item_type"] = itemRef
                                driver.execute_script("arguments[0].click();", Atags[0])
                                departmentSubCategoriesXtraOptions(driver, clicked_tag)
            if len(inner_lis) == count +1:
                navigateBackOnRefinements(driver, item)
                break
            count+=1
    else:
        getItemDetails(driver)
        #navigateBackOnRefinements(driver, item)
        #navigateBackOnCategories(driver, item)

def departmentSubCategoriesXtraOptions(driver,item):
    print("SubCat Xtra Options welcome "+item)
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
        print("error has occured page departmentSubCategoriesXtraOptions, refreshing page")
        driver.refresh()
    except TimeoutException:
        print("Page on departmentSubCategoriesXtraOptions displaying correctly, proceeding.....")

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID,"s-refinements")))
    outer_div = driver.find_element(By.ID, "s-refinements")
    innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
    inner_ul = innerDiv[0].find_elements(By.TAG_NAME, "ul")
    if len(inner_ul) > 0:
        inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
    else:
        dept = driver.find_element(By.ID, "departments")
        inner_ul = dept.find_elements(By.TAG_NAME, "ul")
        inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")

    count = 0
    countInnerLinks = 0
    hasInnerLinks = False
    clicked_tag = ""

    for inner_li in inner_lis:
        if "apb-browse-refinements-indent-2" in inner_li.get_attribute("class") or "s-navigation-indent-2" in inner_li.get_attribute("class"):
            countInnerLinks+=1
        
        if countInnerLinks > 1:
            hasInnerLinks = True
            break


    if hasInnerLinks:
        for inner_li in inner_lis:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
                print("error has occured page departmentSubCategoriesXtraOptions, refreshing page")
                driver.refresh()
            except TimeoutException:
                print("Page on departmentSubCategoriesXtraOptions displaying correctly, proceeding.....")
            try:
                if inner_li.get_attribute("class") is not None:
                    try:
                        Atags = inner_li.find_elements(By.TAG_NAME, "a")
                        print(inner_li.get_attribute("innerText"))
                    except StaleElementReferenceException:
                        #input("Press Enter to continue...")
                        Atags = inner_lis[count].find_elements(By.TAG_NAME, "a")
                        print(inner_li[count].get_attribute("innerText"))
                if len(Atags) > 0:
                    if "apb-browse-refinements-indent-2" in inner_li.get_attribute("class") or "s-navigation-indent-2" in inner_li.get_attribute("class"):
                        itemRef = Atags[0].get_attribute("innerText")
                        clicked_tag = itemRef
                        print("Now navigating to "+Atags[0].get_attribute("innerText"))
                        amzn["item_type"] = itemRef
                        driver.execute_script("arguments[0].click();", Atags[0])
                        departmentSubCategoriesXtraXtraOptions(driver,clicked_tag)
            except StaleElementReferenceException:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
                    print("error has occured page, refreshing page")
                    driver.refresh()
                except TimeoutException:
                    print("Page displaying correctly, proceeding.....")
                outer_div = driver.find_element(By.ID, "s-refinements")
                innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
                inner_ul = innerDiv[0].find_elements(By.TAG_NAME, "ul")

                if len(inner_ul) > 0:
                    inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
                else:
                    dept = driver.find_element(By.ID, "departments")
                    inner_ul = dept.find_elements(By.TAG_NAME, "ul")
                    inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")

                if inner_lis[count].get_attribute("class") is not None:
                    if len(inner_lis) > count:
                        Atags = inner_lis[count].find_elements(By.TAG_NAME, "a")
                        if len(Atags) > 0:
                            if "apb-browse-refinements-indent-2" in inner_lis[count].get_attribute("class") or "s-navigation-indent-2" in inner_lis[count].get_attribute("class"):
                                itemRef = Atags[0].get_attribute("innerText")
                                clicked_tag = itemRef
                                print("Now navigating to "+Atags[0].get_attribute("innerText"))
                                amzn["item_type"] = itemRef
                                driver.execute_script("arguments[0].click();", Atags[0])
                                departmentSubCategoriesXtraXtraOptions(driver,itemRef)

            if len(inner_lis) == count +1:
                navigateBackOnRefinements(driver, item)
                break
            count+=1
    else:
        getItemDetails(driver)
    
def departmentSubCategoriesXtraXtraOptions(driver,item):
    print("SubCat Xtra Xtra Options welcome "+item)
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
        print("error has occured page departmentSubCategoriesXtraXtraOptions, refreshing page")
        driver.refresh()
    except TimeoutException:
        print("Page on departmentSubCategoriesXtraXtraOptions displaying correctly, proceeding.....")
    time.sleep(5)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID,"s-refinements")))
    outer_div = driver.find_element(By.ID, "s-refinements")
    innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
    inner_ul = innerDiv[0].find_element(By.TAG_NAME, "ul")
    inner_lis = inner_ul.find_elements(By.TAG_NAME, "li")
    count = 0
    countInnerLinks = 0
    hasInnerLinks = False

    for inner_li in inner_lis:
        if "apb-browse-refinements-indent-2" in inner_li.get_attribute("class"):
            countInnerLinks+=1
        
        if countInnerLinks > 1:
            hasInnerLinks = True
            break

    if hasInnerLinks:
        for inner_li in inner_lis:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
                print("error has occured page departmentSubCategoriesXtraXtraOptions, refreshing page")
                driver.refresh()
            except TimeoutException:
                print("Page on departmentSubCategoriesXtraXtraOptions displaying correctly, proceeding.....")
            try:
                Atags = inner_li.find_elements(By.TAG_NAME, "a")
                if len(Atags) > 0:
                    if "apb-browse-refinements-indent-2" in inner_li.get_attribute("class"):
                        itemRef = Atags[0].get_attribute("innerText")
                        clicked_tag = itemRef
                        print("Now navigating to "+Atags[0].get_attribute("innerText"))
                        amzn["item_type"] = itemRef
                        driver.execute_script("arguments[0].click();", Atags[0])
                        departmentSubCategoriesXtraXtraFinalOptions(driver, itemRef)
            except StaleElementReferenceException:
                outer_div = driver.find_element(By.ID, "s-refinements")
                innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
                inner_ul = innerDiv[0].find_element(By.TAG_NAME, "ul")
                inner_lis = inner_ul.find_elements(By.TAG_NAME, "li")
                Atags = inner_lis[count].find_elements(By.TAG_NAME, "a")
                if len(Atags) > 0:
                    if "apb-browse-refinements-indent-2" in inner_lis[count].get_attribute("class"):
                        itemRef = Atags[0].get_attribute("innerText")
                        clicked_tag = itemRef
                        print("Now navigating to "+Atags[0].get_attribute("innerText"))
                        amzn["item_type"] = itemRef
                        driver.execute_script("arguments[0].click();", Atags[0])
                        departmentSubCategoriesXtraXtraFinalOptions(driver, itemRef)

            if len(inner_lis) == count +1:
                navigateBackOnRefinements(driver, item)
                break
            count+=1
    else:
        getItemDetails(driver)

def departmentSubCategoriesXtraXtraFinalOptions(driver,item):
    print("SubCat Xtra Xtra Final Options welcome "+item)
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
        print("error has occured page departmentSubCategoriesXtraXtraFinalOptions, refreshing page")
        driver.refresh()
    except TimeoutException:
        print("Page on departmentSubCategoriesXtraXtraFinalOptions displaying correctly, proceeding.....")
    time.sleep(5)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID,"s-refinements")))
    outer_div = driver.find_element(By.ID, "s-refinements")
    innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
    inner_ul = innerDiv[0].find_element(By.TAG_NAME, "ul")
    inner_lis = inner_ul.find_elements(By.TAG_NAME, "li")
    count = 0
    clicked_tag = ""
    countInnerLinks = 0
    hasInnerLinks = False

    for inner_li in inner_lis:
        if "apb-browse-refinements-indent-2" in inner_li.get_attribute("class"):
            countInnerLinks+=1
        
        if countInnerLinks > 1:
            hasInnerLinks = True
            break

    if hasInnerLinks:
        for inner_li in inner_lis:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
                print("error has occured page departmentSubCategoriesXtraXtraFinalOptions, refreshing page")
                driver.refresh()
            except TimeoutException:
                print("Page on departmentSubCategoriesXtraXtraFinalOptions displaying correctly, proceeding.....")
            try:
                Atags = inner_li.find_elements(By.TAG_NAME, "a")
                if len(Atags) > 0:
                    if "apb-browse-refinements-indent-2" in inner_li.get_attribute("class"):
                        itemRef = Atags[0].get_attribute("innerText")
                        clicked_tag = itemRef
                        print("Now navigating to "+Atags[0].get_attribute("innerText"))
                        amzn["item_type"] = itemRef
                        driver.execute_script("arguments[0].click();", Atags[0])
                        departmentSubCategoriesXtraOptions(driver, itemRef)
            except StaleElementReferenceException:
                outer_div = driver.find_element(By.ID, "s-refinements")
                innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
                inner_ul = innerDiv[0].find_element(By.TAG_NAME, "ul")
                inner_lis = inner_ul.find_elements(By.TAG_NAME, "li")
                Atags = inner_lis[count].find_elements(By.TAG_NAME, "a")
                if len(Atags) > 0:
                    if "apb-browse-refinements-indent-2" in inner_lis[count].get_attribute("class"):
                        itemRef = Atags[0].get_attribute("innerText")
                        clicked_tag = itemRef
                        print("Now navigating to "+Atags[0].get_attribute("innerText"))
                        amzn["item_type"] = itemRef
                        driver.execute_script("arguments[0].click();", Atags[0])
                        departmentSubCategoriesXtraOptions(driver, itemRef)

            if len(inner_lis) == count +1:
                navigateBackOnRefinements(driver, item)
            count+=1
    else:
        getItemDetails(driver)

def navigateBackOnCategories(driver, item):
    print("Welcome "+item)
    scrollToTop(driver)
    time.sleep(5)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID,"departments")))
    outer_div = driver.find_element(By.ID, "departments")
    #innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
    inner_ul = outer_div.find_elements(By.TAG_NAME, "ul")
    inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")

    count = 0
    id = ""
    for inner_li in inner_lis:

        if len(inner_lis) == (count+1) :
            atag = inner_lis[count-1].find_elements(By.TAG_NAME, "a")
            driver.execute_script("arguments[0].click();", atag[0])
        #id = inner_lis[count].get_attribute("id")
        count+=1
    # WebDriverWait(driver, 5).until(
    #     EC.presence_of_element_located((By.ID,"s-refinements")))
    # outer_div = driver.find_element(By.ID, "s-refinements")
    # innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
    # inner_ul = innerDiv[1].find_element(By.TAG_NAME, "ul")
    # inner_lis = inner_ul[1].find_elements(By.TAG_NAME, "li")
    # count = 0

    # for inner_li in inner_lis:
    #     try:
    #         Atags = inner_li.find_elements(By.TAG_NAME, "a")
    #         if len(Atags) > 0:
    #             if item == Atags[0].get_attribute("innerText"):
    #                 previousAtag = inner_lis[count-1].find_elements(By.TAG_NAME, "a")
    #                 driver.execute_script("arguments[0].click();", previousAtag)
    #                 #Nav back
    #     except StaleElementReferenceException:
    #         Atags = inner_lis[count].find_elements(By.TAG_NAME, "a")
    #         if len(Atags) > 0:
    #             if item == Atags[0].get_attribute("innerText"):
    #                 previousAtag = inner_lis[count-1].find_elements(By.TAG_NAME, "a")
    #                 driver.execute_script("arguments[0].click();", previousAtag)

    #     count+=1
#def getWorkingSideMenu():

def navigateBackOnRefinements(driver, item):
    print("Going back from "+item)
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Click here to visit the Amazon.co.za home page")))
        print("error has occured page navigateBackOnRefinements, refreshing page")
        driver.refresh()
    except TimeoutException:
        print("Page on navigateBackOnRefinements displaying correctly, proceeding.....")
    scrollToTop(driver)
    time.sleep(5)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID,"s-refinements")))
    outer_div = driver.find_element(By.ID, "s-refinements")
    #innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
    inner_ul = outer_div.find_elements(By.TAG_NAME, "ul")
    if len(inner_ul) > 0:
        inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
        dept = driver.find_elements(By.ID, "departments")
        if len(dept) > 0:
            inner_ul = dept[0].find_elements(By.TAG_NAME, "ul")
            inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
    else:
        dept = driver.find_element(By.ID, "departments")
        inner_ul = dept.find_elements(By.TAG_NAME, "ul")
        inner_lis = inner_ul[0].find_elements(By.TAG_NAME, "li")
    
    #inner_ul = driver.find_element(By.ID, "filter-n")
    #inner_lis = inner_ul.find_elements(By.TAG_NAME, "li")
    count = 0
    id = ""
    for inner_li in inner_lis:
        if "s-navigation-indent-2" in inner_li.get_attribute("class"):
            atag = inner_lis[count-2].find_elements(By.TAG_NAME, "a")
            driver.execute_script("arguments[0].click();", atag[0])
            break
            inner_li.get_attribute("innerText")
            #inner_lis[count-2].get_attribute("innerText")
        #id = inner_lis[count].get_attribute("id")
        count+=1
    # WebDriverWait(driver, 5).until(
    #     EC.presence_of_element_located((By.ID,"s-refinements")))
    # outer_div = driver.find_element(By.ID, "s-refinements")
    # innerDiv = outer_div.find_elements(By.TAG_NAME, "div")
    # inner_ul = innerDiv[1].find_element(By.TAG_NAME, "ul")
    # inner_lis = inner_ul[1].find_elements(By.TAG_NAME, "li")
    # count = 0

    # for inner_li in inner_lis:
    #     try:
    #         Atags = inner_li.find_elements(By.TAG_NAME, "a")
    #         if len(Atags) > 0:
    #             if item == Atags[0].get_attribute("innerText"):
    #                 previousAtag = inner_lis[count-1].find_elements(By.TAG_NAME, "a")
    #                 driver.execute_script("arguments[0].click();", previousAtag)
    #                 #Nav back
    #     except StaleElementReferenceException:
    #         Atags = inner_lis[count].find_elements(By.TAG_NAME, "a")
    #         if len(Atags) > 0:
    #             if item == Atags[0].get_attribute("innerText"):
    #                 previousAtag = inner_lis[count-1].find_elements(By.TAG_NAME, "a")
    #                 driver.execute_script("arguments[0].click();", previousAtag)

    #     count+=1
#def getWorkingSideMenu():

def navigateToMainCategories(driver, item):
    #click hambeger home menu
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID,"nav-hamburger-menu")))
    menu = driver.find_element(By.ID,"nav-hamburger-menu")
    time.sleep(5)
    menu.click()
    time.sleep(5)

    #expand list
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.LINK_TEXT, "See all")))
    link = driver.find_element(By.LINK_TEXT, "See all")
    link.click()
    time.sleep(5)

    WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.LINK_TEXT,item)))
    
    option = driver.find_element(By.LINK_TEXT, item)
    driver.execute_script("arguments[0].click();", option)


#main site
amazon = "https://www.amazon.co.za"
#Navigate to site

#chromedriver_autoinstaller.install()

options = webdriver.ChromeOptions()
#options.add_argument('--headless=new')  # Run Chrome in headless mode
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1200,842')
options.add_argument('--enable-automation')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-extensions")
options.add_argument('--remote-allow-origins=*')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument("--profile-directory=Default")
options.add_argument('--ignore-certificate-errors')
options.add_argument("--disable-geolocation")
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36")
options.add_argument("--start-maximized")
# Create a unique temporary directory for user data
user_data_dir = tempfile.mkdtemp()
options.add_argument("--user-data-dir={}".format(user_data_dir))

if True:
    driver_path = "chromedriver.exe"
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

if False:
    # Create a unique temporary directory for user data
    user_data_dir = tempfile.mkdtemp()
    #options.add_argument("--user-data-dir={}".format(user_data_dir))
    #options.add_argument(f"--user-data-dir={user_data_dir}")

    chrome_driver_path = ChromeDriverManager().install()
    print("\n")
    print("ChromeDriver path:{}".format(chrome_driver_path))
    print("\n In V2")

    # Ensure the path is correct and the file exists
    assert os.path.exists(chrome_driver_path), "ChromeDriver not found!"
    print("\n")
    # Install and set up ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    # Set up the remote WebDriver to connect to the Selenium Grid
    #driver = webdriver.Remote(
    #    command_executor='http://3.148.145.181:4444/wd/hub',
    #    options=options
        #desired_capabilities=DesiredCapabilities.CHROME
    #)
    #driver = webdriver.Chrome(ChromeDriverManager().install())
    #driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=options)

#driver = webdriver.Chrome()
#driver_path = "C:\\xampp\\htdocs\\price tracer\\chromedriver.exe"
#service = Service(driver_path)
#driver = webdriver.Chrome(service=service)
driver.maximize_window()

driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
    "latitude": -30.5595,
    "longitude": 22.9375,
    "accuracy": 100
})

# Open site
driver.get(amazon)
# Check if the browser is launched
if driver:
    print("Browser is launched")
    # Optionally, check if the title or URL is accessible
    print("Title:", driver.title)
    print("Current URL:", driver.current_url)
    # Take a screenshot
    screenshot_path = "../screenshot1.png"   
else:
    print("Browser is not launched")

time.sleep(100)

try:
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located(By.ID,"nav-hamburger-menu"))
    
except:
    print("Title:", driver.title)
    screenshot_path = "../screenshot2.png"
    driver.save_screenshot(screenshot_path)
    #print(f"Screenshot saved to {screenshot_path}")

#click hambeger home menu
WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.ID,"nav-hamburger-menu")))
menu = driver.find_element(By.ID,"nav-hamburger-menu")
time.sleep(5)
menu.click()
time.sleep(5)

#expand list
WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.LINK_TEXT, "See all")))
link = driver.find_element(By.LINK_TEXT, "See all")
link.click()
time.sleep(5)

# read categories
with open('categories.txt', 'r') as file:
    for line in file:
        split_categories = line.strip().split("|")
        #Loop through the departments and get all the data 
        for category in split_categories:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID,"hmenu-content")))
            div = driver.find_element(By.ID, "hmenu-content")
            ul = div.find_elements(By.TAG_NAME, "ul")
            lis = ul[0].find_elements(By.TAG_NAME, "li")
            count_menu_items = 0
            for li in lis:
                try:
                    if category.lower() in li.text.lower():
                        main_option = li.get_attribute("innerText")
                        li.click()
                        driver.execute_script("arguments[0].click();", li)
                        amzn["item_category"] = main_option
                        submenuItems(driver, main_option)
                        break
                except StaleElementReferenceException:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID,"nav-hamburger-menu")))
                    menu = driver.find_element(By.ID,"nav-hamburger-menu")
                    time.sleep(5)
                    menu.click()
                    time.sleep(5)
                    div = driver.find_element(By.ID, "hmenu-content")
                    ul = div.find_elements(By.TAG_NAME, "ul")
                    lis = ul[0].find_elements(By.TAG_NAME, "li")
                    if category.lower() in lis[count_menu_items].text.lower():
                        main_option = lis[count_menu_items].get_attribute("innerText")
                        driver.execute_script("arguments[0].click();", lis[count_menu_items])
                        print("Element is stale and not found in side menu shopping list.")
                        amzn["item_category"] = main_option
                        submenuItems(driver, main_option)
                        break

                count_menu_items+=1
