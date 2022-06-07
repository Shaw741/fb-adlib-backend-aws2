from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
# import requests
import boto3
import time
# import io

class FbAdLibPageSpider:

    def __init__(self, proxylist):
        self.proxylist = proxylist
        self.proxyToBeUsed = ''
        self.maxPollingCount = 10
    
    def get_chrome_driver_instance(self):

        options = webdriver.ChromeOptions()
        options.binary_location = '/opt/chrome/chrome'
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-gpu")
        options.add_argument('--window-size=1440x360')
        options.add_argument("--disable-extensions")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument("--no-zygote")
        options.add_experimental_option("useAutomationExtension", False)  # Adding Argument to Not Use Automation Extension
        options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Excluding enable-automation Switch
        options.add_argument("disable-popup-blocking")
        options.add_argument("disable-notifications")
        self.proxyToBeUsed=random.choice(self.proxylist)
        options.add_argument('--proxy-server=%s' % self.proxyToBeUsed)

        # software_names = [SoftwareName.CHROME.value]
        # operating_systems = [OperatingSystem.LINUX.value]   
        # user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems)
        # user_agent = user_agent_rotator.get_random_user_agent()
        # options.add_argument(f'user-agent={user_agent}')

        driver = webdriver.Chrome(executable_path="/opt/chromedriver",options=options)
        return driver

    def polling_for_driver(self, pageUrl):
        for count in range(self.maxPollingCount):
            print(count)
            try:
                print("pageURL scrapped :- ", pageUrl)
                currentDriver  = self.get_chrome_driver_instance()
                currentDriver.get(pageUrl)
                element = WebDriverWait(currentDriver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "_99s5")))
                print("Working !!!!")
                # screenshot_filename = "pageScraper.png"
                # screenshot_path = "/tmp/" + screenshot_filename
                # currentDriver.save_screenshot(screenshot_path)
                # s3 = boto3.client("s3")
                # s3.put_object(Bucket="fbadlibtest", Key='pageURL' + str(count) + '.png', Body=open(screenshot_path, "rb"))
                return currentDriver
            except Exception as ex:
                print("Not Working just remove the IP from list and proceed for next")
                self.proxylist.remove(self.proxyToBeUsed)
                print(ex)
                currentDriver.quit()
                pass

    def process_page(self, pageUrl):

        fbAdLibItemList = []
        try:
            print("Scraping Page -: " + pageUrl )
            currentDriver  = self.polling_for_driver(pageUrl)
            # screenshot_filename = "screenshot11.png"
            # screenshot_path = "/tmp/" + screenshot_filename
            # currentDriver.save_screenshot(screenshot_path)
            # s3 = boto3.client("s3")
            # s3.put_object(Bucket="fbadlibtest", Key=screenshot_filename, Body=open(screenshot_path, "rb"))
            # print("ScreenShot is available!!!!!!")
            # Wait for List of Ads
            try:
                # Get List Of Ads.
                for ads in currentDriver.find_elements_by_class_name("_99s5"):
                    fbAdlibItem = {}
                    for idx, details in enumerate(ads.find_element_by_class_name('hv94jbsx').find_elements_by_class_name('m8urbbhe')):
                        if idx == 0:
                            try:
                                fbAdlibItem["status"] = details.find_element_by_class_name('nxqif72j').text
                            except Exception as e:
                                print("Exception at while status :")
                                #print(e)
                        if idx == 1: 
                            try:
                                fbAdlibItem["startDate"] = details.find_element_by_tag_name('span').text
                            except Exception as e:
                                print("Exception at while startDate :")
                                #print(e)
                        if idx == 2:
                            platformList = []
                            try:
                                for platform in details.find_elements_by_class_name('jwy3ehce'):
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
                            text = details.find_element_by_tag_name('span').text
                            if text.__contains__('ID'):
                                try:
                                    fbAdlibItem["adID"] = details.find_element_by_tag_name('span').text.split(':')[1].strip()
                                except Exception as e:
                                    print("Exception at while adID :")
                                    #print(e)
                            # print(details.find_element_by_tag_name('span').text)
                        if idx == 4:
                            text = details.find_element_by_tag_name('span').text
                            try:
                                if text.__contains__('ID'):
                                    fbAdlibItem["adID"] = text.split(':')[1].strip()
                            except Exception as e:
                                print("Exception at while adID :")
                                #print(e)
                    try:
                        text = ads.find_element_by_class_name('hv94jbsx').find_element_by_class_name('_9b9y')
                        if text:
                            fbAdlibItem["noOfCopyAds"] = text.find_element_by_tag_name('strong').text
                            # print(text.find_element_by_tag_name('strong').text)
                    except Exception as e:
                        fbAdlibItem["noOfCopyAds"] = '0'
                        print("Exception at while noOfCopyAds :")
                        #print(e)
                    fbAdLibItemList.append(fbAdlibItem)
            except Exception as e:
                print(e)
            finally:
                currentDriver.quit()
        
        except Exception as e:
            print("Exception Occured While Scrapping page :" + pageUrl)
            print(str(e))

        finally:
            print(fbAdLibItemList)
            return fbAdLibItemList

def lambda_handler(event, context):
    print(event)
    start_time = datetime.now()
    fbAdLibPageSpider = FbAdLibPageSpider(event["activeProxies"])
    fbAdLibItemList = fbAdLibPageSpider.process_page(event["pageURL"])

    combinedProxyAdList = []
    for fbAdLibItem in fbAdLibItemList:
        adProxies = {}
        adProxies["activeProxies"] = event["activeProxies"]
        adProxies["fbAdlibItem"] = fbAdLibItem
        combinedProxyAdList.append(adProxies)

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    print(f"Elapsed run time: {elapsed_time} seconds")

    return {
        "statusCode": 200,
        "fbAdlibItemList": combinedProxyAdList
    }
