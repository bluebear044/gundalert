import requests
import urllib3
import time
import traceback
import sys
import re
from log_util import logger
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from db import DB

class Soup:

    urllib3.disable_warnings()

    def appendData(self, url, title, price):
        logger.debug("\n== Item Info ==\nURL : %s\nTITLE : %s\nPRICE : %s\n",url, title , price)
        db = DB()

        if not db.dupCheck(url):
            db.insert(url,title,price)

    def reqUrl(self, url, max_retries=10, retry_interval=1):
        retry_count = 0
        while retry_count < max_retries:
            try:
                logger.info("request url : %s", url)
                response = requests.get(url, verify=False)
                # 성공적인 응답을 받았을 경우 바로 반환합니다.
                if response.status_code == 200:
                    html = response.text.encode("utf-8")
                    logger.debug("response encoding : %s", response.encoding)
                    return html
            except requests.exceptions.RequestException as e:
                logger.error("An exception occurred: %s", str(e))
            # 재시도 간격만큼 대기합니다.
            time.sleep(retry_interval)
            retry_count += 1

        # 최대 재시도 횟수를 초과한 경우 None을 반환합니다.
        return None

    # def reqUrl(self, url):
    #     try:
    #         logger.info("request url : %s", url)
    #         response = requests.get(url, verify=False)
    #         html = response.text.encode("utf-8")
    #         logger.debug("response encoding : %s", response.encoding)
    #         return html
    #     except Exception as e:
    #         logger.error(e)


    def checkStringContains(self, text):

        include_list = ["PG", "MG", "HG", "RG", "RE/100", "로보트혼", "로봇혼"]
        exclude_list = ["경계전기", "데칼", "HGBC", "HGCE", "태양의 기사 피코", "트랜스포머", "SYNDUALITY", "마신영웅전 와타루", "신듀얼리티", "CONVERGE", "HG OP", "HG BD", "HG_BD", "HG BC", "HG CM", "BB/SD", "건프라군", "HG BF", "건담브레이커", "엑시아", "더블오", "프리덤", "저스티스", "데스티니", "HG-IBO"]
        
        if not any(include_str in text for include_str in include_list):
            return False

        if any(exclude_str in text for exclude_str in exclude_list):
            return False

        return True


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
            logger.error(traceback.print_exc())


    def bnkrMallSoup(self, url):

        logger.debug("Request URL : %s", url)
        try:
            html = self.reqUrl(url)
            soup = BeautifulSoup(html, "html.parser")
            orderButton = soup.find_all("button", class_=["show_open buy_reserv btn btn-box full color-red hovNone","show_default buy btn btn-box full color-red hovNone"])
            if 0 < len(orderButton):
                logger.debug("구매가능")
                title = soup.find("div", "title").getText()
                price = soup.find("div", "price").find("span").getText()
                self.appendData(url, title, price)
            else:
                logger.debug("구매불가")
        except Exception as e:
            logger.error(traceback.print_exc())


    def bnkrMallSearchSoup(self):
        try:
            html = self.reqUrl("https://www.bnkrmall.co.kr/goods/category.do?cate=1576&pview=&psort=&cateName=%EA%B1%B4%ED%94%84%EB%9D%BC&page=1&sale=&soldout=Y&reserved=&rowprice=&highprice=&chkbrand=180%2C403%2C562%2C182%2C404%2C503%2C183%2C184%2C181&chkseries=590%2C589%2C49%2C297%2C301%2C300%2C299%2C597%2C291%2C282%2C283%2C791%2C281%2C50%2C756%2C280%2C673&brandIdx=&seriesIdx=&drawCnt=0&drawIdx=&brandCnt=26&seriesCnt=45&realdrawCnt=0&age=&etc=&endGoods=Y")
            soup = BeautifulSoup(html, "html.parser")
            banners = soup.find_all("a", "thumb")

            for item in banners:
                if "goods" in item.get("href"):
                    title = item.find("h5").getText()
                    if self.checkStringContains(title):
                        url = item.get("href").replace("../","https://www.bnkrmall.co.kr/")
                        price = item.find("span", "num font-20 font-bold").getText().replace("\t", "").replace("\n", "")
                        self.appendData(url, title, price)
        except Exception as e:
            logger.error(traceback.print_exc())


    def gundamBoomSoupPaging(self):
        try:
            now = datetime.now()

            for i in range(12):
                yearMonth = now.strftime("%Y%m")
                logger.debug("yearMonth : %s", yearMonth)
                url = "https://www.gundamboom.com/product/reserve.php?cate_no=" + yearMonth
                html = self.reqUrl(url)
                soup = BeautifulSoup(html, "html.parser")
                pages = len(soup.find("ul", "page").find_all("li"))

                for pageNumber in range(1, pages-1):
                    self.gundamBoomSoup(url, pageNumber)

                now += timedelta(days=30)
        except Exception as e:
            logger.error(traceback.print_exc())


    def gundamBoomSoup(self, url, pageNumber):

        logger.debug("Request URL : %s Page : %s", url, pageNumber)
        
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
                            logger.debug("구매가능")
                            itemUrl = "https://www.gundamboom.com" + item.find("dd","name").find("a")["href"]
                            price = item.find("p", "right").find("span").getText()
                            self.appendData(itemUrl, itemTitle, price)
                else:
                    logger.debug("구매불가")
        except Exception as e:
            logger.error(traceback.print_exc())


    def angelGundamSoup(self):
        try:
            html = self.reqUrl("https://www.1004gundam.co.kr/mall/mbn_itemlist.php?rankey=recordno&sort=reserve&sun=4&newreg=&cate=003&q=&key=")
            soup = BeautifulSoup(html, "html.parser")
            banners = soup.find_all("dl", "rightPad")

            for item in banners:
                soldOutText = item.find("span", "ico1").getText()
                if soldOutText != '예약마감':
                    if item.find("dd","name") is not None:
                        itemTitle = item.find("dd","name").getText().encode("ISO-8859-1", "ignore").decode("euc-kr", "ignore")
                        if self.checkStringContains(itemTitle):
                            logger.debug("구매가능")
                            itemUrl = item.find("dd","name")["onclick"].replace("javascript:location.href=", "").replace("'", "")
                            li_tag = item.find("dd", "price").find("li", "left")
                            li_tag.find('span').extract()
                            price = li_tag.get_text()
                            self.appendData(itemUrl, itemTitle, price)
                else:
                    logger.debug("구매불가")
        except Exception as e:
            logger.error(traceback.print_exc())


    def gundamHomeSoupPaging(self):
        try:
            html = self.reqUrl("https://www.gundamhome.com/shop/goods/goods_list.php?&category=028")
            soup = BeautifulSoup(html, "html.parser")
            lastPage = soup.find_all("a", "navi")[-1].getText().replace("[", "").replace("]", "")

            for i in range(int(lastPage)):
                logger.debug("page : %s", i)
                pageNumber = str(i+1)
                self.gundamHomeSoup("https://www.gundamhome.com/shop/goods/goods_list.php?category=028&page="+pageNumber)
        except Exception as e:
            logger.error(traceback.print_exc())


    def gundamHomeSoup(self, url):
        try:
            html = self.reqUrl(url)
            soup = BeautifulSoup(html, "html.parser")
            item_td = soup.find("td", style="padding:15 0")

            item_list = item_td.find_all("td")

            for item in item_list:
                if len(item.find_all("div")) == 3:
                    itemTitle = item.find_all("div")[1].find("a").getText()
                    if self.checkStringContains(itemTitle):
                        itemUrl = item.find_all("div")[1].find("a")["href"].replace("..", "https://www.gundamhome.com/shop")
                        price = item.find_all("div")[2].find("b").getText().replace("원", "")
                        self.appendData(itemUrl, itemTitle, price)

        except Exception as e:
            logger.error(traceback.print_exc())


    def hobbyFactorySoup(self):
        try:
            urls = []
            urls.append("http://www.hobbyfactory.kr/shop/shopbrand.html?type=N&xcode=042&mcode=015") #PG
            urls.append("http://www.hobbyfactory.kr/shop/shopbrand.html?type=N&xcode=042&mcode=001") #MG
            urls.append("http://www.hobbyfactory.kr/shop/shopbrand.html?type=N&xcode=042&mcode=007") #RG
            urls.append("http://www.hobbyfactory.kr/shop/shopbrand.html?type=N&xcode=042&mcode=003") #HGUC
            urls.append("http://www.hobbyfactory.kr/shop/shopbrand.html?type=N&xcode=042&mcode=013") #RE/100
            urls.append("http://www.hobbyfactory.kr/shop/shopbrand.html?type=N&xcode=042&mcode=006") #HG
            urls.append("http://www.hobbyfactory.kr/shop/shopbrand.html?type=N&xcode=042&mcode=020") #1/100
            urls.append("http://www.hobbyfactory.kr/shop/shopbrand.html?type=N&xcode=042&mcode=022") #1/144
            urls.append("http://www.hobbyfactory.kr/shop/shopbrand.html?type=N&xcode=042&mcode=023") #기타등급

            for url in urls:
                html = self.reqUrl(url)
                soup = BeautifulSoup(html, "html.parser")
                item_list = soup.find_all("ul", "item")

                for item in item_list:
                    if len(item.find_all("li","soldout")) == 0:
                        itemTitle = item.find_all("a")[1].getText().encode("ISO-8859-1", "ignore").decode("euc-kr", "ignore")
                        if self.checkStringContains(itemTitle):
                            linkUrl = "http://www.hobbyfactory.kr"+item.find("a").get("href")
                            pattern = r"(http://www.hobbyfactory.kr/shop/shopdetail.html\?branduid=\d+)"
                            itemUrl = re.search(pattern, linkUrl).group(1)
                            price = item.find("li","prd-price").getText().encode("ISO-8859-1", "ignore").decode("euc-kr", "ignore").replace("원", "")
                            self.appendData(itemUrl, itemTitle, price)

        except Exception as e:
            logger.error(traceback.print_exc())


    def naverBandaiSoup(self):
        try:
            urls = []
            urls.append("https://brand.naver.com/bandai/category/7469c4bfaba0478ca06c44cadd9dfdeb?st=RECENT&page=1&size=80") #PG
            urls.append("https://brand.naver.com/bandai/category/d3dec23f9a8c4bbc8de3ab2746312a1c?st=RECENT&page=1&size=80") #MG
            urls.append("https://brand.naver.com/bandai/category/a7f23d00c7204277b9f8e509b7d3fd5b?st=RECENT&page=1&size=80") #RG
            urls.append("https://brand.naver.com/bandai/category/f801c729edcb466ea3057d09f6d63386?st=RECENT&page=1&size=80") #HG
            urls.append("https://brand.naver.com/bandai/category/d02e6260462545008107ee081c7da3f8?st=RECENT&page=1&size=80") #HGUC
            urls.append("https://brand.naver.com/bandai/category/d02e6260462545008107ee081c7da3f8?st=RECENT&page=1&size=80") #기타등급

            for url in urls:
                html = self.reqUrl(url)
                soup = BeautifulSoup(html, "html.parser")
                item_list = soup.find_all("div", "_3iW9G4pEbm")

                for item in item_list:
                    if len(item.find_all("span", "_3nu9XhU47m")) == 0:
                        itemTitle = item.find("strong", "_3pA0Duwrhw").getText()
                        if self.checkStringContains(itemTitle):
                            itemUrl = "https://brand.naver.com"+item.find("a")["href"]
                            price = item.find("span","LGJCRfhDKi").getText().replace("원", "")
                            self.appendData(itemUrl, itemTitle, price)

        except Exception as e:
            logger.error(traceback.print_exc())


if __name__ =="__main__":

    if len(sys.argv) < 2:
        print("Usage : python soup.py [bandai|bandaiSearch|gundamBoom|angelGundam|gundamHome|hobbyFactory|naverBandai]")
        sys.exit(1)

    arg1 = sys.argv[1]
    if arg1 == "bandai":
        Soup().premiumBandaiSoup()
    
    elif arg1 == "bandaiSearch":
        Soup().bnkrMallSearchSoup()
    
    elif arg1 == "gundamBoom":
        Soup().gundamBoomSoupPaging()

    elif arg1 == "angelGundam":
        Soup().angelGundamSoup()

    elif arg1 == "gundamHome":
        Soup().gundamHomeSoupPaging()

    elif arg1 == "hobbyFactory":
        Soup().hobbyFactorySoup()

    elif arg1 == "naverBandai":
        Soup().naverBandaiSoup()
        
    else:
        print("Please insert [bandai|bandaiSearch|gundamBoom|angelGundam|gundamHome|hobbyFactory|naverBandai] ")
