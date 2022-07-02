from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import boto3
from webdriver_manager.chrome import ChromeDriverManager
from decouple import config
from selenium.webdriver.chrome.options import Options

class FbAdLibPageSpider:

    def __init__(self, proxylist):
        self.proxylist = proxylist
        self.proxyToBeUsed = ''
        self.maxPollingCount = 25
        self.bucket_name = "fbadslib-dev"

    def takeScreenShot(self, driver, ss_name):
        screenshot_path = "/tmp/" + ss_name
        driver.save_screenshot(screenshot_path)
        s3 = boto3.client("s3",
                          aws_access_key_id=config("aws_access_key_id"),
                          aws_secret_access_key=config("aws_secret_access_key"))
        s3.put_object(Bucket=self.bucket_name, Key=ss_name, Body=open(screenshot_path, "rb"))
    
    def get_chrome_driver_options(self):

        options = Options()
        options.binary_location = '/opt/chrome-linux/chrome'
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-gpu")
        options.add_argument('--window-size=1440x626')
        options.add_argument("--disable-extensions")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument("--no-zygote")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("disable-popup-blocking")
        options.add_argument("disable-notifications")
        self.proxyToBeUsed  = random.choice(self.proxylist)
        options.add_argument('--proxy-server=%s' % self.proxyToBeUsed)

        return options

    def polling_for_driver(self, pageUrl):
        attempts = 0
        workingDriver = None
        while True:
            driver = None
            attempts = attempts + 1
            if attempts == self.maxPollingCount:
                break
            else:
                print("Started attempts :- " + str(attempts))
                try:
                    options  = self.get_chrome_driver_options()
                    driver = webdriver.Chrome("/opt/chromedriver",options=options)
                    driver.get(pageUrl)
                    element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "_99s5")))
                    print(f"Working { self.proxyToBeUsed }!!!!")
                    workingDriver = driver
                    break
                except Exception as ex:
                    if driver:
                        driver.quit()
                    print(f"Not Working { self.proxyToBeUsed }!!!!")
                    print(ex)
                    continue
        return workingDriver            
            

    def process_page(self, pageUrl):
        print("Page URL to be scraped :- " + pageUrl)
        fbAdLibItemList = []
        driver = None
        try:
            driver = self.polling_for_driver(pageUrl)

            for ads in driver.find_elements(by=By.CLASS_NAME, value="_99s5"):

                fbAdlibItem = {
                    "status": '',
                    "startDate":'',
                    "platforms":[],
                    "adID":'',
                    "noOfCopyAds":"0 ads"
                }

                for idx, details in enumerate(ads.find_element(by=By.CLASS_NAME, value='hv94jbsx').find_elements(by=By.CLASS_NAME, value='m8urbbhe')):
                    if idx == 0:
                        try:
                            fbAdlibItem["status"] = details.find_element(by=By.CLASS_NAME, value='nxqif72j').text
                        except Exception as e:
                            print("Exception at while status :")
                            #print(e)
                    if idx == 1: 
                        try:
                            fbAdlibItem["startDate"] = details.find_element(by=By.TAG_NAME, value='span').text
                        except Exception as e:
                            print("Exception at while startDate :")
                            #print(e)
                    if idx == 2:
                        platformList = []
                        try:
                            for platform in details.find_elements(by=By.CLASS_NAME, value='jwy3ehce'):
                                platform_style = platform.get_attribute("style")
                                if platform_style.__contains__('0px'):
                                    platformList.append("Facebook")
                                    # print("Facebook")
                                if platform_style.__contains__('-19px'):
                                    platformList.append("Instagram")
                                    # print("Instagram")
                                if platform_style.__contains__('-17px -66px'):
                                    platformList.append("Audience Network")
                                    # print("Audience Network")
                                if platform_style.__contains__('-17px -79px'):
                                    platformList.append("Messenger")
                                    # print("Messenger")
                            fbAdlibItem["platforms"] = platformList
                        except Exception as e:
                            fbAdlibItem["platforms"] = platformList
                            #print(e)
                    if idx == 3:
                        text = details.find_element(by=By.TAG_NAME, value='span').text
                        if text.__contains__('ID'):
                            try:
                                fbAdlibItem["adID"] = details.find_element(by=By.TAG_NAME, value='span').text.split(':')[1].strip()
                            except Exception as e:
                                print("Exception at while adID :")
                                #print(e)
                    if idx == 4:
                        text = details.find_element(by=By.TAG_NAME, value='span').text
                        try:
                            if text.__contains__('ID'):
                                fbAdlibItem["adID"] = text.split(':')[1].strip()
                        except Exception as e:
                            print("Exception at while adID :")
                            #print(e)

                try:
                    text = ads.find_element(by=By.CLASS_NAME, value='hv94jbsx').find_element(by=By.CLASS_NAME, value='_9b9y')
                    if text:
                        fbAdlibItem["noOfCopyAds"] = int(text.find_element(by=By.TAG_NAME, value='strong').text)
                except Exception as e:
                    print("Exception at noOfCopyAds :--")
                    #print(e)

                fbAdLibItemList.append(fbAdlibItem)
        except Exception as e:
            print(f"Exception Occured While getting list of ads from page :::: {pageUrl}")
            print(e)
            if driver:
                driver.quit()
        finally:
            print(f"Got List Of Ads for a Page  ::::  {pageUrl}")
            if driver:
                driver.quit()
            return fbAdLibItemList