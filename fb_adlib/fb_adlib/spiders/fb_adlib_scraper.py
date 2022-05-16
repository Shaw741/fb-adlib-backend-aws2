import scrapy
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from fb_adlib.items import FbAdlibItem


class FBAdLibSpider(scrapy.Spider):
    name = "fbAdLib"
    start_urls = [
        'https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id=101672787924056&search_type=page&media_type=all',
    ]

    def __init__(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def parse(self, response):
        self.driver.get(response.url)
        element = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "_99s5")))
        for ads in self.driver.find_elements_by_class_name("_99s5"):
            fbAdlibItem = FbAdlibItem()
            for idx, details in enumerate(ads.find_element_by_class_name('hv94jbsx').find_elements_by_class_name('m8urbbhe')):
                if idx == 0:
                    print(details.find_element_by_class_name('nxqif72j').text)
                    fbAdlibItem['status'] = details.find_element_by_class_name('nxqif72j').text
                if idx == 1: 
                    print(details.find_element_by_tag_name('span').text)
                    fbAdlibItem['startDate'] = details.find_element_by_tag_name('span').text
                if idx == 2:
                    platformList = []
                    for platform in details.find_elements_by_class_name('jwy3ehce'):
                        platform_style = platform.get_attribute("style")
                        if platform_style.__contains__('0px -1040px'):
                            platformList.append("Facebook")
                            print("Facebook")
                        if platform_style.__contains__('-19px -824px'):
                            platformList.append("Instagram")
                            print("Instagram")
                        if platform_style.__contains__('-17px -66px'):
                            platformList.append("Audience Network")
                            print("Audience Network")
                        if platform_style.__contains__('-17px -79px'):
                            platformList.append("Messenger")
                            print("Messenger")
                    fbAdlibItem['platforms'] = platformList
                if idx == 3:
                    fbAdlibItem['adID'] = details.find_element_by_tag_name('span').text
                    print(details.find_element_by_tag_name('span').text)
            detailedAdURL = "https://www.facebook.com/ads/library/?id=" + fbAdlibItem['adID']
            yield scrapy.Request(detailedAdURL, callback = self.parse_detailedAd_contents, cb_kwargs=dict(fbAdlibItem=fbAdlibItem))

    def parse_detailedAd_contents(self, response, fbAdlibItem):
        yield fbAdlibItem
