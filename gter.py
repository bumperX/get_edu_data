
# coding: utf-8

# In[554]:


import lxml
from lxml import etree, html
import requests
import json
import time


# In[637]:


all_offer = {}


# In[654]:


for page in range(43,51):
    print('page: {}'.format(page))
    web_link = 'http://bbs.gter.net/forum.php?mod=forumdisplay&fid=49&filter=typeid&typeid=158&page={}'.format(page)
    web_resp = requests.get(web_link, allow_redirects = False)
    web_resp.encoding = 'gbk'
    web_tree = html.fromstring(web_resp.text)
    posts_ls = web_tree.xpath('//*[@id="forum_49"]/tbody/tr/td/em/a')
    posts = [a.attrib['href'] for a in posts_ls]
    
    usrs = {}
    for j in range(len(posts)):
        print(j)
        offer_resp = requests.get(posts[j], allow_redirects = True)
        time.sleep(1)
        offer_resp.encoding = 'gbk'
        offer_tree = html.fromstring(offer_resp.text)

    #     usr_name = offer_tree.xpath('//*[@id="postlist"]/div[1]/div[2]/div/table/tbody/tr[1]/td[1]/div/div/a/text()')[0]
        offer_tb = offer_tree.xpath('//*[@id="postlist"]/div[1]/div[2]/div[1]/table[1]/tr[1]/td[2]/div[2]/div/div/table')
        time.sleep(1)
        offer_details = {}
        usr_bg = {}
        offers = []

        for i in range(len(offer_tb)):
            attribs = offer_tb[i].attrib
            if 'summary' in attribs:
                summary = attribs['summary']

                if 'offer' in summary:
                    offer_item = offer_tb[i].xpath('.//tr//text()')
                    time.sleep(1)
                    offer_list = list(
                        filter(None, [item.strip().replace('\r\n', '').
                                      replace('                    ', '').
                                      replace('/', ',') 
                                      for item in offer_item 
                                      if item.strip() != '\r\n']
                              ))
    #                 print('offer_list: {}'.format(offer_list))

                    offer = {}
                    for x in range(0, len(offer_list), 2):
                        if x+1 < len(offer_list):
                            offer[offer_list[x]] = offer_list[x+1]

                if offer not in offers:
                    offers.append(offer)


                if '个人情况' in summary and usr_bg == {}:
                    offer_item = offer_tb[i].xpath('.//tr//text()')
                    time.sleep(1)
                    bg = list(
                        filter(None, [item.strip().replace('\r\n', '').
                                      replace('                    ', '').
                                      replace('/', ',') 
                                      for item in offer_item 
                                      if item.strip() != '\r\n']
                              ))

                    for y in range(0, len(bg), 2):
                        if y+1 < len(bg):
                            usr_bg[bg[y]] = bg[y+1]

    #     print('offers: {}'.format(offers)) 
        if len(usr_bg)!=0: offer_details['personal_info'] = usr_bg
        if len(offers)!=0: offer_details['offers'] = offers
        if len(offer_details)!=0: usrs[j] = offer_details
    if not usrs in all_offer.values(): all_offer[page] = usrs


