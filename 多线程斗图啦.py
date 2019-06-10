import requests
from lxml import etree
import re
import time
from urllib import request
import os
import threading
from queue import Queue
class Productor(threading.Thread):
    HEADERS ={
        'Referer':"http://www.doutula.com/",
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }
    def __init__(self,page_queue,image_queue):
        super(Productor,self) .__init__()
        self.page_queue = page_queue
        self.image_ueue = image_queue
    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()
            self.parse_url(url)
    def parse_url(self,url):
        response = requests.get(url, headers=self.HEADERS)
        html = etree.HTML(response.text)
        imgs = html.xpath(
            '//div[@class="col-sm-9 center-wrap"]/a/div[@class="random_article"]/div/img[@referrerpolicy="no-referrer"]')
        for img in imgs:
            img_url = img.get('data-original')
            alt = img.get('alt')
            alt = re.sub(r'[\?，。\.!]', '', alt)
            suffix = os.path.splitext(img_url)[1]
            filename = alt + suffix
            self.image_ueue.put((img_url,filename))
class Consumer(threading.Thread):
    def __init__(self,page_queue,image_queue):
        super(Consumer,self) .__init__()
        self.page_queue = page_queue
        self.image_ueue = image_queue
    def run(self):
        while True:
            if self.image_ueue.empty() and self.page_queue.empty():
                break
            img_url,filename = self.image_ueue.get()
            request.urlretrieve(img_url, '图片/' + filename)
            print(filename +'下载完成')
def main():
    page_queue = Queue(10)
    image_queue = Queue(100)
    for x in range(1,10):
        url = 'https://www.doutula.com/article/list/?page=%d'%x
        page_queue.put(url)
    for x in range(5):
        t = Productor(page_queue,image_queue)
        t.start()
    for x in range(5):
        t = Consumer(page_queue,image_queue)
        t.start()
if __name__ == '__main__':
    main()