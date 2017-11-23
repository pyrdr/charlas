# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 22:31:38 2017

@author: juan9
"""

file_names = ['diario_libre_fb','fb_el_dia','fb_listin','fb_nacional','hoy_fb']
ids= ['DiarioLibre','eldia.com.do','listindiario','1385155231726142','periodicohoyRD']

import urllib.request as urllib2
import json
import datetime
import csv
import time
import pandas as pd


app_id = "175344463016958"
app_secret = "3ab6d67e8ab1f74095b8e4d9e1cff37e" # DO NOT SHARE WITH ANYONE!

access_token = app_id + "|" + app_secret

def request_until_succeed(url):
    req = urllib2.Request(url)
    success = False
    while success is False:
        try: 
            response = urllib2.urlopen(req)
            if response.getcode() == 200:
                success = True
        except:
            time.sleep(5)
            
            print ("Error for URL %s: %s" % (url, datetime.datetime.now()))

    return response.read()

def testFacebookPageFeedData(page_id, access_token,links = False):
    
    # construct the URL string
    base = "https://graph.facebook.com/v2.10"
    node = "/" + page_id + "/feed" # changed
    if links:
        parameters = "/?fields=message,link,created_time,reactions.type(LOVE).limit(0).summary(total_count).as(reactions_love),reactions.type(WOW).limit(0).summary(total_count).as(reactions_wow),reactions.type(HAHA).limit(0).summary(total_count).as(reactions_haha),reactions.type(ANGRY).limit(0).summary(total_count).as(reactions_angry),reactions.type(SAD).limit(0).summary(total_count).as(reactions_sad),reactions.type(LIKE).limit(0).summary(total_count).as(reactions_like)&limit={}&access_token={}".format(100, access_token) # changed
    else:
        parameters = "/?fields=message,created_time,reactions.type(LOVE).limit(0).summary(total_count).as(reactions_love),reactions.type(WOW).limit(0).summary(total_count).as(reactions_wow),reactions.type(HAHA).limit(0).summary(total_count).as(reactions_haha),reactions.type(ANGRY).limit(0).summary(total_count).as(reactions_angry),reactions.type(SAD).limit(0).summary(total_count).as(reactions_sad),reactions.type(LIKE).limit(0).summary(total_count).as(reactions_like)&limit={}&access_token={}".format(100, access_token) # changed
   
    url = base + node + parameters
    
    # retrieve data
    data = json.loads(request_until_succeed(url))
    
    return data
    
def Get_News(page_id,limit = 10,link = False):
    result = {}
    nex = None
    for  i in range(limit):
        range_dates = []
        range_messages = []
        range_angry = []
        range_haha = []
        range_like = []
        range_love = []
        range_sad = []
        range_wow = []
        range_ids=  []
        if i == 0:
            data = testFacebookPageFeedData(page_id,access_token,link)
            nex = data['paging']['next']
            for d in data['data']:
                range_dates.append(d['created_time'])
                if link and 'message' in d:
                        if 'http'  in d['message']:
                            range_messages.append(d['message'])
                        else:
                            range_messages.append(d['link'])
                elif link and 'message' not in d:
                        range_messages.append(d['link'])
                else:
                    try:
                        range_messages.append(d['message'])
                    except:
                        range_messages.append(' ')
                range_angry.append(d['reactions_angry']['summary']['total_count'])
                range_haha.append(d['reactions_haha']['summary']['total_count'])
                range_like.append(d['reactions_like']['summary']['total_count'])
                range_love.append(d['reactions_love']['summary']['total_count'])
                range_sad.append(d['reactions_sad']['summary']['total_count'])
                range_wow.append(d['reactions_wow']['summary']['total_count'])
                range_ids.append(d['id'])
            result['dates'] = range_dates
            result['messages'] = range_messages
            result['angry'] = range_angry
            result['haha'] = range_haha
            result['like'] = range_like
            result['love'] = range_love
            result['sad'] = range_sad
            result['wow'] = range_wow
            result['id'] = range_ids
        
        else:
            data = json.loads(request_until_succeed(nex))
            try:
                nex = data['paging']['next']
            except:
                break
            for d in data['data']:
                try:
                    if link and 'message' in d:
                        if 'http'  in d['message']:
                            range_messages.append(d['message'])
                        else:
                            range_messages.append(d['link'])
                    elif link and 'message' not in d:
                        range_messages.append(d['link'])
                    else:
                        range_messages.append(d['message'])
                    range_dates.append(d['created_time'])
                    range_angry.append(d['reactions_angry']['summary']['total_count'])
                    range_haha.append(d['reactions_haha']['summary']['total_count'])
                    range_like.append(d['reactions_like']['summary']['total_count'])
                    range_love.append(d['reactions_love']['summary']['total_count'])
                    range_sad.append(d['reactions_sad']['summary']['total_count'])
                    range_wow.append(d['reactions_wow']['summary']['total_count'])
                    range_ids.append(d['id'])
                    
                except:
                    print(d)
            result['dates'].extend(range_dates)
            result['messages'].extend(range_messages)
            result['angry'].extend(range_angry)
            result['haha'].extend(range_haha)
            result['like'].extend(range_like)
            result['love'].extend(range_love)
            result['sad'].extend(range_sad)
            result['wow'].extend(range_wow)
            result['id'].extend(range_ids)
            
    
    result_df = pd.DataFrame(result)
    return result_df

import re
def get_url(url):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)
    try:
        result =   urls[0]
    except:
        result = 'Not found'
    return result


def Save_News():
    for i in range(len(ids)):
        if i == 4:
            #Caso periodico HOY
            news = Get_News(ids[i],1000,True)
        else:
            news = Get_News(ids[i],1000)
            
        news.dates=pd.to_datetime(news.dates)
        news['month'] = news.dates.dt.month
        news['year'] = news.dates.dt.year
        valid_news = news.loc[((news.messages.str.contains('http')) | (news.messages.str.contains('ht'))) & (~news.messages.str.contains('twitter.com'))]
        valid_news['url'] = valid_news.messages.apply(get_url)
        final_news = valid_news.loc[(valid_news.url != 'Not found') & (~valid_news.url.str.contains('facebook.com'))]
        final_news.to_csv(file_names[i] + '.csv',index = False)

Save_News()
