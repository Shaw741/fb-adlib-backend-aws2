from concurrent.futures import ThreadPoolExecutor
from FbAdLibAdDataCleaner import FbAdLibAdDataCleaner
from FbAdLibAdSpider import FbAdLibAdSpider
from FbAdLibPageSpider import FbAdLibPageSpider
from FbAdsLibDataStore import FbAdsLibDataStore

class FbAdsLibScraper:

    def __init__(self, proxyUrls, fbadslibpages):
        self.scraperInput = { "proxyUrls" : proxyUrls, "fbadslibpages" : fbadslibpages }

    def startDataCleaner(self,fbAdlibItem):
        fbAdLibAdDataCleaner = FbAdLibAdDataCleaner()
        cleanedFbAdlibItem = fbAdLibAdDataCleaner.clean_data(fbAdlibItem)
        return cleanedFbAdlibItem

    def startDataStore(self,cleanedFbAdlibItem):
        fbAdsLibDataStore = FbAdsLibDataStore()
        storedFbAdlibItem = fbAdsLibDataStore.save_ad(cleanedFbAdlibItem)
        return storedFbAdlibItem

    def startAdScraper(self,combinedProxyAd):

        fbAdLibAdSpider = FbAdLibAdSpider(combinedProxyAd["activeProxies"])
        fbAdlibItem = fbAdLibAdSpider.process_ad(combinedProxyAd['fbAdlibItem'])

        cleanedFbAdlibItem = self.startDataCleaner(fbAdlibItem)
        storedFbAdlibItem  = self.startDataStore(cleanedFbAdlibItem)

        print(f"Data is successfully stored for Ad : {storedFbAdlibItem['adID']}")

    def startPageScraper(self, combinedProxyPage):

        fbAdLibPageSpider = FbAdLibPageSpider(combinedProxyPage["activeProxies"])
        try:
            fbAdLibItemList = fbAdLibPageSpider.process_page(combinedProxyPage["pageURL"])

            combinedProxyAdList = []
            for fbAdLibItem in fbAdLibItemList:
                adProxies = {}
                adProxies["activeProxies"] = combinedProxyPage["activeProxies"]
                adProxies["fbAdlibItem"] = fbAdLibItem
                combinedProxyAdList.append(adProxies)

            print(f"Got All the Ads for : {combinedProxyPage['pageURL']}")

            result = []
            with ThreadPoolExecutor(max_workers=20) as exe:
                result = exe.map(self.startAdScraper,combinedProxyAdList)

        except Exception as ex:
            print(f'fn.startPageScraper Exception Occured !!!')
            print(ex)
        
    def startScraper(self):

        try:
            combinedProxyPageList = []
            for page in self.scraperInput["fbadslibpages"]:
                pageProxies = {}
                pageProxies["activeProxies"] = self.scraperInput["proxyUrls"]
                pageProxies["pageURL"]       = page
                combinedProxyPageList.append(pageProxies)

            with ThreadPoolExecutor(max_workers=10) as exe:
                result = exe.map(self.startPageScraper,combinedProxyPageList)

        except Exception as ex:
            print("Fn.startScraper Exception Occured !!!")
            print(ex)


        

