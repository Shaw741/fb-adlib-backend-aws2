import scrapy
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 
from fb_adlib.items import FbAdlibItem, PageInfo

class FBAdLibSpider(scrapy.Spider):
    name = "fbAdLib"
    start_urls = [
        'https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id=101672787924056&search_type=page&media_type=all',
        'https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id=100166531477296&search_type=page&media_type=all'
    ]

    def parse(self, response):

        # chrome_options = webdriver.ChromeOptions()
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", prefs)
        # # chrome_options=chrome_options

        # Current Page URL
        currentPageUrl = response.url

        # 2 Chrome Driver For each Page 
        currentDriver  = webdriver.Chrome(ChromeDriverManager().install())
        detailedDriver = webdriver.Chrome(ChromeDriverManager().install())


        currentDriver.get(currentPageUrl)
        time.sleep(10)

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
                            fbAdlibItem['status'] = details.find_element_by_class_name('nxqif72j').text
                        except Exception as e:
                            print("Exception at while status :")
                            print(e)
                    if idx == 1: 
                        # print(details.find_element_by_tag_name('span').text)
                        try:
                            fbAdlibItem['startDate'] = details.find_element_by_tag_name('span').text
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
                            fbAdlibItem['platforms'] = platformList
                        except Exception as e:
                            fbAdlibItem['platforms'] = platformList
                            print(e)
                    if idx == 3:
                        text = details.find_element_by_tag_name('span').text
                        if text.__contains__('ID'):
                            try:
                                fbAdlibItem['adID'] = details.find_element_by_tag_name('span').text.split(':')[1].strip()
                            except Exception as e:
                                print("Exception at while adID :")
                                print(e)
                        # print(details.find_element_by_tag_name('span').text)
                    if idx == 4:
                        text = details.find_element_by_tag_name('span').text
                        try:
                            if text.__contains__('ID'):
                                fbAdlibItem['adID'] = text.split(':')[1].strip()
                        except Exception as e:
                            print("Exception at while adID :")
                            print(e)
                try:
                    text = ads.find_element_by_class_name('hv94jbsx').find_element_by_class_name('_9b9y')
                    if text:
                        fbAdlibItem['noOfCopyAds'] = text.find_element_by_tag_name('strong').text
                        # print(text.find_element_by_tag_name('strong').text)
                except Exception as e:
                    fbAdlibItem['noOfCopyAds'] = 0
                    print("Exception at while noOfCopyAds :")
                    print(e)
                fbAdlibItemList.append(fbAdlibItem)
        except Exception as e:
            print(e)
        currentDriver.quit()

        print(fbAdlibItemList)
        # Get Detailed Ads info
        for idx, scrappedAds in enumerate(fbAdlibItemList):
            if scrappedAds['adID']:
                detailedAdURL = "https://www.facebook.com/ads/library/?id=" + scrappedAds['adID']
                print(detailedAdURL)
                yield scrapy.Request(detailedAdURL, callback = self.parse_detailedAd_contents, cb_kwargs=dict(fbAdlibItem=scrappedAds, detailedDriver=detailedDriver))

                # Get Detailed Ads info
        # # 507162470876850 video
        # # 525881972487516 image
        # detailedAdURL = "https://www.facebook.com/ads/library/?id=507162470876850"
        # yield scrapy.Request(detailedAdURL, callback = self.parse_detailedAd_contents, cb_kwargs=dict(fbAdlibItem= FbAdlibItem(), detailedDriver=detailedDriver))

    def parse_detailedAd_contents(self, response, fbAdlibItem, detailedDriver):
        print('started scraping ad :', response.url)
        detailedDriver.get(response.url)

        # Wait for Details to be loaded
        element = WebDriverWait(detailedDriver, 20).until(EC.presence_of_element_located((By.XPATH, "//div [contains( text(), 'See ad details')]")))
        detailedDriver.find_element_by_xpath("//div [contains( text(), 'See ad details')]").click()
        time.sleep(5)
        for link in detailedDriver.find_element_by_css_selector('.effa2scm > .qi2u98y8').find_elements_by_tag_name("a"):
            try:
                fbAdlibItem['adMediaURL'] = link.find_element_by_tag_name("img").get_attribute('src')
                fbAdlibItem['adMediaType'] = 'image'
                break
            except Exception as e:
                print("Exception while adMediaURL Image")
                print(e)
                fbAdlibItem['adMediaURL'] = ""
                fbAdlibItem['adMediaType'] = ""

        if fbAdlibItem['adMediaURL'] == "":
            try:
                fbAdlibItem['adMediaURL'] = detailedDriver.find_element_by_css_selector('.effa2scm > .qi2u98y8').find_element_by_tag_name('video').get_attribute('src')
                fbAdlibItem['adMediaType'] = "video"
            except Exception as e:
                print("Exception while adMediaURL Video")
                print(e)
                fbAdlibItem['adMediaURL'] = ""
                fbAdlibItem['adMediaType'] = ""

        try:
            fbAdlibItem['adDescription'] = detailedDriver.find_element_by_css_selector(".qi2u98y8.n6ukeyzl").find_element_by_css_selector('.n54jr4lg ._4ik5').text
        except Exception as e:
            print("Exception while adDescription")
            print(e)
            fbAdlibItem['adDescription'] = ""

        try:
            fbAdlibItem["ctaStatus"] = detailedDriver.find_element_by_css_selector("._8jg_").find_element_by_css_selector(".duy2mlcu").text
        except Exception as e:
            print("Exception while ctaStatus")
            print(e)
            fbAdlibItem['ctaStatus'] = ""

        try:
            for idx, info in enumerate(detailedDriver.find_element_by_css_selector("._8jg_").find_elements_by_css_selector("._4ik5")): 
                if idx == 0:
                    fbAdlibItem['displayURL'] = info.text
                if idx == 1:
                    fbAdlibItem['headline'] = info.text
        except Exception as e:
            print("Exception while Ads Headline")
            print(e)

        try:
            fbAdlibItem['purchaseURL'] = detailedDriver.find_element_by_css_selector('.qi2u98y8.n6ukeyzl').find_elements_by_tag_name('a')[2].get_attribute('href')
        except Exception as e:
            print("Exception while Ads purchaseURL")
            print(e)

        ##### Scrape Page Info
        pageInfo = PageInfo()
        try:
            pageInfo['name'] = detailedDriver.find_element_by_css_selector(".jbmj41m4").find_element_by_tag_name('a').text
        except Exception as e:
            print("Exception while pageInfo name")
            print(e)
            pageInfo['name'] = ""
        try:
            pageInfo['url'] = detailedDriver.find_element_by_css_selector(".jbmj41m4").find_element_by_tag_name('a').get_attribute('href')
        except Exception as e:
            print("Exception while pageInfo url")
            print(e)
            pageInfo['url'] = ""
        try:
            pageInfo['logo'] = detailedDriver.find_element_by_css_selector(".jbmj41m4").find_element_by_tag_name('img').get_attribute('src')
        except Exception as e:
            print("Exception while pageInfo logo")
            print(e)
            pageInfo['logo'] = ""

        fbAdlibItem['pageInfo'] = pageInfo

        # pageInfo['platform'] = []
        # try:
        #     pagePlatformInfo = PagePlatformInfo()
        #     print("total platforms: ", len(detailedDriver.find_elements_by_css_selector('.hck7fp40')))
        #     for plt in detailedDriver.find_elements_by_css_selector('.hck7fp40'):
        #         try:
        #             if plt.find_element_by_tag_name('i').get_attribute('class').__contains__('sx_6ae709'):
        #                 pagePlatformInfo['name'] = "Facebook"
        #                 try:
        #                     pagePlatformInfo['likes'] = plt.find_element_by_css_selector('.e946d6ch:nth-child(1)').text
        #                 except:
        #                     pagePlatformInfo['likes'] = 0
        #             if plt.find_element_by_tag_name('i').get_attribute('class').__contains__('sx_a5eb6a'):
        #                 pagePlatformInfo['name'] = "Instagram"
        #                 try:
        #                     pagePlatformInfo['followers'] = plt.find_element_by_css_selector('.e946d6ch:nth-child(1)').text
        #                 except:
        #                     pagePlatformInfo['followers'] = 0
        #         except:
        #             print(fbAdlibItem)
        #             print(pageInfo)
        #             print("Exception Occured while getting Individual Page Platforms!!")
        # except:
        #     print("Exception Occured while getting Page Platforms!!")

        yield fbAdlibItem
