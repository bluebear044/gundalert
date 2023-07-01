import requests
import urllib3
import time
import logging
import traceback
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from db import DB

class Soup:

    logging.basicConfig(filename="gundalert.log", encoding="utf-8", level=logging.INFO)
    urllib3.disable_warnings()

    def appendData(self, url, title, price):
        logging.debug("\n== Item Info ==\nURL : %s\nTITLE : %s\nPRICE : %s\n",url, title , price)
        db = DB()
        db.insert(url,title,price)

    def reqUrl(self, url, max_retries=10, retry_interval=1):
        retry_count = 0
        while retry_count < max_retries:
            try:
                logging.info("request url : %s", url)
                response = requests.get(url, verify=False)
                # 성공적인 응답을 받았을 경우 바로 반환합니다.
                if response.status_code == 200:
                    html = response.text.encode("utf-8")
                    logging.debug("response encoding : %s", response.encoding)
                    return html
            except requests.exceptions.RequestException as e:
                logging.error("An exception occurred: %s", str(e))
            # 재시도 간격만큼 대기합니다.
            time.sleep(retry_interval)
            retry_count += 1

        # 최대 재시도 횟수를 초과한 경우 None을 반환합니다.
        return None

    # def reqUrl(self, url):
    #     try:
    #         logging.info("request url : %s", url)
    #         response = requests.get(url, verify=False)
    #         html = response.text.encode("utf-8")
    #         logging.debug("response encoding : %s", response.encoding)
    #         return html
    #     except Exception as e:
    #         logging.error(e)


    def checkStringContains(self, paramString):

        subStrings = ["PG", "MG", "HG", "RG", "RE/100", "로보트혼", "로봇혼"]
        
        for subString in subStrings:
            if subString in paramString:
                return True
        return False


    def premiumBandaiSoup(self):
        try:
            html = self.reqUrl("https://www.bnkrmall.co.kr/premium/p_category.do")
            soup = BeautifulSoup(html, "html.parser")
            banners = soup.find_all("a", "item")
            
            for item in banners:
                if "goods" in item.get("href") and self.checkStringContains(item.find("p","name").getText()):
                    url = item.get("href").replace("../","https://www.bnkrmall.co.kr/")
                    self.bnkrMallSoup(url)
        except Exception as e:
            logging.error(traceback.print_exc())


    def bnkrMallSoup(self, url):

        logging.debug("Request URL : %s", url)
        try:
            html = self.reqUrl(url)
            soup = BeautifulSoup(html, "html.parser")
            orderButton = soup.find_all("button", class_=["show_open buy_reserv btn btn-box full color-red hovNone","show_default buy btn btn-box full color-red hovNone"])
            if 0 < len(orderButton):
                logging.debug("구매가능")
                title = soup.find("div", "title").getText()
                price = soup.find("div", "price").find("span").getText()
                self.appendData(url, title, price)
            else:
                logging.debug("구매불가")
        except Exception as e:
            logging.error(traceback.print_exc())


    def bnkrMallSearchSoup(self):
        try:
            html = self.reqUrl("https://www.bnkrmall.co.kr/goods/category.do?cate=1576&pview=&psort=&cateName=%EA%B1%B4%ED%94%84%EB%9D%BC&page=1&sale=&soldout=Y&reserved=&rowprice=&highprice=&chkbrand=180%2C403%2C562%2C182%2C404%2C503%2C183%2C184%2C181&chkseries=590%2C589%2C49%2C297%2C301%2C300%2C299%2C597%2C291%2C282%2C283%2C791%2C281%2C50%2C756%2C280%2C673&brandIdx=&seriesIdx=&drawCnt=0&drawIdx=&brandCnt=26&seriesCnt=45&realdrawCnt=0&age=&etc=&endGoods=Y")
            soup = BeautifulSoup(html, "html.parser")
            banners = soup.find_all("a", "thumb")

            for item in banners:
                if "goods" in item.get("href"):
                    url = item.get("href").replace("../","https://www.bnkrmall.co.kr/")
                    title = item.find("h5").getText()
                    price = item.find("span", "num font-20 font-bold").getText().replace("\t", "").replace("\n", "")
                    self.appendData(url, title, price)
        except Exception as e:
            logging.error(traceback.print_exc())


    def gundamBoomSoupPaging(self):
        try:
            now = datetime.now()

            for i in range(12):
                yearMonth = now.strftime("%Y%m")
                logging.debug("yearMonth : %s", yearMonth)
                url = "https://www.gundamboom.com/product/reserve.php?cate_no=" + yearMonth
                html = self.reqUrl(url)
                soup = BeautifulSoup(html, "html.parser")
                pages = len(soup.find("ul", "page").find_all("li"))

                for pageNumber in range(1, pages-1):
                    self.gundamBoomSoup(url, pageNumber)

                now += timedelta(days=30)
        except Exception as e:
            logging.error(traceback.print_exc())


    def gundamBoomSoup(self, url, pageNumber):

        logging.debug("Request URL : %s Page : %s", url, pageNumber)
        
        try:
            html = self.reqUrl(url+"&page="+str(pageNumber))
            soup = BeautifulSoup(html, "html.parser")
            banners = soup.find_all("dl")

            for item in banners:
                soldOutImage = item.find("span", "noPic")
                if soldOutImage is None:
                    if item.find("dd","name") is not None:
                        itemTitle = item.find("dd","name").find("a").getText().encode("ISO-8859-1", "ignore").decode("euc-kr", "ignore")
                        if self.checkStringContains(itemTitle):
                            logging.debug("구매가능")
                            itemUrl = "https://www.gundamboom.com" + item.find("dd","name").find("a")["href"]
                            price = item.find("p", "right").find("span").getText()
                            self.appendData(itemUrl, itemTitle, price)
                else:
                    logging.debug("구매불가")
        except Exception as e:
            logging.error(traceback.print_exc())


if __name__ =="__main__":
    soup = Soup()
    soup.premiumBandaiSoup()
    soup.bnkrMallSearchSoup()
    soup.gundamBoomSoupPaging()