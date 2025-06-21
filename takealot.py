import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from requests.exceptions import ReadTimeout
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
import chromedriver_autoinstaller
import os
import tempfile
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from selenium.webdriver.chrome.options import Options
import dbconnection

takealot = {
    "item_category": "",
    "item_subcategory": "",
    "item_type": "",
    "categories_site":""
}

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

def getCategories(driver):
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'list-menu')))
        ul = driver.find_element(By.CLASS_NAME, "list-menu")
        lis = ul.find_elements(By.TAG_NAME, "li")
        cat_count = 0
        takealot["categories_site"] = driver.current_url
        
        for li in lis:
            len(lis)
            #Default count = 0
            if cat_count > 0:
                try:
                    try:
                        li.click()
                    except ElementClickInterceptedException:
                        driver.execute_script("arguments[0].click();", li)
                    time.sleep(5)
                    getSeeMoreButton(driver)
                    time.sleep(5)
                    getExpandedCategoriesMenuByIndex(driver)
                except StaleElementReferenceException:
                    newli = getLiOnIndex(driver, 'list-menu', cat_count, locator="class")
                    try:
                        newli.click()
                    except ElementClickInterceptedException:
                        driver.execute_script("arguments[0].click();", newli)
                    time.sleep(5)
                    getSeeMoreButton(driver)
                    time.sleep(5)
                    getExpandedCategoriesMenuByIndex(driver)
            cat_count+=1

    except TimeoutException:
        getSubMenuCategories(driver, False)

def getLiOnIndex(driver, locatorName, index, locator="class"):
    if locator == "class":
        WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, locatorName)))
        ul = driver.find_element(By.CLASS_NAME, locatorName)
        lis = ul.find_elements(By.TAG_NAME, "li")
    return lis[index]

def getSeeMoreButton(driver):
    try:
        #WebDriverWait(driver, 200).until(
        #    EC.presence_of_element_located((By.CLASS_NAME, 'category-widget-module_show-more_2HZyM')))
        WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'category-widget-module_title_2--iz')))
        print("Side menu list is perfectly aligned.")
    except TimeoutException:
        #driver.refresh()
        time.sleep(20)
        print("Side menu is not yet aligned, waiting for page to fully load.")

    try:
        if elementExists(driver.find_elements(By.CLASS_NAME, "category-widget-module_show-more_2HZyM")):
            print("See More Element Exists")
            seeMore = driver.find_element(By.CLASS_NAME, "category-widget-module_show-more_2HZyM")
            seeMoreText = seeMore.get_attribute("innerText")
            driver.execute_script("arguments[0].scrollIntoView();", seeMore)
            while seeMoreText == "See More":   
                try:
                    seeMore.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", seeMore)
                WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "category-widget-module_show-more_2HZyM")))
                seeMore = driver.find_element(By.CLASS_NAME, "category-widget-module_show-more_2HZyM")
                driver.execute_script("arguments[0].scrollIntoView();", seeMore)
                if seeMore is not seeMoreText:
                    break

    except NoSuchElementException:
        print("See More element doesn't exists.")
        
def getExpandedCategoriesMenuByIndex (driver):
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'transition-horizontal-module_slide_3FOk5')))
    except TimeoutException:
        input("Press Enter to continue...1")
    getSeeMoreButton(driver)
    container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
    aTags = container.find_elements(By.TAG_NAME, "a")
    expanded_count = 0
    defaultCount = 0
    indexCounter = 0
    for aTag in aTags:
        if aTag.get_attribute("aria-current") is not None:
            defaultCount = indexCounter
            break
        indexCounter+=1
    #defaultCount = 2
    #Defaul defaultCount = 2
    for aTag in aTags:
        #if defaultCount > 1:
        if expanded_count > defaultCount or (len(aTags)-1) == expanded_count:
            print("Menu num >>>>>>>>>>>>>>>>>>  "+str(expanded_count+1))
            try:
                time.sleep(5)
                getSeeMoreButton(driver)
                
                #driver.refresh()
                if "accessories" not in aTag.get_attribute("innerText").lower():
                    takealot["item_subcategory"] = aTag.get_attribute("innerText")
                    driver.execute_script("arguments[0].click();", aTag)
                    #aTag.click()

                    time.sleep(5)
                    getSubMenuCategories(driver, True)
                    getSeeMoreButton(driver)
            except StaleElementReferenceException:
                #driver.refresh()
                time.sleep(5)
                getSeeMoreButton(driver)
                container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                aTags = container.find_elements(By.TAG_NAME, "a")
                if "accessories" not in aTags[expanded_count-1].get_attribute("innerText").lower():
                    takealot["item_subcategory"] = aTags[expanded_count-1].get_attribute("innerText")
                    #aTags[count].click()
                    driver.execute_script("arguments[0].click();", aTags[expanded_count])
                    time.sleep(5)
                    getSubMenuCategories(driver, True)
                    getSeeMoreButton(driver)

        if expanded_count == len(aTags)-1:
            container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
            aTags = container.find_elements(By.TAG_NAME, "a")
            if elementExists(driver.find_elements(By.CLASS_NAME,"swiper-slide")):
                #print("Now exiting the ["+aTags[defaultCount].get_attribute("innerText")+"] scenario")
                #driver.execute_script("arguments[0].click();", aTags[defaultCount-1])
                #topNav =  driver.find_element(By.CLASS_NAME,"swiper-slide")
                #topNav.click()
                print("Now exiting the ["+aTags[defaultCount].get_attribute("innerText")+"] scenario")
                driver.get(takealot["categories_site"])
                time.sleep(5)
            else:
                print("Now exiting the ["+aTags[defaultCount].get_attribute("innerText")+"] scenario")
                #driver.execute_script("arguments[0].click();", aTags[count-1])
                driver.get(takealot["categories_site"])
                time.sleep(5)
            #aTags[1].click()
            #driver.back()
            defaultCount = 0
        expanded_count+=1

def getSubMenuCategories(driver, straight_to_refined_categories):
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'transition-horizontal-module_slide_3FOk5')))
    except TimeoutException:
        input("Press Enter to continue...2")
    getSeeMoreButton(driver)
    container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
    aTags = container.find_elements(By.TAG_NAME, "a")
    sub_count = 0
    defaultCount = 0
    indexCounter = 0
    for aTag in aTags:
        if aTag.get_attribute("aria-current") is not None:
            defaultCount = indexCounter
            break
        indexCounter+=1

    #defaultCount = 2
    for aTag in aTags:
        #if sub_count > 5:
        if sub_count > defaultCount or (len(aTags)-1) == sub_count:
            print("Sub menu num >>>>>>>>>>>>>>>>>>  "+str(sub_count+1))
            try:
                container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                aTags = container.find_elements(By.TAG_NAME, "a")
                time.sleep(5)
                getSeeMoreButton(driver)
                print("Now starting the ["+aTag.get_attribute("innerText")+"] scenario")
                takealot["item_type"] = aTag.get_attribute("innerText")
                #driver.execute_script("arguments[0].click();", aTag)
                #Cater for inner submenu items
                #if len(aTags) - defaultCount > 1:
                if len(aTags) - defaultCount > 1:
                    container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                    aTags = container.find_elements(By.TAG_NAME, "a")
                    driver.execute_script("arguments[0].click();", aTags[sub_count])
                    time.sleep(5)
                    #Check if more options are available
                    getSeeMoreButton(driver)
                    inner_container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                    inner_aTags = inner_container.find_elements(By.TAG_NAME, "a")
                    inner_indexCounter = 0
                    for inner_Tag in inner_aTags:
                        if inner_Tag.get_attribute("aria-current") is not None:
                                break
                        inner_indexCounter +=1
                    #if len(inner_aTags) ==  inner_indexCounter+1:
                    if len(inner_aTags) ==  inner_indexCounter+2:
                        getItems(driver)
                        time.sleep(5)
                        inner_sub_container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                        inner_sub_aTags = inner_sub_container.find_elements(By.TAG_NAME, "a")
                        driver.execute_script("arguments[0].click();", inner_sub_aTags[defaultCount])
                    else:
                        getSubMenuCategoriesOptions(driver)
                    # aTagCounter = 0
                    # for aTag in aTags:
                    #     if aTagCounter > defaultCount:
                    #         try:
                    #             if "accessories" not in aTag.get_attribute("innerText").lower():
                    #                 getSeeMoreButton(driver)
                    #                 container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                    #                 aTags = container.find_elements(By.TAG_NAME, "a")
                    #                 driver.execute_script("arguments[0].click();", aTags[aTagCounter])
                    #                 time.sleep(5)
                    #                 getItems(driver)
                    #                 time.sleep(5)
                    #                 inner_sub_container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                    #                 inner_sub_aTags = inner_sub_container.find_elements(By.TAG_NAME, "a")
                    #                 driver.execute_script("arguments[0].click();", inner_sub_aTags[defaultCount])

                    #         except StaleElementReferenceException:
                    #             container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                    #             aTags = container.find_elements(By.TAG_NAME, "a")
                    #             if "accessories" not in aTags[aTagCounter].get_attribute("innerText").lower():
                    #                 getSeeMoreButton(driver)
                    #                 container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                    #                 aTags = container.find_elements(By.TAG_NAME, "a")
                    #                 driver.execute_script("arguments[0].click();", aTags[aTagCounter])
                    #                 time.sleep(5)
                    #                 getItems(driver)
                    #                 time.sleep(5)
                    #                 inner_sub_container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                    #                 inner_sub_aTags = inner_sub_container.find_elements(By.TAG_NAME, "a")
                    #                 driver.execute_script("arguments[0].click();", inner_sub_aTags[defaultCount])
                    #                 time.sleep(5)
                    #     aTagCounter +=1
                    #     print("Exiting for loop")
                else:
                    #aTag.click()
                    time.sleep(5)
                    getItems(driver)
            except StaleElementReferenceException:
                time.sleep(5)
                getSeeMoreButton(driver)
                container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                aTags = container.find_elements(By.TAG_NAME, "a")
                print("Now starting the ["+aTags[defaultCount].get_attribute("innerText")+"] scenario")
                takealot["item_type"] = aTags[sub_count].get_attribute("innerText")
                #aTags[count].click()
                #driver.execute_script("arguments[0].click();", aTags[count])
                if len(aTags) - defaultCount > 1:
                    container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                    aTags = container.find_elements(By.TAG_NAME, "a")
                    driver.execute_script("arguments[0].click();", aTags[sub_count])
                    time.sleep(5)


                    #Check if more options are available
                    getSeeMoreButton(driver)
                    inner_container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                    inner_aTags = inner_container.find_elements(By.TAG_NAME, "a")
                    inner_indexCounter = 0
                    for inner_Tag in inner_aTags:
                        if inner_Tag.get_attribute("aria-current") is not None:
                                break
                        inner_indexCounter +=1
                    
                    if len(inner_aTags) ==  inner_indexCounter+1:
                        getItems(driver)
                        time.sleep(5)
                        inner_sub_container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                        inner_sub_aTags = inner_sub_container.find_elements(By.TAG_NAME, "a")
                        driver.execute_script("arguments[0].click();", inner_sub_aTags[defaultCount])
                    else:
                        getSubMenuCategoriesOptions(driver)

                else:
                    time.sleep(5)
                    getItems(driver)


        if sub_count == len(aTags)-1:
            container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
            aTags = container.find_elements(By.TAG_NAME, "a")
            if len(aTags) == 2:
                aTags[1].click()
            else:
                print("Now exiting the ["+aTags[defaultCount].get_attribute("innerText")+"] scenario")
                driver.execute_script("arguments[0].click();", aTags[defaultCount-1])
                #aTags[defaultCount-1].click()
                
                #driver.execute_script("arguments[0].click();", aTags[3])

        sub_count+=1

def getSubMenuCategoriesOptions(driver):

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'transition-horizontal-module_slide_3FOk5')))
    except TimeoutException:
        input("Press Enter to continue...3")
    getSeeMoreButton(driver)
    container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
    aTags = container.find_elements(By.TAG_NAME, "a")
    sub_count = 0
    defaultCount = 0
    indexCounter = 0
    for aTag in aTags:
        if aTag.get_attribute("aria-current") is not None:
            defaultCount = indexCounter
            break
        indexCounter+=1

    if len(aTags) > defaultCount+1:
        #defaultCount = 2
        for aTag in aTags:
            if sub_count > defaultCount or (len(aTags)-1) == sub_count:
                print("Sub menu num >>>>>>>>>>>>>>>>>>  "+str(sub_count+1))
                try:
                    container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                    aTags = container.find_elements(By.TAG_NAME, "a")
                    time.sleep(5)
                    getSeeMoreButton(driver)
                    print("Now starting the ["+aTag.get_attribute("innerText")+"] scenario")
                    takealot["item_type"] = aTag.get_attribute("innerText")
                    if len(aTags) - defaultCount > 1:
                        container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                        aTags = container.find_elements(By.TAG_NAME, "a")
                        driver.execute_script("arguments[0].click();", aTags[sub_count])
                        time.sleep(5)
                        #Check if more options are available
                        getSeeMoreButton(driver)
                        inner_container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                        inner_aTags = inner_container.find_elements(By.TAG_NAME, "a")
                        inner_indexCounter = 0
                        for inner_Tag in inner_aTags:
                            if inner_Tag.get_attribute("aria-current") is not None:
                                    break
                            inner_indexCounter +=1
                        
                        if len(inner_aTags) ==  inner_indexCounter+ 1:
                            getItems(driver)
                            time.sleep(5)
                            inner_sub_container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                            inner_sub_aTags = inner_sub_container.find_elements(By.TAG_NAME, "a")
                            driver.execute_script("arguments[0].click();", inner_sub_aTags[defaultCount])
                        else:
                            getSubMenuCategoriesXTraOptions(driver)

                    else:
                        time.sleep(5)
                        getItems(driver)
                except StaleElementReferenceException:
                    time.sleep(5)
                    getSeeMoreButton(driver)
                    container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                    aTags = container.find_elements(By.TAG_NAME, "a")
                    print("Now starting the ["+aTags[defaultCount].get_attribute("innerText")+"] scenario")
                    takealot["item_type"] = aTags[sub_count].get_attribute("innerText")
                    if len(aTags) - defaultCount > 1:
                        container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                        aTags = container.find_elements(By.TAG_NAME, "a")
                        driver.execute_script("arguments[0].click();", aTags[sub_count])
                        time.sleep(5)

                        #Check if more options are available
                        getSeeMoreButton(driver)
                        inner_container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                        inner_aTags = inner_container.find_elements(By.TAG_NAME, "a")
                        inner_indexCounter = 0
                        for inner_Tag in inner_aTags:
                            if inner_Tag.get_attribute("aria-current") is not None:
                                    break
                            inner_indexCounter +=1
                        
                        if len(inner_aTags) ==  inner_indexCounter+1:
                            getItems(driver)
                            time.sleep(5)
                            inner_sub_container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                            inner_sub_aTags = inner_sub_container.find_elements(By.TAG_NAME, "a")
                            driver.execute_script("arguments[0].click();", inner_sub_aTags[defaultCount])
                        else:
                            getSubMenuCategoriesXTraOptions(driver)

                    else:
                        time.sleep(5)
                        getItems(driver)


            if sub_count == len(aTags)-1:
                container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                aTags = container.find_elements(By.TAG_NAME, "a")
                if len(aTags) == 2:
                    aTags[1].click()
                else:
                    print("Now exiting the ["+aTags[defaultCount].get_attribute("innerText")+"] scenario")
                    driver.execute_script("arguments[0].click();", aTags[defaultCount-1])

            sub_count+=1
    else:
        time.sleep(5)
        getItems(driver)

def getSubMenuCategoriesXTraOptions(driver):
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'transition-horizontal-module_slide_3FOk5')))
    except TimeoutException:
        input("Press Enter to continue...4")
    getSeeMoreButton(driver)
    container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
    aTags = container.find_elements(By.TAG_NAME, "a")
    sub_count = 0
    defaultCount = 0
    indexCounter = 0
    for aTag in aTags:
        if aTag.get_attribute("aria-current") is not None:
            defaultCount = indexCounter
            break
        indexCounter+=1

    if len(aTags) > defaultCount+1:
        #defaultCount = 2
        for aTag in aTags:
            #if sub_count > 2:
            if sub_count > defaultCount or (len(aTags)-1) == sub_count:
                print("Sub menu num >>>>>>>>>>>>>>>>>>  "+str(sub_count+1))
                try:
                    container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                    aTags = container.find_elements(By.TAG_NAME, "a")
                    time.sleep(5)
                    getSeeMoreButton(driver)
                    print("Now starting the ["+aTag.get_attribute("innerText")+"] scenario")
                    takealot["item_type"] = aTag.get_attribute("innerText")
                    if len(aTags) - defaultCount > 1:
                        container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                        aTags = container.find_elements(By.TAG_NAME, "a")
                        driver.execute_script("arguments[0].click();", aTags[sub_count])
                        time.sleep(5)
                        #Check if more options are available
                        getSeeMoreButton(driver)
                        inner_container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                        inner_aTags = inner_container.find_elements(By.TAG_NAME, "a")
                        inner_indexCounter = 0
                        for inner_Tag in inner_aTags:
                            if inner_Tag.get_attribute("aria-current") is not None:
                                    break
                            inner_indexCounter +=1
                        
                        if len(inner_aTags) ==  inner_indexCounter+ 1:
                            getItems(driver)
                            time.sleep(5)
                            inner_sub_container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                            inner_sub_aTags = inner_sub_container.find_elements(By.TAG_NAME, "a")
                            driver.execute_script("arguments[0].click();", inner_sub_aTags[defaultCount])
                        else:
                            getSubMenuCategoriesXTraXTraOptions(driver)

                    else:
                        time.sleep(5)
                        getItems(driver)
                except StaleElementReferenceException:
                    time.sleep(5)
                    getSeeMoreButton(driver)
                    container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                    aTags = container.find_elements(By.TAG_NAME, "a")
                    print("Now starting the ["+aTags[defaultCount].get_attribute("innerText")+"] scenario")
                    takealot["item_type"] = aTags[sub_count].get_attribute("innerText")
                    if len(aTags) - defaultCount > 1:
                        container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                        aTags = container.find_elements(By.TAG_NAME, "a")
                        driver.execute_script("arguments[0].click();", aTags[sub_count])
                        time.sleep(5)

                        #Check if more options are available
                        getSeeMoreButton(driver)
                        inner_container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                        inner_aTags = inner_container.find_elements(By.TAG_NAME, "a")
                        inner_indexCounter = 0
                        for inner_Tag in inner_aTags:
                            if inner_Tag.get_attribute("aria-current") is not None:
                                    break
                            inner_indexCounter +=1
                        
                        if len(inner_aTags) ==  inner_indexCounter+1:
                            getItems(driver)
                            time.sleep(5)
                            inner_sub_container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                            inner_sub_aTags = inner_sub_container.find_elements(By.TAG_NAME, "a")
                            driver.execute_script("arguments[0].click();", inner_sub_aTags[defaultCount])
                        else:
                            getSubMenuCategoriesXTraXTraOptions(driver)

                    else:
                        time.sleep(5)
                        getItems(driver)


            if sub_count == len(aTags)-1:
                container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
                aTags = container.find_elements(By.TAG_NAME, "a")
                if len(aTags) == 2:
                    aTags[1].click()
                else:
                    print("Now exiting the ["+aTags[defaultCount].get_attribute("innerText")+"] scenario")
                    driver.execute_script("arguments[0].click();", aTags[defaultCount-1])

            sub_count+=1
    else:
        time.sleep(5)
        getItems(driver)

def getSubMenuCategoriesXTraXTraOptions (driver):
    print("Work in progress")

def loadMoreButtonAvailable (driver):
    available = False
    try:
        if elementExists(driver.find_element(By.CLASS_NAME, "search-listings-module_load-more_OwyvW")):
            available = True

    except NoSuchElementException:
        print("Load More element doesn't exists.")

    return available

def clickLoadMoreButtonPresent(driver):
    if loadMoreButtonAvailable (driver):
        try:
            if len(driver.find_elements(By.CLASS_NAME, "search-listings-module_load-more_OwyvW"))>0:
                loadMoreButtonExists = True
            while (loadMoreButtonExists):
                try:
                    #loadMore = driver.find_element(By.CLASS_NAME, "search-listings-module_load-more_OwyvW")
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "search-listings-module_load-more_OwyvW"))
                        )
                        loadMore = driver.find_element(By.CLASS_NAME, "search-listings-module_load-more_OwyvW")
                        # Interact with the element
                        try:
                            driver.execute_script("arguments[0].click();", loadMore)
                            print("clicked >>> Load More")
                        except TimeoutException:
                            print("Click attempt timed out, retrying...")
                        #driver.execute_script("arguments[0].click();", loadMore)
                        if elementExists(driver.find_elements(By.CLASS_NAME, "search-listings-module_load-more_OwyvW")):
                            loadMoreButtonExists = True
                        else:
                            loadMoreButtonExists = False
                    except TimeoutException:
                        print("Load More Element not found within the given time")
                        if elementExists(driver.find_elements(By.CLASS_NAME, "search-listings-module_load-more_OwyvW")):
                            loadMoreButtonExists = True
                        else:
                            loadMoreButtonExists = False
                        time.sleep(20)
                    except ReadTimeout:
                        print("Load More Element not found, read element failed")
                        if elementExists(driver.find_elements(By.CLASS_NAME, "search-listings-module_load-more_OwyvW")):
                            loadMoreButtonExists = True
                        else:
                            loadMoreButtonExists = False
                        time.sleep(20)
                    #original
                    #time.sleep(5)
                except StaleElementReferenceException:
                    print("Load More Element is stale, reattempting to click")
                    #loadMore = driver.find_element(By.CLASS_NAME, "search-listings-module_load-more_OwyvW")
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "search-listings-module_load-more_OwyvW"))
                        )
                        loadMore = driver.find_element(By.CLASS_NAME, "search-listings-module_load-more_OwyvW")
                        # Interact with the element
                        try:
                            driver.execute_script("arguments[0].click();", loadMore)
                            print("clicked >>> Load More")
                        except TimeoutException:
                            print("Click attempt timed out, retrying...")
                        #driver.execute_script("arguments[0].click();", loadMore)
                        print("clicked >>> Load More")
                        if elementExists(driver.find_elements(By.CLASS_NAME, "search-listings-module_load-more_OwyvW")):
                            loadMoreButtonExists = True
                        else:
                            loadMoreButtonExists = False
                    except TimeoutException:
                        print("Load More Element not found within the given time")
                        if elementExists(driver.find_elements(By.CLASS_NAME, "search-listings-module_load-more_OwyvW")):
                            loadMoreButtonExists = True
                        else:
                            loadMoreButtonExists = False
                        time.sleep(20)
                    except ReadTimeout:
                        print("Load More Element not found, read element failed")
                        if elementExists(driver.find_elements(By.CLASS_NAME, "search-listings-module_load-more_OwyvW")):
                            loadMoreButtonExists = True
                        else:
                            loadMoreButtonExists = False
                        time.sleep(20)
                    #aws time delay
                    #time.sleep(5)
                except TimeoutException:
                    driver.refresh()
                    print("Timing out")
                except ReadTimeout:
                    driver.refresh()
                    print("Read timing out")
        except NoSuchElementException:
            print("Load More Button is no longer available")
        except TimeoutException:
            driver.refresh()
            print("Timing out")
            clickLoadMoreButtonPresent(driver)
        except ReadTimeout:
            driver.refresh()
            print("Read timing out")
            clickLoadMoreButtonPresent(driver)
                
def getItemsssssssss(driver):
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'grid-margin-x')))
    onFIrstPage = False
    counter = 0
    price = 0
    #Load More Button
    LoadMoreExists = loadMoreButtonAvailable(driver)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "panel-module_panel_1aKv4")))
    articles = driver.find_elements(By.CLASS_NAME, "panel-module_panel_1aKv4")
    len(articles)

    while LoadMoreExists:
        articles = driver.find_elements(By.CLASS_NAME, "panel-module_panel_1aKv4")
        for article in articles:
            try:
                if elementExists(articles[counter].find_element(By.LINK_TEXT, "Shop All Options")):
                    onFIrstPage = True
                    button = articles[counter].find_element(By.LINK_TEXT, "Shop All Options")
                    price = articles[counter].find_element(By.CLASS_NAME, "currency-module_currency_29IIm").get_attribute("innerText")
                    #driver.execute_script("arguments[0].scrollIntoView();", button)
                        #actions = ActionChains(driver).move_to_element(button)
                        #actions.execute_script("arguments[0].click();", button)
                        #actions.perform()
                        #Ammended Here
                    actions = ActionChains(driver)
                    actions.move_to_element(button).perform()
                    #button.click()
                    coverDiv = article.find_element(By.CLASS_NAME, "product-card-module_link-underlay_3sfaA")
                    driver.execute_script("arguments[0].click();", coverDiv)
            except NoSuchElementException:
                onFIrstPage = True
                    #buttons = article.find_elements(By.TAG_NAME, "button")
                    #addToCart = buttons[0]
                articles = driver.find_elements(By.CLASS_NAME, "panel-module_panel_1aKv4")
                coverDiv = articles[counter].find_element(By.CLASS_NAME, "product-card-module_link-underlay_3sfaA")
                    #len(aTag)
                aTag = articles[counter].find_elements(By.TAG_NAME, "a")
                price = articles[counter].find_element(By.CLASS_NAME, "currency-module_currency_29IIm").get_attribute("innerText")
                    #aTag[0].click()
                driver.execute_script("arguments[0].click();", coverDiv)
            except StaleElementReferenceException:
                onFIrstPage = True
                #buttons = article.find_elements(By.TAG_NAME, "button")
                    #addToCart = buttons[0]
                articles = driver.find_elements(By.CLASS_NAME, "panel-module_panel_1aKv4")
                coverDiv = articles[counter].find_element(By.CLASS_NAME, "product-card-module_link-underlay_3sfaA")
                    #len(aTag)
                aTag = articles[counter].find_elements(By.TAG_NAME, "a")
                price = articles[counter].find_element(By.CLASS_NAME, "currency-module_currency_29IIm").get_attribute("innerText")
                    #aTag[0].click()
                driver.execute_script("arguments[0].click();", coverDiv)
            getItemDetails(driver,onFIrstPage,price)

        print("<<<<<<<<<<<<<<<<< Next Iteration ("+str(counter+1)+") >>>>>>>>>>>>>>>")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-listings-module_load-more_OwyvW")))
        except TimeoutException:
            print("Failed to located Load More Button")
        LoadMoreExists = loadMoreButtonAvailable(driver)

        if not LoadMoreExists:
            container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
            aTags = container.find_elements(By.TAG_NAME, "a")
            if len(aTags) == 3:
                aTags[2].click()
            else:
                aTags[3].click()

        counter+=1

def getItems(driver):
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'grid-margin-x')))
    except TimeoutException:
        input("Press Enter to continue...5")
    onFIrstPage = False
    counter = 0
    price = 0
    #Load More Button
    clickLoadMoreButtonPresent(driver)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "panel-module_panel_1aKv4")))
    articles = driver.find_elements(By.CLASS_NAME, "panel-module_panel_1aKv4")
    len(articles)

    for article in articles:
        if True:
        #if counter > 1960:
            print("item num >>>>>>>>>>>>>>>>>>  "+str(counter+1))
            print("article total >>>>>>>>>>>>>>>>>>  "+str(len(articles)))
            #Load More Button
            clickLoadMoreButtonPresent(driver)
            try:
                try:
                    if elementExists(article.find_element(By.LINK_TEXT, "Shop All Options")):
                        onFIrstPage = True
                        button = article.find_element(By.LINK_TEXT, "Shop All Options")
                        price = article.find_element(By.CLASS_NAME, "currency-module_currency_29IIm").get_attribute("innerText")
                        #driver.execute_script("arguments[0].scrollIntoView();", button)
                        #actions = ActionChains(driver).move_to_element(button)
                        #actions.execute_script("arguments[0].click();", button)
                        #actions.perform()
                        #Ammended Here
                        actions = ActionChains(driver)
                        actions.move_to_element(button).perform()
                        #button.click()
                        coverDiv = article.find_element(By.CLASS_NAME, "product-card-module_link-underlay_3sfaA")
                        driver.execute_script("arguments[0].click();", coverDiv)
                except NoSuchElementException:
                    onFIrstPage = True
                    #buttons = article.find_elements(By.TAG_NAME, "button")
                    #addToCart = buttons[0]
                    articles = driver.find_elements(By.CLASS_NAME, "panel-module_panel_1aKv4")
                    coverDiv = articles[counter].find_element(By.CLASS_NAME, "product-card-module_link-underlay_3sfaA")
                    #len(aTag)
                    aTag = articles[counter].find_elements(By.TAG_NAME, "a")
                    price = articles[counter].find_element(By.CLASS_NAME, "currency-module_currency_29IIm").get_attribute("innerText")
                    #aTag[0].click()
                    driver.execute_script("arguments[0].click();", coverDiv)
                except StaleElementReferenceException:
                    onFIrstPage = True
                    #buttons = article.find_elements(By.TAG_NAME, "button")
                    #addToCart = buttons[0]
                    articles = driver.find_elements(By.CLASS_NAME, "panel-module_panel_1aKv4")
                    coverDiv = articles[counter].find_element(By.CLASS_NAME, "product-card-module_link-underlay_3sfaA")
                    #len(aTag)
                    aTag = articles[counter].find_elements(By.TAG_NAME, "a")
                    price = articles[counter].find_element(By.CLASS_NAME, "currency-module_currency_29IIm").get_attribute("innerText")
                    #aTag[0].click()
                    driver.execute_script("arguments[0].click();", coverDiv)
                time.sleep(5)
                getItemDetails(driver,onFIrstPage,price)
                time.sleep(5)
            except StaleElementReferenceException:
                try:
                    articles = driver.find_elements(By.CLASS_NAME, "panel-module_panel_1aKv4")
                    if elementExists(articles[counter].find_element(By.LINK_TEXT, "Shop All Options")):
                        onFIrstPage = True
                        button = articles[counter].find_element(By.LINK_TEXT, "Shop All Options")
                        price = articles[counter].find_element(By.CLASS_NAME, "currency-module_currency_29IIm").get_attribute("innerText")
                        driver.execute_script("arguments[0].scrollIntoView();", button)
                        actions = ActionChains(driver).move_to_element(button)
                        actions.execute_script("arguments[0].click();", button)
                        actions.perform()
                        #driver.execute_script("arguments[0].click();", button)
                        articles = driver.find_elements(By.CLASS_NAME, "panel-module_panel_1aKv4")
                        coverDiv = articles[counter].find_element(By.CLASS_NAME, "product-card-module_link-underlay_3sfaA")
                        driver.execute_script("arguments[0].click();", coverDiv)
                except NoSuchElementException:
                    onFIrstPage = True
                    articles = driver.find_elements(By.CLASS_NAME, "panel-module_panel_1aKv4")
                    coverDiv = articles[counter].find_element(By.CLASS_NAME, "product-card-module_link-underlay_3sfaA")
                    aTag = articles[counter].find_elements(By.TAG_NAME, "a")
                    price = articles[counter].find_element(By.CLASS_NAME, "currency-module_currency_29IIm").get_attribute("innerText")
                    driver.execute_script("arguments[0].click();", coverDiv)
                    #coverDiv.click()
                    #driver.execute_script("arguments[0].click();", coverDiv) 
                time.sleep(5)
                getItemDetails(driver,onFIrstPage,price)
                time.sleep(5)
        
        print("<<<<<<<<<<<<<<<<< Next Iteration ("+str(counter+1)+") >>>>>>>>>>>>>>>")

        if counter == len(articles)-1:
            container = driver.find_element(By.CLASS_NAME, "transition-horizontal-module_slide_3FOk5")
            aTags = container.find_elements(By.TAG_NAME, "a")
            indexCounter = 0
            defaultCount = 0
            for aTag in aTags:
                if aTag.get_attribute("aria-current") is not None:
                    defaultCount = indexCounter
                    break
                indexCounter+=1
            #driver.execute_script("arguments[0].click();", aTags[defaultCount-1])
            print("<<<<<<<<<<<<<<<<< Done getting items >>>>>>>>>>>>>>>")
            #aTags[defaultCount-1].click()
            #if len(aTags) == 3:
                #aTags[2].click()
            #else:
                #aTags[3].click()

        counter+=1

def getItemDetails(driver,onNewWindow,advertAmount):
    import time
    itemExists = True

    time.sleep(5)
    if onNewWindow:
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(5)
    else:
        time.sleep(5)
    try:
        WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'buybox-offer-module_single-item_18a_g')))
    except TimeoutException:
        try:
            WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'buybox-offer-module_list-price_2GEsn')))
        except TimeoutException:
            try:
                WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'buybox-offer-module_radio-container_3H43X')))
            except TimeoutException:
                try:
                    time.sleep(5)
                    WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'buybox-offer-module_single-item_18a_g')))
                except TimeoutException:
                    try:
                        driver.refresh()
                        time.sleep(5)
                        WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'buybox-offer-module_single-item_18a_g')))
                    except TimeoutException:
                        try:
                            driver.refresh()
                            time.sleep(5)
                            WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'buybox-offer-module_single-item_18a_g')))
                        except TimeoutException:
                            try:
                                driver.refresh()
                                WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'buybox-offer-module_list-price_2GEsn')))
                            except TimeoutException:
                                try:
                                    driver.refresh()
                                    WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, 'error-module_button_20I_9')))
                                except TimeoutException:
                                    try:
                                        input("Press Enter to continue...7")
                                        WebDriverWait(driver, 5).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, 'buybox-offer-module_single-item_18a_g')))
                                    except TimeoutException:
                                        itemExists = False
                                        print ("Skipping Item.......")
        
        

    if itemExists:
        try:
        
            imgContainer = driver.find_elements(By.CLASS_NAME, "image-box")
            img = imgContainer[0].find_element(By.TAG_NAME, "img")
            ProductTitle = driver.find_element(By.CLASS_NAME, "product-title")
            title = ProductTitle.find_element(By.TAG_NAME, "h1")
            #priceContainer = driver.find_element(By.CLASS_NAME, "currency-module_currency_29IIm")
            try:
                priceDiv = driver.find_element(By.CLASS_NAME, "buybox-offer-module_single-item_18a_g")
                priceContainer = priceDiv.find_element(By.CLASS_NAME, "currency-module_currency_29IIm")
                price = priceContainer.get_attribute("innerText")                 
            except NoSuchElementException:
                price = advertAmount

        except StaleElementReferenceException:
            priceDiv = driver.find_element(By.CLASS_NAME, "buybox-offer-module_single-item_18a_g")
            try:
                priceContainer = priceDiv.find_element(By.CLASS_NAME, "currency-module_currency_29IIm")
                price = priceContainer.get_attribute("innerText")                 
            except NoSuchElementException:
                price = advertAmount
        except TimeoutException:
            input("Press Enter to continue...6")
        
        item_link = driver.current_url
        print(title.get_attribute("innerText").encode("utf-8"))
        print(img.get_attribute("src"))
        print(price)
        print(item_link)
        #Add data to the DB
        items_array = [takealot["item_category"],takealot["item_subcategory"],takealot["item_type"],title.get_attribute("innerText").encode("utf-8"), img.get_attribute("src"),item_link]
        dbs = dbconnection.init_db("takealot",point_to=dbconnection.pointer)
        uniqueId = 0
        if not dbconnection.itemExists(dbs, item_link):
            uniqueId = dbconnection.loadItem(dbs,items_array)
        else:
            uniqueId = dbconnection.getUniqueitemId(dbs,item_link)

        if not dbconnection.pricesWithinTheWeek(dbs, uniqueId):
            now = datetime.now()
            date = now.strftime("%Y-%m-%d")
            time = now.strftime("%H:%M:%S")
            prices_array = [uniqueId,price,date,time]
            dbconnection.loadPrice(dbs, prices_array)



        if onNewWindow:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        else:
            driver.back()
            time.sleep(5)
            # WebDriverWait(driver, 20).until(
            # EC.presence_of_element_located((By.CLASS_NAME, 'recommendation-swiper')))
            # productDescription = driver.find_element(By.CLASS_NAME, "recommendation-swiper")
            try:
                priceDiv = driver.find_element(By.CLASS_NAME, "buybox-offer-module_single-item_18a_g")
                while priceDiv.is_displayed():
                    driver.back()
                    time.sleep(5)
            except NoSuchElementException:
                    time.sleep(5)


#main site
site = "https://www.takealot.com/"
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
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36")
options.add_argument("--start-maximized")

# Create a unique temporary directory for user data
user_data_dir = tempfile.mkdtemp()
options.add_argument("--user-data-dir={}".format(user_data_dir))
#Navigate to site
#driver_path = "C:\\xampp\\htdocs\\price tracer\\chromedriver.exe"
if False:
    driver_path = "C:\\xampp\\htdocs\\price tracer\\chromedriver.exe"
    #driver_path = "/usr/local/bin/chromedriver"
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)


if True:

    # Create a unique temporary directory for user data
    user_data_dir = tempfile.mkdtemp()
    #options.headless = False
    #options.add_argument("--user-data-dir={}".format(user_data_dir))
    #options.add_argument(f"--user-data-dir={user_data_dir}")

    chrome_driver_path = ChromeDriverManager().install()
    print("\n")
    print("ChromeDriver path:{}".format(chrome_driver_path))
    print("\n")

    # Ensure the path is correct and the file exists
    assert os.path.exists(chrome_driver_path), "ChromeDriver not found!"
    print("\n")
    # Install and set up ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
# Set up the remote WebDriver to connect to the Selenium Grid
#browserOptions = Options()
#browserOptions.set_capability('browserName', 'chrome')
# Add any other capabilities you need
#driver = webdriver.Remote(
    #command_executor='http://127.0.0.0:4444/wd/hub',
    #options=browserOptions
    #command_executor='http://13.58.21.137:4444/wd/hub',
    #desired_capabilities=DesiredCapabilities.CHROME
#)

driver.maximize_window()

# Open site
driver.get(site)
# Check if the browser is launched
if driver:
    print("Browser is launched")
    # Optionally, check if the title or URL is accessible
    print("Title:", driver.title)
    print("Current URL:", driver.current_url)
    # Take a screenshot
    screenshot_path = "../screenshot1.png"
    #try:
    #    if driver.save_screenshot(screenshot_path):
    #        print(f"Screenshot saved to {screenshot_path}")
    #    else:
    #        print("Failed to save screenshot")
    #except Exception as e:
    #    print(f"An error occurred: {e}")
        # Log additional details
    #    print(f"Current working directory: {os.getcwd()}")
    #    print(f"Directory contents: {os.listdir('../screenshoots')}")
    #driver.save_screenshot(screenshot_path)
    #print(f"Screenshot saved to {screenshot_path}")
   
else:
    print("Browser is not launched")

time.sleep(100)

try:
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="shopfront-app"]/div[3]/div/div/div[1]/a/img')))
    
except:
    print("Title:", driver.title)
    screenshot_path = "../screenshot2.png"
    driver.save_screenshot(screenshot_path)
    #print(f"Screenshot saved to {screenshot_path}")



WebDriverWait(driver, 100).until(
             EC.presence_of_element_located((By.CLASS_NAME, 'department-dropdown-module_department-categories_RSgO7')))
# read categories
with open('categories.txt', 'r') as file:
    for line in file:
        split_categories = line.strip().split("|")
        #Loop through the departments and get all the data 
        for category in split_categories:
            ul = driver.find_element(By.CLASS_NAME, 'department-dropdown-module_department-categories_RSgO7')
            #ul = driver.find_element(By.XPATH, '//*[@id="shopfront-app"]/header/div/div/div[1]/div/div/div/ul')
            lis = ul.find_elements(By.TAG_NAME, "li")
            main_count = 0
            for li in lis:
                listName = li.get_attribute("innerText")
                if category.lower() in listName.lower():
                    print("click on >>> "+li.get_attribute("innerText"))
                    primaryMenu = li.get_attribute("innerText")
                    menuOption = driver.find_element(By.LINK_TEXT, primaryMenu)
                    #menuOption.click()
                    WebDriverWait(driver, 100).until(
                        EC.element_to_be_clickable((By.LINK_TEXT, primaryMenu)))
                    hover = ActionChains(driver).move_to_element(menuOption)
                    hover.click(menuOption)
                    driver.execute_script("arguments[0].click();", menuOption)
                    hover.perform()
                    #header = driver.find_element(By.CLASS_NAME, 'department-flyout-module_department-header_3tyWE')
                    #time.sleep(100)
                    WebDriverWait(driver, 100).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'department-flyout-module_content_3tZbQ')))
                    firstOptions = driver.find_elements(By.CLASS_NAME, 'department-flyout-module_content_3tZbQ')
                    lis = firstOptions[0].find_elements(By.TAG_NAME, "li")
                    counter = 0
                    for li in lis:
                        try:
                            if li.get_attribute("class"):
                                if li.get_attribute("class").strip() is None or not li.get_attribute("class").strip():
                                    if "finder" not in li.get_attribute("innerText").lower() and "charcoal" not in li.get_attribute("innerText").lower():
                                        #Remove charcoal part
                                        #default counter > 0
                                        #if counter > 2:
                                        if counter > 11:
                                            takealot["item_category"] = li.get_attribute("innerText")
                                            print("option is "+li.get_attribute("innerText"))
                                            print("class is ["+li.get_attribute("class").strip()+"]")
                                            try:
                                                try:
                                                    option_a_tag = li.find_elements(By.TAG_NAME, "a")
                                                    driver.execute_script("arguments[0].click();", option_a_tag[0])
                                                except ElementClickInterceptedException:
                                                    option_a_tag = li.find_elements(By.TAG_NAME, "a")
                                                    driver.execute_script("arguments[0].click();", option_a_tag[0])

                                                time.sleep(5)
                                                getCategories(driver)
                                            except StaleElementReferenceException:
                                                firstOptions = driver.find_elements(By.CLASS_NAME, 'department-flyout-module_content_3tZbQ')
                                                lis = firstOptions[0].find_elements(By.TAG_NAME, "li")
                                                takealot["item_category"] = lis[counter].get_attribute("innerText")
                                                try:
                                                    #lis[counter].click()
                                                    option_a_tag = li.find_elements(By.TAG_NAME, "a")
                                                    driver.execute_script("arguments[0].click();", option_a_tag[0])
                                                except ElementClickInterceptedException:
                                                    option_a_tag = lis[counter].find_elements(By.TAG_NAME, "a")
                                                    driver.execute_script("arguments[0].click();", option_a_tag[0])
                                                time.sleep(5)
                                                getCategories(driver)

                                        #go back after
                                        #driver.back()
                        except StaleElementReferenceException:
                            dept_dropdown = driver.find_element(By.CLASS_NAME, "department-dropdown-module_department-dropdown_3j_Aa")
                            actions = ActionChains(driver)
                            # Hover over Shop by Department drop down
                            actions.move_to_element(dept_dropdown).perform()
                            # Wait for the School submenu to be present and hover over it
                            print("current main menu is "+listName)
                            try:
                                WebDriverWait(driver, 100).until(
                                    EC.element_to_be_clickable((By.LINK_TEXT, listName)))
                            except TimeoutException:
                                dept_dropdown = driver.find_element(By.CLASS_NAME, "department-dropdown-module_department-dropdown_3j_Aa")
                                actions = ActionChains(driver)
                                driver.execute_script("arguments[0].click();", dept_dropdown)
                                actions.move_to_element(dept_dropdown).perform()

                            menuOption = driver.find_element(By.LINK_TEXT, listName)
                            actions.move_to_element(menuOption).perform()
                            WebDriverWait(driver, 100).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'department-flyout-module_content_3tZbQ')))

                            firstOptions = driver.find_elements(By.CLASS_NAME, 'department-flyout-module_content_3tZbQ')
                            lis = firstOptions[0].find_elements(By.TAG_NAME, "li")

                            for li in lis:
                                if lis[counter].get_attribute("class"):
                                    if lis[counter].get_attribute("class").strip() is None or not lis[counter].get_attribute("class").strip():
                                        if "finder" not in lis[counter].get_attribute("innerText").lower():
                                            #default counter > 0
                                            if counter > 0:
                                                takealot["item_category"] = lis[counter].get_attribute("innerText")
                                                print("option is "+lis[counter].get_attribute("innerText"))
                                                print("class is ["+lis[counter].get_attribute("class").strip()+"]")
                                                try:
                                                    try:
                                                        option_a_tag = lis[counter].find_elements(By.TAG_NAME, "a")
                                                        driver.execute_script("arguments[0].click();", option_a_tag[0])
                                                    except ElementClickInterceptedException:
                                                        option_a_tag = lis[counter].find_elements(By.TAG_NAME, "a")
                                                        driver.execute_script("arguments[0].click();", option_a_tag[0])

                                                    time.sleep(5)
                                                    getCategories(driver)
                                                except StaleElementReferenceException:
                                                    firstOptions = driver.find_elements(By.CLASS_NAME, 'department-flyout-module_content_3tZbQ')
                                                    lis = firstOptions[0].find_elements(By.TAG_NAME, "li")
                                                    takealot["item_category"] = lis[counter].get_attribute("innerText")
                                                    try:
                                                        #lis[counter].click()
                                                        option_a_tag = lis[counter].find_elements(By.TAG_NAME, "a")
                                                        driver.execute_script("arguments[0].click();", option_a_tag[0])
                                                    except ElementClickInterceptedException:
                                                        option_a_tag = lis[counter].find_elements(By.TAG_NAME, "a")
                                                        driver.execute_script("arguments[0].click();", option_a_tag[0])
                                                    time.sleep(5)
                                                    getCategories(driver)

                            #go back after
                            #driver.back()
                            
                            
                        counter+=1
                        #driver.back()
            main_count+=1



            #s = //*[@id="shopfront-app"]/header/div/div/div[1]/div/div/div/ul


            