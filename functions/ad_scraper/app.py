from datetime import datetime
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import boto3
import time

class FbAdLibAdSpider:
    
    def __init__(self, proxyToBeUsed):
        self.proxyToBeUsed = proxyToBeUsed
    
    def get_chrome_driver_instance(self):
        options = webdriver.ChromeOptions()
        options.binary_location = '/opt/chrome/chrome'
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-gpu")
        options.add_argument('--window-size=1280x1696')
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")
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
        # options.add_argument('--proxy-server=%s' % self.proxyToBeUsed)

        software_names     = [SoftwareName.CHROME.value]
        operating_systems  = [OperatingSystem.LINUX.value]   
        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems)
        user_agent = user_agent_rotator.get_random_user_agent()
        options.add_argument(f'user-agent={user_agent}')

        print(self.proxyToBeUsed)
        driver = webdriver.Chrome(executable_path="/opt/chromedriver",options=options)
        return driver

    def process_ad(self, fbAdlibItem):
        adUrl = "https://www.facebook.com/ads/library/?id=" + fbAdlibItem["adID"]
        print("adURL scrapped :- ", adUrl)
        detailedDriver  = self.get_chrome_driver_instance()
        try:
            detailedDriver.get(adUrl)
            screenshot_filename = "adsScraper.png"
            screenshot_path = "/tmp/" + screenshot_filename
            detailedDriver.save_screenshot(screenshot_path)
            s3 = boto3.client("s3")
            s3.put_object(Bucket="fbadlibtest", Key=screenshot_filename, Body=open(screenshot_path, "rb"))
    
            # Wait for Details to be loaded
            element = WebDriverWait(detailedDriver, 20).until(EC.presence_of_element_located((By.XPATH, "//div [contains( text(), 'See ad details')]")))
            detailedDriver.find_element_by_xpath("//div [contains( text(), 'See ad details')]").click()
            time.sleep(10)
    
            for link in detailedDriver.find_element_by_css_selector('.effa2scm > .qi2u98y8').find_elements_by_tag_name("a"):
                try:
                    fbAdlibItem["adMediaURL"] = link.find_element_by_tag_name("img").get_attribute('src')
                    fbAdlibItem["adMediaType"] = 'image'
                    break
                except Exception as e:
                    print("Exception while adMediaURL Image")
                    print(e)
                    fbAdlibItem["adMediaURL"] = ""
                    fbAdlibItem["adMediaType"] = ""
    
            if fbAdlibItem["adMediaURL"] == "":
                try:
                    fbAdlibItem["adMediaURL"] = detailedDriver.find_element_by_css_selector('.effa2scm > .qi2u98y8').find_element_by_tag_name('video').get_attribute('src')
                    fbAdlibItem["adMediaType"] = "video"
                except Exception as e:
                    print("Exception while adMediaURL Video")
                    print(e)
                    fbAdlibItem["adMediaURL"] = ""
                    fbAdlibItem["adMediaType"] = ""
    
            try:
                fbAdlibItem["adDescription"] = detailedDriver.find_element_by_css_selector(".qi2u98y8.n6ukeyzl").find_element_by_css_selector('.n54jr4lg ._4ik5').text
            except Exception as e:
                print("Exception while adDescription")
                print(e)
                fbAdlibItem["adDescription"] = ""
    
            try:
                fbAdlibItem["ctaStatus"] = detailedDriver.find_element_by_css_selector("._8jg_").find_element_by_css_selector(".duy2mlcu").text
            except Exception as e:
                print("Exception while ctaStatus")
                print(e)
                fbAdlibItem["ctaStatus"] = ""
    
            try:
                for idx, info in enumerate(detailedDriver.find_element_by_css_selector("._8jg_").find_elements_by_css_selector("._4ik5")): 
                    if idx == 0:
                        fbAdlibItem["displayURL"] = info.text
                    if idx == 1:
                        fbAdlibItem["headline"] = info.text
                    if idx == 2:
                        fbAdlibItem["purchaseDescription"] = info.text
            except Exception as e:
                print("Exception while Ads Headline")
                print(e)
    
            try:
                fbAdlibItem["purchaseURL"] = detailedDriver.find_element_by_css_selector('.qi2u98y8.n6ukeyzl').find_elements_by_tag_name('a')[2].get_attribute('href')
            except Exception as e:
                print("Exception while Ads purchaseURL")
                print(e)
    
            ##### Scrape Page Info
            pageInfo = {}
            try:
                pageInfo["name"] = detailedDriver.find_element_by_css_selector(".jbmj41m4").find_element_by_tag_name('a').text
            except Exception as e:
                print("Exception while pageInfo name")
                print(e)
                pageInfo["name"] = ""
            try:
                pageInfo["url"] = detailedDriver.find_element_by_css_selector(".jbmj41m4").find_element_by_tag_name('a').get_attribute('href')
            except Exception as e:
                print("Exception while pageInfo url")
                print(e)
                pageInfo["url"] = ""
            try:
                pageInfo["logo"] = detailedDriver.find_element_by_css_selector(".jbmj41m4").find_element_by_tag_name('img').get_attribute('src')
            except Exception as e:
                print("Exception while pageInfo logo")
                print(e)
                pageInfo["logo"] = ""
    
            fbAdlibItem["pageInfo"] = pageInfo
            # try:
            #     line = json.dumps(fbAdlibItem.__dict__) + ","
            #     print(line)
            #     self.file.write(line)
            # except Exception as e:
            #     print("Error while saving data to file :")
            #     print(e)
        except Exception as e:
            print(e)
        finally:
            detailedDriver.quit()
            return fbAdlibItem


def lambda_handler(event, context):
    start_time = datetime.now()

    proxyToBeUsed=random.choice(event["activeProxies"])
    fbAdLibAdSpider = FbAdLibAdSpider(proxyToBeUsed)

    fbAdlibItem = fbAdLibAdSpider.process_ad(event['fbAdlibItem'])

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    print(f"Elapsed run time: {elapsed_time} seconds")

    return {
        "statusCode": 200,
        "fbAdlibItem": fbAdlibItem
    }