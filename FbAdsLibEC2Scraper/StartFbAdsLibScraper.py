import time
from datetime import datetime
from FbAdsLibScraper import FbAdsLibScraper

try:
    t1 = time.perf_counter()
    print(f"***********************************Scraper Start : { datetime.now().strftime('%d/%m/%Y %H:%M:%S') } ***********************")
    proxyUrls=[
        "192.187.111.82:17066",
        "198.204.249.42:19002",
        "69.30.217.114:19001",
        "173.208.152.162:19009",
        "198.204.241.50:17020",
        "192.187.111.82:17062",
        "107.150.42.74:17001",
        "192.187.111.82:17093",
        "107.150.42.146:19017",
        "198.204.249.42:19020"
    ]
    fbadslibpages=[
            "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id=109703320647903&search_type=page&media_type=all",
            # "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id=101194931664714&search_type=page&media_type=all",
		    # "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id=100613581460475&search_type=page&media_type=all",
		    # "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id=2324132321162033&search_type=page&media_type=all",
		    # "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id=101672787924056&search_type=page&media_type=all",
		    # "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id=100166531477296&search_type=page&media_type=all"
          ]
    fbAdsLibScraper = FbAdsLibScraper(proxyUrls, fbadslibpages)
    fbAdsLibScraper.startScraper()
    t2 = time.perf_counter()
    print(f"***********************************Scraper End : { datetime.now().strftime('%d/%m/%Y %H:%M:%S') } ***********************")
    print(f'Scraper Took:{t2 - t1} seconds')
except Exception as ex:
    print("Exception Occured While Scrapping :-")
    print(ex)


# try:
#     t1 = time.perf_counter()
#     print(f"***********************************Scraper Start : { datetime.now().strftime('%d/%m/%Y %H:%M:%S') } ***********************")
#     cleanedFbAdlibItem = {'status': 'Active', 'startDate': '2022-06-08', 'platforms': ['Facebook', 'Facebook', 'Audience Network', 'Messenger'], 'adID': '3219422001610117', 'noOfCopyAds': '2', 'adMediaURL': 'https://video-lax3-1.xx.fbcdn.net/v/t42.1790-2/10000000_425870779340674_1677875396473456968_n.?_nc_cat=110&ccb=1-7&_nc_sid=cf96c8&_nc_ohc=WVQMTa6ZNa4AX-kVeZK&_nc_ht=video-lax3-1.xx&oh=00_AT-MOoZNcH6Ee3DBXJhH1UGjVp2kiEblC935HzCDA5NAmg&oe=62BD780C', 'adMediaType': 'video', 'adDescription': '??Tired of Your Trimmer Being too Weak to Cut Tough Weeds???Transform Your Weeder to A Beast That Slices Through Anything!Get it here????https://www.culticate.com/6Trimmer', 'ctaStatus': 'Shop now','displayURL': 'WWW.CULTICATE.COM', 'headline': '??50% Off Limited Time Only UNIVERSAL 6-Steel Razors Trimmer Head', 'purchaseDescription': '', 'purchaseURL': 'https://l.facebook.com/l.php?u=https%3A%2F%2Fwww.              culticate.com%2Fproducts%2F6-steel-blades-trimmer-head&h=AT082mYqvDlkddTe_OOa2ScrH65eGkTEKGKtKkJki_5_4DN0UEiOF8worQhubYDmh49meO4cwcrmvXBvi-pzzbjk4t4Q2uynNDLeYm4                                     DmomPWd3c9ZcLozMgI4gB9gYsBLzkq0VusYvt3Q', 'pageInfo': {'name': 'Culticate', 'url': 'https://www.facebook.com/Culticate/', 'logo': 'https://scontent-lax3-2.xx.fbcdn.net/v/t39.354266/286938011_965862330775799_450487203209140268_n.jpg?stp=dst-jpg_s60x60&_nc_cat=111&ccb=1-7&_nc_sid=cf96c8&_nc_ohc=pOglLCUd3BUAX_H4Uyw&_nc_ht=scontent-lax3-2.xx&oh=00_AT9NtMZklgqWPMdbUK1sGrEsI3J4K-jVm7X8XLaSmzq81g&oe=62C252D0'}}
#     fbAdsLibDataStore = FbAdsLibDataStore()
#     storedFbAdlibItem = fbAdsLibDataStore.save_ad(cleanedFbAdlibItem)
#     t2 = time.perf_counter()
#     print(f"***********************************Scraper End : { datetime.now().strftime('%d/%m/%Y %H:%M:%S') } ***********************")
#     print(f'MultiThreaded Code Took:{t2 - t1} seconds')
# except Exception as ex:
#     print("Exception While Scrapping :-")
#     print(ex)


