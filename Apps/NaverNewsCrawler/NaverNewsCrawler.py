import os
import sys
import urllib.request
import json

def crawlNaverNews(url, start=0, display=10):

    client_id = "hm09aj7HFDZ5INSt1yAo"
    client_secret = "09aDjlENm9"

    url += f'&start={start}&display={display}'

    # 이 부분을 반복 실행하지 않는 방법 찾아보기
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    #
    if(rescode==200):
        response_body = response.read() # json 객체 -> item 객체만 가져와서 value로 바꾸면 됨
        json_string = response_body.decode('utf-8')
        py_data = json.loads(json_string)
        news_data = py_data['items']
        print(news_data)
        return news_data
    else:
        print("Error Code:" + rescode)


def crawlNaverNewsAll(keyword):
    encText = urllib.parse.quote(keyword)

    start = 1
    display = 10

    url = "https://openapi.naver.com/v1/search/blog?query=" + encText

    corpus = []
    while start <= 100:
        crawled_news = crawlNaverNews(url, start, display)
        if crawled_news:
            corpus += crawled_news
            start += display
        else:
            break

    return corpus