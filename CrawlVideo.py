import requests
from bs4 import BeautifulSoup
import os
import lxml
import time

class ViedeoCrawler():
    def __init__(self):
        self.url = ""
        self.down_path = r"F:\VideoSpider\DOWN"
        self.final_path = r"F:\VideoSpider\FINAL"

    def run(self):
        print("Start!")
        start_time = time.time()
        os.chdir(self.down_path)
        html = requests.get(self.url).text
        bsObj = BeautifulSoup(html, 'lxml')
        duration = bsObj.find('meta', {'property': "video:duration"})['content'].replace("\"", "")
        limit = int(duration) // 10 + 2
        for i in range(1,limit):
            try:
                resp = requests.get(
                    " " % i)
            except:
                print('到达尽头，下载完成！')
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
        print("下载完成！总共耗时 %d s" % (time.time()-start_time))
        print("接下来进行合并……")
        os.system('copy/b %s\\*.ts %s\\new.ts' % (self.down_path,self.final_path))
        files = os.listdir(self.down_path)
        for filena in files:
            del_file = self.down_path + '\\' + filena
            os.remove(del_file)
        print("合并完成，请您欣赏！")

crawler = ViedeoCrawler()
crawler.run()
