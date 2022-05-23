from datetime import datetime
import json
import sys
from concurrent.futures import ThreadPoolExecutor, wait
import time 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from itemadapter import ItemAdapter
from fb_adlib_items import FbAdlibItem, PageInfo


class FbAdLibSpider:

    start_urls = [
                    'https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id=101672787924056&search_type=page&media_type=all',
                    'https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id=100166531477296&search_type=page&media_type=all'
                 ]

    def open_spider(self):
        self.file = open('items.jl', 'w')
        self.file.write("[" + "\n")

    def close_spider(self):
        self.file.write("\n" + "]")
        self.file.close()

    def process_ad(self, adUrl, fbAdlibItem):
        
        print('started scraping ad :', adUrl)
        print(json.dumps(fbAdlibItem.__dict__))

        detailedDriver  = webdriver.Chrome(ChromeDriverManager().install())
        detailedDriver.get(adUrl)

        # Wait for Details to be loaded
        element = WebDriverWait(detailedDriver, 20).until(EC.presence_of_element_located((By.XPATH, "//div [contains( text(), 'See ad details')]")))
        detailedDriver.find_element_by_xpath("//div [contains( text(), 'See ad details')]").click()
        time.sleep(5)

        for link in detailedDriver.find_element_by_css_selector('.effa2scm > .qi2u98y8').find_elements_by_tag_name("a"):
            try:
                fbAdlibItem.adMediaURL = link.find_element_by_tag_name("img").get_attribute('src')
                fbAdlibItem.adMediaType = 'image'
                break
            except Exception as e:
                print("Exception while adMediaURL Image")
                print(e)
                fbAdlibItem.adMediaURL = ""
                fbAdlibItem.adMediaType = ""

        if fbAdlibItem.adMediaURL == "":
            try:
                fbAdlibItem.adMediaURL = detailedDriver.find_element_by_css_selector('.effa2scm > .qi2u98y8').find_element_by_tag_name('video').get_attribute('src')
                fbAdlibItem.adMediaType = "video"
            except Exception as e:
                print("Exception while adMediaURL Video")
                print(e)
                fbAdlibItem.adMediaURL = ""
                fbAdlibItem.adMediaType = ""

        try:
            fbAdlibItem.adDescription = detailedDriver.find_element_by_css_selector(".qi2u98y8.n6ukeyzl").find_element_by_css_selector('.n54jr4lg ._4ik5').text
        except Exception as e:
            print("Exception while adDescription")
            print(e)
            fbAdlibItem.adDescription = ""

        try:
            fbAdlibItem.ctaStatus = detailedDriver.find_element_by_css_selector("._8jg_").find_element_by_css_selector(".duy2mlcu").text
        except Exception as e:
            print("Exception while ctaStatus")
            print(e)
            fbAdlibItem.ctaStatus = ""

        try:
            for idx, info in enumerate(detailedDriver.find_element_by_css_selector("._8jg_").find_elements_by_css_selector("._4ik5")): 
                if idx == 0:
                    fbAdlibItem.displayURL = info.text
                if idx == 1:
                    fbAdlibItem.headline = info.text
        except Exception as e:
            print("Exception while Ads Headline")
            print(e)

        try:
            fbAdlibItem.purchaseURL = detailedDriver.find_element_by_css_selector('.qi2u98y8.n6ukeyzl').find_elements_by_tag_name('a')[2].get_attribute('href')
        except Exception as e:
            print("Exception while Ads purchaseURL")
            print(e)

        ##### Scrape Page Info
        pageInfo = PageInfo()
        try:
            pageInfo.name = detailedDriver.find_element_by_css_selector(".jbmj41m4").find_element_by_tag_name('a').text
        except Exception as e:
            print("Exception while pageInfo name")
            print(e)
            pageInfo.name = ""
        try:
            pageInfo.url = detailedDriver.find_element_by_css_selector(".jbmj41m4").find_element_by_tag_name('a').get_attribute('href')
        except Exception as e:
            print("Exception while pageInfo url")
            print(e)
            pageInfo.url = ""
        try:
            pageInfo.logo = detailedDriver.find_element_by_css_selector(".jbmj41m4").find_element_by_tag_name('img').get_attribute('src')
        except Exception as e:
            print("Exception while pageInfo logo")
            print(e)
            pageInfo.logo = ""

        fbAdlibItem.pageInfo = pageInfo.__dict__
        detailedDriver.quit()
        try:
            line = json.dumps(fbAdlibItem.__dict__) + ","
            print(line)
            self.file.write(line)
        except Exception as e:
            print("Error while saving data to file :")
            print(e)

    def process_page(self, pageUrl):
        print("Page with URL : " + pageUrl + " is being scrapped!!!")
        
        currentDriver  = webdriver.Chrome(ChromeDriverManager().install())
        currentDriver.get(pageUrl)
        time.sleep(10)

        try:
            # Wait for List of Ads
            element = WebDriverWait(currentDriver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "_99s5")))
            fbAdlibItemList = []
            print("total ads found for page :" + str(len(currentDriver.find_elements_by_class_name("_99s5"))))

            try:
                # Get List Of Ads.
                for ads in currentDriver.find_elements_by_class_name("_99s5"):
                    fbAdlibItem = FbAdlibItem()
                    for idx, details in enumerate(ads.find_element_by_class_name('hv94jbsx').find_elements_by_class_name('m8urbbhe')):
                        if idx == 0:
                            # print(details.find_element_by_class_name('nxqif72j').text)
                            try:
                                fbAdlibItem.status = details.find_element_by_class_name('nxqif72j').text
                            except Exception as e:
                                print("Exception at while status :")
                                print(e)
                        if idx == 1: 
                            # print(details.find_element_by_tag_name('span').text)
                            try:
                                fbAdlibItem.startDate = details.find_element_by_tag_name('span').text
                            except Exception as e:
                                print("Exception at while startDate :")
                                print(e)
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
                                fbAdlibItem.platforms = platformList
                            except Exception as e:
                                fbAdlibItem.platforms = platformList
                                print(e)
                        if idx == 3:
                            text = details.find_element_by_tag_name('span').text
                            if text.__contains__('ID'):
                                try:
                                    fbAdlibItem.adID = details.find_element_by_tag_name('span').text.split(':')[1].strip()
                                except Exception as e:
                                    print("Exception at while adID :")
                                    print(e)
                            # print(details.find_element_by_tag_name('span').text)
                        if idx == 4:
                            text = details.find_element_by_tag_name('span').text
                            try:
                                if text.__contains__('ID'):
                                    fbAdlibItem.adID = text.split(':')[1].strip()
                            except Exception as e:
                                print("Exception at while adID :")
                                print(e)
                    try:
                        text = ads.find_element_by_class_name('hv94jbsx').find_element_by_class_name('_9b9y')
                        if text:
                            fbAdlibItem.noOfCopyAds = text.find_element_by_tag_name('strong').text
                            # print(text.find_element_by_tag_name('strong').text)
                    except Exception as e:
                        fbAdlibItem.noOfCopyAds = 0
                        print("Exception at while noOfCopyAds :")
                        print(e)
                    fbAdlibItemList.append(fbAdlibItem)
            except Exception as e:
                print(e)
            currentDriver.quit()

            print(fbAdlibItemList)

            # Get Detailed Ads info
            futures = []

            # scrape and crawl
            with ThreadPoolExecutor(max_workers=5) as executor:
                for idx, adData in enumerate(fbAdlibItemList):
                    detailedAdURL = "https://www.facebook.com/ads/library/?id=" + adData.adID
                    print(detailedAdURL)
                    futures.append(
                        executor.submit(self.process_ad, detailedAdURL, adData)
                    )
            
            # wait(futures)
        except Exception as e:
            print("Exception Occured While Scrapping page :" + pageUrl)
            print(e)


    def scrapeAds(self):

        self.open_spider()

        start_time = datetime.now()
        futures = []

        # scrape and crawl
        with ThreadPoolExecutor(max_workers=2) as executor:
            for idx, pageUrl in enumerate(self.start_urls):
                futures.append(
                    executor.submit(self.process_page, pageUrl)
                )

        wait(futures)
        self.close_spider()
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        print(f"Elapsed run time: {elapsed_time} seconds")

if __name__ == "__main__":
    fbAdLibSpider = FbAdLibSpider()
    fbAdLibSpider.scrapeAds()