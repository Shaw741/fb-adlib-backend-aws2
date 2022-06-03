from datetime import datetime
from selenium import webdriver
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

class ActiveProxyChecker:
    
    def get_chrome_driver_instance(self, proxyToBeVerified):
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
        options.add_argument('--proxy-server=%s' % proxyToBeVerified)

        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.LINUX.value]   
        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems)
        user_agent = user_agent_rotator.get_random_user_agent()
        options.add_argument(f'user-agent={user_agent}')

        driver = webdriver.Chrome(executable_path="/opt/chromedriver",options=options)

        return driver

    def process_proxies(self, proxyUrls):
        activeProxyList = []
        for proxyToBeVerified in proxyUrls:
            try:
                currentDriver  = self.get_chrome_driver_instance(proxyToBeVerified)
                currentDriver.get('https://www.facebook.com/ads/library/?active_status=all&ad_type=political_and_issue_ads&country=IN&media_type=all')
                print("Working : " + proxyToBeVerified)
                activeProxyList.append(proxyToBeVerified)
            except Exception as e:
                print("Not Working : " + proxyToBeVerified)
                print(e)
            finally:
                currentDriver.quit()
                pass
        return activeProxyList

def lambda_handler(event, context):
    start_time = datetime.now()

    activeProxyChecker = ActiveProxyChecker()
    activeProxyList = activeProxyChecker.process_proxies(event["proxyUrls"])

    combinedProxyPageList = []
    for page in event["fbadslibpages"]:
        pageProxies = {}
        pageProxies["activeProxies"] = activeProxyList
        pageProxies["pageURL"] = page
        combinedProxyPageList.append(pageProxies)

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    print(f"Elapsed run time: {elapsed_time} seconds")

    return {
        "statusCode": 200,
        "combinedProxyPageList": combinedProxyPageList
    }
