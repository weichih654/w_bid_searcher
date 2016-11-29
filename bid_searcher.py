#!/usr/bin/env python
import urllib2
import urllib
import re
import time
import logging
import sys
import Queue, time, threading, datetime

log = logging.getLogger ('bid')
#hdlr = logging.StreamHandler ()
log.setLevel (logging.DEBUG)
#log.addHandler (hdlr)

def get_content (url):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive',
       'Cookie': '_ts_id=340332053300390D3F0C; __gads=ID=75750d9ee6008bb4:T=1480304149:S=ALNI_MY6y901-6hRseczneJINR3Z2Ua5kA; __asc=d42340e6158a900c01d4c91956d; __auc=d42340e6158a900c01d4c91956d; _ga=GA1.3.1813721420.1480304149'}
    request=urllib2.Request(url,None,headers = hdr)
    try:
        response = urllib2.urlopen(request)
        data = response.read()

        html = data
    except:
        log.error ("get_content urlopen fail")
    return html

class BidProduct:
    def __init__ (self):
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
        self.__products__ = []

    def __get_all_links (self, url):
        pass

    def __get_products (self, url):
        pass

    def get_products (self):
        return self.__products__

    def get_sellers (self):
        pass

class YahooSearcher(BidSearcher):
    def __init__ (self, keyword, seller = None):
        BidSearcher (keyword, seller)

    def __get_all_links (self, url):
        pass

    def __get_products (self, url):
        pass

class RutenSearcher(BidSearcher):
    def __init__ (self, keyword, seller = None):
        BidSearcher (keyword, seller)
        self.html = None
        self.max_page = 5
        self.seller = seller
        self.__sellers__ = []

        if self.seller is None:
            main_url = "http://search.ruten.com.tw/search/s000.php?enc=u&searchfrom=searchf&t=0&k="
        else:
            main_url = "http://search.ruten.com.tw/search/ulist00.php?s=" + seller + "&enc=b&c=0&k="
            keyword = urllib.quote_plus(keyword.decode ('utf-8').encode ('big5').replace('+', ' '))

        url = main_url + keyword
        log.debug ("url = %s" % url)
        products = []
        for i in range (0, self.max_page):
            if self.seller is None:
                i = i + 1
            _url = ("%s&p=%d" % (url, i))
            _products = self.__get_products (_url)
            if _products is None:
                break;
            products.extend (_products)
            if self.seller is not None:
                break;
        #self.__get_all_links (url)

        #for p in products:
        #    log.debug ("all product link = %s, seller = %s" % (p.link, p.seller))
        self.__products__ = products

    def __get_all_links (self, url):
        if self.html == None:
            self.html = get_content (url)
        #log.debug ("html = %s" % self.html)

    def __get_products (self, url):
        log.debug ("get_products url = %s" % url)
        html = get_content (url)
        #log.debug ("html = %s" % html)
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
            log.debug ("link is empty")
            #log.debug ("html = " + html)
            #return None

        log.debug ("link length = %d, name length = %d, seller length = %d" % (len (m_link), len (m_name), len (m_seller)))

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
            log.debug ("link = %s, title = %s" % (p.link, p.title))
        return products

    def get_sellers (self):
        if len (self.__products__) == 0:
            return []
        all_sellers = []
        for p in self.__products__:
            all_sellers.append (p.seller)
        self.__sellers__ = all_sellers
        return set (self.__sellers__)

def doJob(*args):
    log.debug ("doJob")
    queue = args[0]
    while queue.qsize() > 0:
        job = queue.get()
        args[1][job.seller] = job.do()

class Job:
    def __init__ (self, seller, keyword):
        self.seller = seller
        self.keyword = keyword

    def do (self):
        log.debug ("Job do")
        _s = RutenSearcher (self.keyword, self.seller)
        _p = _s.get_products ()
        log.debug ("Job done, seller = %s, keyword = %s, products count = %d" % (self.seller, self.keyword, len (_p)))
        return _p

def search_seller_by_all_keywords (searchers):
    # Implement two searcher now
    if len (searchers) != 2:
        return None
    s1 = RutenSearcher (searchers[0])
    s2 = RutenSearcher (searchers[1])
    p1 = s1.get_products ()
    p2 = s2.get_products ()
    log.debug ("p1 have %d products" % len (p1))
    log.debug ("p2 have %d products" % len (p2))

    hs1 = None
    hs2 = None
    if len (p1) < len (p2):
        hs1 = s1
        hs2 = s2
        k1 = searchers[0]
        k2 = searchers[1]
    else:
        hs1 = s2
        hs2 = s1
        k1 = searchers[1]
        k2 = searchers[0]

    sellers = hs1.get_sellers ()
    sellers_count = len (sellers)

    all_products = {}
    for s in sellers:
        all_products[s] = None

    que = Queue.Queue()
    for s in sellers:
        que.put(Job(s, k2))

    log.debug ("create Thd1")
    thd1 = threading.Thread(target=doJob, name='Thd1', args=(que,all_products))
    thd2 = threading.Thread(target=doJob, name='Thd2', args=(que,all_products))
    thd3 = threading.Thread(target=doJob, name='Thd3', args=(que,all_products))
    thd4 = threading.Thread(target=doJob, name='Thd4', args=(que,all_products))
    thd5 = threading.Thread(target=doJob, name='Thd5', args=(que,all_products))
    thd1.start()
    thd2.start()
    thd3.start()
    thd4.start()
    thd5.start()

    all_finish = False
    while all_finish is False:
        all_finish = True
        for p in all_products:
            if all_products[p] is None:
                all_finish = False
                break
        time.sleep (1)

    _sellers = []
    for p in all_products:
        log.debug ("seller = %s, product count = %d" % (p, len (all_products[p]) if all_products[p] is not None else 0))
        if len (all_products[p]) != 0:
            _sellers.append (p)
    return _sellers

    #for s in sellers:
    #    log.debug ("[%s]" % s)
    #    _s = RutenSearcher (k2, s)
    #    _p = _s.get_products ()
    #    log.debug ("get %d products in second search" % len (_p))



if __name__ == '__main__':
    print ("hello world\n")
    first_keyword = sys.argv[1]
    second_keyword = sys.argv[2]

    search_seller_by_all_keywords ([first_keyword, second_keyword])

