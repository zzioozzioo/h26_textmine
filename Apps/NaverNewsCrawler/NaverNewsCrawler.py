# 네이버 API를 활용하여 뉴스 데이터를 크롤링하는 모듈

import os
import sys
import urllib.request
import json

CLIENT_ID = "hm09aj7HFDZ5INSt1yAo"
CLIENT_SECRET = "09aDjlENm9"

def crawlNaverNews(url, start=0, display=10):
    url += f'&start={start}&display={display}'

    # 이 부분을 반복 실행하지 않는 방법 찾아보기
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)

    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if rescode == 200:
            py_data = json.loads(response.read().decode('utf-8'))
            print(py_data['items'])
            return py_data
    except Exception as e:
        print("Error Code:" + rescode)
        return None
    #


def crawlNaverNewsAll(keyword, max_display=100):
    encText = urllib.parse.quote(keyword)
    url = "https://openapi.naver.com/v1/search/news?query=" + encText

    start = 1
    display = 10
    corpus = []
    
    while start <= max_display:
        crawled_news = crawlNaverNews(url, start, display)
        if crawled_news and 'items' in crawled_news:
            corpus += crawled_news['items']
            start += display
        else:
            break

    return corpus