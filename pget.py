# -*- coding: utf-8 -*-
from urllib.parse import urlparse
from urllib.parse import unquote
import http.client
import os
import sys
class DownloadSession:
    locExt = ".pgetpoz"
    tmpExt = ".pgettmp"
    fileName = ""
    poz = "0"
    buffsize = 1024
    fileSize = 0
    def load(self):
        while os.path.exists(self.fileName):
            basename = ".".join(self.fileName.split(".")[:-1])
            extname = self.fileName.split(".")[-1]
            self.fileName = basename+"#."+extname
        if os.path.exists(self.fileName+self.locExt) and os.path.exists(self.fileName+self.tmpExt):
            try:
                logfile = open(self.fileName+self.locExt,'r')
                a = logfile.read()
                logfile.close()
                print("读取到上次未完成进度"+a+"字节")
                self.poz = a
            except Exception as e:
                self.poz = "0"
        else:
            return "0"
    def conn(self,object):
        try:
            httpClient = None
            filename = self.fileName
            point = int(self.poz)
            if object.scheme=="http":
                httpClient = http.client.HTTPConnection(object.netloc, timeout=3000)
            else:
                httpClient = http.client.HTTPSConnection(object.netloc, timeout=3000)
            header = {
            "user-agent": "mozilla/4.0 (compatible; msie 5.01; windows nt 5.0)connection: keep-alive",
            "Range": "bytes="+str(point)+"-"
            }
            con = httpClient.request('GET', object.path+"?"+object.query,headers = header)
            fileContext = None
            #response是HTTPResponse对象
            response = httpClient.getresponse()
            if response.status>=200 and response.status <300:
                length = int(response.getheader("Content-Length"))
                self.fileSize = length
                print ("获取到文件大小:"+str(length/self.buffsize)+"KB")
                file = open(filename+self.tmpExt,'ab')
                logfile = open(filename+self.locExt,'w')
                print("正在下载"+filename)
                bufferLength = self.buffsize
                i=0;
                while True :
                    fileContext = response.read(bufferLength)
                    i+=1
                    percent = int((point+i*self.buffsize)*100/(point+length)*100)/100
                    sys.stdout.write("[%s] %.2f%%\r" % (('%%-%ds' % 50) % (int(percent * 50 / 100) * '-'), percent))
                    # print("已下载"+str(percent)+"%",end="\r")
                    if len(fileContext)==0:
                        file.close()
                        os.rename(filename+self.tmpExt,filename)
                        os.remove(filename+self.locExt)
                        print("\n")
                        print("下载完成")
                        break
                    file.write(fileContext)
                    logfile.seek(0,0)
                    logfile.write(str(file.tell()))
            elif response.status==301 or response.status==302:
                    url= response.getheader("Location")
                    print("获得远程地址:"+url)
                    self.conn(urlparse(url))
                    pass
            else:
                    print (str(response.status)+" : "+response.reason)
                    print(response.read().decode())
        except Exception as e:
            print(e)
        finally:
            if httpClient:
                httpClient.close()
if __name__ =="__main__":
    try:
        url = ""
        session = DownloadSession()
        args = sys.argv
        if len(args)>=2:
            url=args[1]
            print ("下载地址:"+args[1])
        else:
            while(url==""):
                url = input("下载地址:")
        a = urlparse(url.strip())
        session.fileName = unquote(a.path.split("/")[-1])
        session.load()
        session.conn(a)
    except KeyboardInterrupt as  e:
        print("\n")
        print ("下载停止")
