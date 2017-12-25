# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import os
import lxml
import time
import random
import re
import m3u8

class ViedeoCrawler():
    def __init__(self):
        self.url = ""
        self.down_path = r"F:\Spider\VideoSpider\DOWN"
        self.final_path = r"F:\Spider\VideoSpider\FINAL"
        try:
            self.name = re.findall(r'/[A-Za-z]*-[0-9]*',self.url)[0][1:]
        except:
            self.name = "uncensord"
        self.headers = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent':'Mozilla/5.0 (Linux; U; Android 6.0; zh-CN; MZ-m2 note Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/40.0.2214.89 MZBrowser/6.5.506 UWS/2.10.1.22 Mobile Safari/537.36'
        }

    def get_ip_list(self):
        print("正在获取代理列表...")
        url = 'http://www.xicidaili.com/nn/'
        html = requests.get(url=url, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        ips = soup.find(id='ip_list').find_all('tr')
        ip_list = []
        for i in range(1, len(ips)):
            ip_info = ips[i]
            tds = ip_info.find_all('td')
            ip_list.append(tds[1].text + ':' + tds[2].text)
        print("代理列表抓取成功.")
        return ip_list

    def get_random_ip(self,ip_list):
        print("正在设置随机代理...")
        proxy_list = []
        for ip in ip_list:
            proxy_list.append('http://' + ip)
        proxy_ip = random.choice(proxy_list)
        proxies = {'http': proxy_ip}
        print("代理设置成功.")
        return proxies

    def get_uri_from_m3u8(self,realAdr):
        print("正在解析真实下载地址...")
        with open('temp.m3u8', 'wb') as file:
            file.write(requests.get(realAdr).content)
        m3u8Obj = m3u8.load('temp.m3u8')
        print("解析完成.")
        return m3u8Obj.segments

    def run(self):
        print("Start!")
        start_time = time.time()
        os.chdir(self.down_path)
        html = requests.get(self.url).text
        bsObj = BeautifulSoup(html, 'lxml')
        realAdr = bsObj.find(id="video-player").find("source")['src']

        # duration = bsObj.find('meta', {'property': "video:duration"})['content'].replace("\"", "")
        # limit = int(duration) // 10 + 3

        ip_list = self.get_ip_list()
        proxies = self.get_random_ip(ip_list)
        uriList = self.get_uri_from_m3u8(realAdr)
        i = 1   # count
        for key in uriList:
            if i%50==0:
                print("休眠10s")
                time.sleep(10)
            if i%120==0:
                print("更换代理IP")
                proxies = self.get_random_ip(ip_list)
            try:
                resp = requests.get(key.uri, headers = self.headers, proxies=proxies)
            except Exception as e:
                print(e)
                return
            if i < 10:
                name = ('clip00%d.ts' % i)
            elif i > 100:
                name = ('clip%d.ts' % i)
            else:
                name = ('clip0%d.ts' % i)
            with open(name,'wb') as f:
                f.write(resp.content)
                print('正在下载clip%d' % i)
            i = i+1
        print("下载完成！总共耗时 %d s" % (time.time()-start_time))
        print("接下来进行合并……")
        os.system('copy/b %s\\*.ts %s\\%s.ts' % (self.down_path,self.final_path, self.name))
        print("合并完成，请您欣赏！")
        y = input("请检查文件完整性，并确认是否要删除碎片源文件？(y/n)")
        if y=='y':
            files = os.listdir(self.down_path)
            for filena in files:
                del_file = self.down_path + '\\' + filena
                os.remove(del_file)
            print("碎片文件已经删除完成")
        else:
            print("不删除，程序结束。")

if __name__=='__main__':
    crawler = ViedeoCrawler()
    crawler.run()
