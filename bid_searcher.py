#!/usr/bin/env python
import urllib2
import re
import time
import logging
import sys

logging.basicConfig (level=logging.DEBUG)

def get_content (url):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers={'User-Agent':user_agent,}
    request=urllib2.Request(url,None,headers)
    try:
        response = urllib2.urlopen(request)
        data = response.read()

        html = data
    except:
        logging.error ("get_content urlopen fail")
    return html

class BidProduct:
    def __init__ (self):
        logging.debug ("BidProduct construct")
        self.seller = None
        self.price = None
        self.current_price = None
        self.link = None
        self.title = None

    def get_seller (self):
        return self.sellef

    def get_link (self):
        return self.link

    def get_current_price (self):
        return self.current_price

    def get_price (self):
        return self.price

class BidSearcher:
    def __init__ (self, keyword, seller = None):
        logging.debug ("BidSearcher construct")

    def __get_all_links (self, url):
        pass

    def __get_products (self, url):
        pass

    def get_products (self):
        return self.__products__

class RutenSearcher(BidSearcher):
    def __init__ (self, keyword, seller = None):
        BidSearcher (keyword, seller)
        self.__products__ = []
        self.html = None
        self.max_page = 10
        self.seller = seller

        if seller is None:
            main_url = "http://search.ruten.com.tw/search/s000.php?enc=u&searchfrom=searchf&t=0&k="
        else:
            main_url = "http://search.ruten.com.tw/search/ulist00.php?s=" + seller + "&enc=b&c=0&k="

        url = main_url + keyword
        logging.debug ("url = %s" % url)
        products = []
        for i in range (0, self.max_page):
            if self.seller is not None:
                i = i + 1
            _url = ("%s&p=%d" % (url, i))
            _products = self.__get_products (_url)
            products.extend (_products)
        #self.__get_all_links (url)

        for p in products:
            logging.debug ("all product link = %s, seller = %s" % (p.link, p.seller))
        self.__products__ = products

    def __get_all_links (self, url):
        if self.html == None:
            self.html = get_content (url)
        #logging.debug ("html = %s" % self.html)

    def __get_products (self, url):
        logging.debug ("get_products url = %s" % url)
        html = get_content (url)
        #logging.debug ("html = %s" % html)
        if self.seller == None:
            m_link = re.findall ('<a class="item-name-anchor" href="(.*?)"', html)
        else:
            m_link = re.findall ('"(http://goods.ruten.com.tw/item/show?.*?)"', html)

        if m_link is None:
            return None

        m_name = re.findall ('<span class="item-name.*?>(.*?)<', html)
        if m_name is None:
            return None

        m_seller = re.findall ('"http://class.ruten.com.tw/user/index00.php\?s=(.*?)"', html)
        if m_seller is None:
            return None

        m_current_price = re.findall ('<span class="item-current_price-text".*?>(.*?)<', html)
        if m_current_price is None:
            return None

        logging.debug ("link length = %d, name length = %d, seller length = %d" % (len (m_link), len (m_name), len (m_seller)))

        products = []
        if len (m_link) == len (m_name) and len (m_link) == len (m_seller):
            for i in range (0, len (m_link)):
                product = BidProduct ()
                product.link = m_link[i]
                product.title = m_name[i]
                if self.seller == None:
                    product.seller = m_seller[i]
                else:
                    product.seller = self.seller
                products.append (product)
                i = i + 1

        for p in products:
            logging.debug ("link = %s, title = %s" % (p.link, p.title))
        return products

if __name__ == '__main__':
    print ("hello world\n")
    first_keyword = sys.argv[1]
    second_keyword = sys.argv[1]

    searcher = RutenSearcher (first_keyword)
    first_products = searcher.get_products()

    all_sellers = []
    for p in first_products:
        all_sellers.append (p.seller)
    all_sellers = set (all_sellers)

    for a in all_sellers:
        logging.debug ("seller = %s" % a)
        searcher_2 = RutenSearcher (second_keyword, a)

