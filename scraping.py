
# coding: utf-8

# In[ ]:


import lxml
from lxml import etree
import requests
import time
from time import sleep
import json


# In[64]:


def content(url, headers):
    try:
        r = requests.get(url=url, headers=headers)
    except requests.exceptions.ConnectionError:
        r.status_code = "Connection refused"
    html = r.text.encode('utf-8')
    result = etree.HTML(html)
#     time.sleep(1)
    return result


# In[4]:


headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
}
url='https://www.usnews.com/education/best-global-universities/search?region=&subject=&name='
result = content(url, headers)


# In[5]:


allPage = result.xpath('//div[@class="pagination"]//a[last()-1]')
sumPage = allPage[0].text


# In[6]:


subjects_list = []
select = result.xpath('//select[@name="subject"]')
allOptions = select[0].xpath('option')


# In[8]:


#删除没有的第一项
del allOptions[0]
for option in allOptions:
    subjects_list.append(option.text.strip().lower().replace(' and ','-').replace('/','-').replace(' ','-'))
pageSize = 0


# In[65]:


univ_details = []

# print etree.tostring(result, pretty_print=True)
allPage = result.xpath('//div[@class="pagination"]//a[last()-1]')
try:
    sumPage = allPage[0].text
except:
    pass

for a in range(int(sumPage)):
    url='https://www.usnews.com/education/best-global-universities/rankings?'+ '&page=' + str(a+1)
    result = content(url=url, headers=headers)

    #拿到学校名字
    schoolNames = result.xpath('//div[@class="block unwrap"]//h2//a')
    for s in schoolNames:
        univ_details.append({'name':s.text})
        print(etree.tostring(s))
    
    link_res = result.xpath('//div[@class="block unwrap"]//h2//a/@href')
        
    #设置索引
    pageSize = len(schoolNames)
    pageSize *= a
    # print schoolNames[0].text

    for i,link_l in enumerate(link_res):
        i = int(i)
        result = content(url=link_l, headers=headers)
        
        #大学内部两个大列表
        content_list1 = {}
        content_list2 = {}

        content1 = result.xpath('//div[@id="directoryPageSection-institution-data"]')
        if content1:
            content1_subDivs = content1[0].xpath('div')

            index = 0
            for subDIv in content1_subDivs:
                if index == 0:
                    content_list1[univ_details[i]['name']] = [dict(
                        value = subDIv.xpath('div')[0].text.strip(),    #数量
                        key   = subDIv.xpath('div')[1].text.strip()    #指标
                    )]
                    index += 1
                else:
                    content_list1[univ_details[i]['name']] += [dict(
                        value = subDIv.xpath('div')[0].text.strip(),    #数量
                        key = subDIv.xpath('div')[1].text.strip()    #指标
                    )]

        content2 = result.xpath('//div[@id="directoryPageSection-indicator-rankings"]')
        if content2:
            content2_subDivs = content2[0].xpath('div')
            #删除一个没有用的div
            del content2_subDivs[0]

            index = 0
            for subDIv in content2_subDivs:
                if index == 0:
                    content_list2[univ_details[i]['name']] = [dict(
                        value = subDIv.xpath('div')[0].text.strip(),    #数量
                        key   = subDIv.xpath('div')[1].text.strip()    #指标
                    )]
                    index += 1
                else:
                    content_list2[univ_details[i]['name']] += [dict(
                        key   = subDIv.xpath('div')[1].text.strip(),    #指标
                        value = subDIv.xpath('div/span/span')[0].text.strip().replace('#','')   #排名
                    )]
        univ_details[i + pageSize]['summary'] = content_list1
        univ_details[i + pageSize]['indicator'] = content_list2


# In[68]:


len(univ_details)


# In[46]:


global_rank = []

subjects_list[1] = 'arts-and-humanities'
for subject in subjects_list:
    print(subject)
    seq1 = []
    link_list = []
    
    url='https://www.usnews.com/education/best-global-universities/search?region=&subject=' + subject
    
    result = content(url=url, headers=headers)
    
    # print etree.tostring(result, pretty_print=True)
    allPage = result.xpath('//div[@class="pagination"]//a[last()-1]')
    try:
        sumPage = allPage[0].text
    except:
        pass
          
    for a in range(int(sumPage)):
        url='https://www.usnews.com/education/best-global-universities/search?subject=' + subject + '&page=' + str(a+1)
        result = content(url=url, headers=headers)
 
        #拿到学校名字
        schoolNames = result.xpath('//div[@class="block unwrap"]//h2//a')
        for s in schoolNames:
            seq1.append({'name':s.text})
            
        
        #设置索引
        pageSize = len(schoolNames)
        pageSize *= a
        # print schoolNames[0].text
 

        link_res = result.xpath('//div[@class="block unwrap"]//h2//a/@href')
        #拿到学校链接
#         for link_r in link_res:
#              link_list.append(link_r)
        for i, link_r in enumerate(link_res):
            seq1[i + pageSize]['link'] = link_r  
        
        #拿到排名
        rank_list = result.xpath('//div/span[@class="rankscore-bronze"]')
        for i,r in enumerate(rank_list):
            seq1[i + pageSize]['ranking'] = r.text.strip().replace('#','')
        # print rank_list[0].text.strip().replace('#','')
        
        #拿到国家，地区
        span = result.xpath('//div[@class="block unwrap"]//div[1]/span')
        for i in range(0,len(span),2):
            seq1[round(i/2) + pageSize]['country'] = span[i].text
            seq1[round(i/2) + pageSize]['area'] = span[i+1].text
 
     #print(len(seq1))
     #print(len(link_list))

    global_rank.append({
        'subject': subject,
        'rank': seq1})


# In[69]:


with open('global_univ_details.json', 'w') as outfile:
    json.dump(univ_details, outfile)

