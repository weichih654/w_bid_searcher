#!/usr/bin/env python
import urllib2
import re
import time
import logging
import sys

logging.basicConfig (level=logging.DEBUG, filename="log")

def get_content (url):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive',
       'Cookie': '_ts_id=3407350C3D053D053C0A; user_credit=45; good_credit=52; member=UrBHCGdZWdHjmvwkJuEVWHI6hNyx0C7IEFFlQ5c1mORT5KGB2qc6BDWmVkCXKqB1QoeJLv%2FOlJDeyq8sfKjPPLSFmdO7J%2Bbhm6aD%2FDk4VHfQNqDYiHNswgLh6da0gRE0fKU8%2Fv3DOlvnijIS%2FrRHvRS2g5t8pfUbZUWu2hlKUwBtmTA7IXHX80vL4%2FFGdXwtKIph%2BpecWjddb4cgv%2BqQ7XYyXsz30j%2BvTRxX%2BN%2B6S1MIu5imKwWYRFanmyvUByw%3D; bid_rid=5761590; bid_nick=5796c677; login=1; last_login_status=20161123103256+s+TW; login_status_code=1; rt_header_info=eyJ1c2VyX25pY2siOiJ3bGl1IiwiZ29vZF9jcmVkaXQiOjUyLCJsYXN0X2xvZ2luX3RpbWUiOjE0Nzk4NjgzNzYsImxhc3RfbG9naW5fY2hlY2siOnRydWV9; __asc=2f2fe5141589a01ff27709d2dd8; __auc=25f750cc15355afe2364d51e36d; _ga=GA1.3.213042389.1457431503'}
    request=urllib2.Request(url,None,headers = hdr)
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

        if self.seller is None:
            main_url = "http://search.ruten.com.tw/search/s000.php?enc=u&searchfrom=searchf&t=0&k="
        else:
            main_url = "http://search.ruten.com.tw/search/ulist00.php?s=" + seller + "&enc=b&c=0&k="
            keyword = keyword.decode ('utf-8').encode ('big5')

        url = main_url + keyword
        logging.debug ("url = %s" % url)
        products = []
        for i in range (0, self.max_page):
            if self.seller is None:
                i = i + 1
            _url = ("%s&p=%d" % (url, i))
            _products = self.__get_products (_url)
            if _products is None:
                break;
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
            m_link = re.findall ('"(http://goods.ruten.com.tw/item/show?.*?)" class="item-url"', html)

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

        if len (m_link) == 0:
            logging.debug ("link is empty")
            #logging.debug ("html = " + html)
            #return None

        logging.debug ("link length = %d, name length = %d, seller length = %d" % (len (m_link), len (m_name), len (m_seller)))

        products = []
        if len (m_link) == len (m_name) and \
            (self.seller is not None or \
                    self.seller is None and len (m_link) == len (m_seller)):
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
    second_keyword = sys.argv[2]

    searcher = RutenSearcher (first_keyword)
    first_products = searcher.get_products()

    all_sellers = []
    for p in first_products:
        all_sellers.append (p.seller)
    all_sellers = set (all_sellers)

    for a in all_sellers:
        logging.info ("seller = %s" % a)
        print ("seller = %s" % a)
        searcher_2 = RutenSearcher (second_keyword, a)
        products_2 = searcher_2.get_products ()
        for s2 in products_2:
            logging.info ("link = %s, title = %s, seller = %s", s2.link, s2.title, s2.seller)
            print ("link = %s, title = %s, seller = %s, store = %s%s" % (s2.link, s2.title.decode ('big5').encode ('utf-8'), s2.seller, 'http://search.ruten.com.tw/search/ulist00.php?s=', s2.seller))

