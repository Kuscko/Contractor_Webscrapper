import gc
import time

import schedule # pip install schedule
from selenium import webdriver # pip install selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# local imports
from emailingfunctions import *
from objects import Contract

# login info
login_info = { # define username and password for login_info
    "username": "",
    "password": ""
}

# NIACS codes & STATES declarateion for contract filters
NAICS = ["811420", "238320", "561740", "811412", "561720", "611513", "561311", "442299", "442110"]
STATES = ["Florida", "North Carolina"]


def webDriverApp():
    options = Options()
    #.headless = True
    options.add_argument("--window-size=1920,1080")
    DRIVER_PATH = "webdriver\chromedriver"
    global browser
    browser = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    browser.get("https://app.usfcrgov.com/login.php")


# TODO: Look into logging into the site one time, or re-obtaining a new selenium session for the web browser.
#       making 'browser' a global variable might be the best option when it's called, much like using global conn in
#       db.py
#   Addendum 1: making the browser webdriver object global worked. File now loops without any hickups and memory should
#   be taken care of. Extensive observation is neccessary however on first run through given TWO(2) weeks of run time.

def Scrape(i):
    # Variable Declaration
    nameList=[]
    emailList=[]
    phoneList=[]

    # enters the website link and iterates through valid pages.
    browser.get("https://app.usfcrgov.com/?module=afpds&view=agents&page=" + str(i))
    # initiates each element on the web page using xpath.
    names = browser.find_elements_by_xpath("//ul[contains(@class, 'uk-grid')]/li[1]")
    emails = browser.find_elements_by_xpath("//ul[contains(@class, 'uk-grid')]/li[4]")
    phone_numbers = browser.find_elements_by_xpath("//ul[contains(@class, 'uk-grid')]/li[5]")
    # get the required fields for contractors.
    for name in names:
        placeholder = browser.execute_script("return arguments[0].childNodes[2].textContent", name)
        nameList.append(placeholder.strip())

    for email in emails:
        placeholder = browser.execute_script("return arguments[0].childNodes[2].textContent", email)
        emailList.append(placeholder.strip())

    for phone in phone_numbers:
        placeholder = browser.execute_script("return arguments[0].childNodes[2].textContent", phone)
        phoneList.append(placeholder.strip())
    # appends the required fields to the database 
    for entry in range(0, len(nameList)):
        existCheck = db.get_contract_by_email(emailList[entry])
        if existCheck == 0:
            print(nameList[entry], emailList[entry], str(i))
            row = Contract(name=nameList[entry], email=emailList[entry], phone=phoneList[entry], sent=0)
            db.add_contract(row)
        else:
            pass

def page_iteration():
    # Variable Declaration
    pageCap = 0
    # Get the maximum page numbers to iterate through
    parentElement = browser.find_element_by_css_selector("div.uk-width-1-3.uk-text-center")
    paragraphChildElement = parentElement.find_element_by_tag_name("p")
    childElements = paragraphChildElement.find_elements_by_tag_name("strong")
    for child in childElements:
        if int(child.text) > 1:
            pageCap = int(child.text)
            break
    for i in range(1, pageCap + 1):
        Scrape(i)
    waitCheck = input("WaitCheck")


def enter_form_info():
    # element declarations
    naicsInputBox = browser.find_element_by_id("agents_naics-selectized")
    stateInputBox = browser.find_element_by_id("agents_state-selectized")
    applyFiltersBtn = browser.find_element_by_id("submit")

    # fill in form data for NAICS codes and State info
    for code in range(len(NAICS)):
        naicsInputBox.send_keys(NAICS[code])
        naicsInputBox.send_keys(Keys.ENTER)
        naicsInputBox.click()
        browser.implicitly_wait(3)
    for state in range(len(STATES)):
        stateInputBox.send_keys(STATES[state])
        stateInputBox.send_keys(Keys.ENTER)
        stateInputBox.click()
        browser.implicitly_wait(3)
    browser.implicitly_wait(8)
    applyFiltersBtn.click()
    browser.implicitly_wait(5)


def go_to_agent_listing():
    # open toggle side bar element to access agents button element.
    sideBarToggle = browser.find_element_by_id("sidebar_main_toggle")
    sideBarToggle.click()
    browser.implicitly_wait(5)

    # locate and click agents button element.
    agentsButton = browser.find_element_by_xpath('//li[@title="Agent Finder"]')
    agentsButton.click()

    # wait and call EnterFormInfo
    browser.implicitly_wait(10)


def login():
    # element declarations
    userInput = browser.find_element_by_id("login_username")
    passInput = browser.find_element_by_id("login_password")
    signInButton = browser.find_element_by_id("submit")

    # actions
    userInput.send_keys(login_info['username'])
    passInput.send_keys(login_info['password'])
    signInButton.click()

    # wait and call GoToAgentListing
    browser.implicitly_wait(5)


def start():
    webDriverApp()
    login()
    go_to_agent_listing()
    enter_form_info()
    page_iteration()
    browser.quit()
    StartEmails()



def CleanMeUp():
    '''   
        Runs to clean up the program and any resources left in memory that haven't already been removed.
    '''
    check = input("Are you user you want to close me? Y/N: ")
    if check.lower() == "y":
        gc.collect()
        db.close()
        exit()
    elif check.lower() == "n":
        os.system('cls')
        scheduler()
    else:
        print("Enter a valid entry")
        CleanMeUp()


def scheduler():
    ''' 
        Create a scheduler that executes the program every 14 days
    '''
    db.connect()
    schedule.every(14).days.do(start)
    #schedule.every().monday.at("09:30").do(start)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        CleanMeUp()


if __name__ == '__main__':
    scheduler()
