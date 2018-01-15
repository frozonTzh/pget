from urllib.parse import urlparse
from urllib.parse import unquote
import http.client
import os
import sys

locExt = ".pgetoffset"
tmpExt = ".pgettmp"
buffsize = 0x10000
class DownLoadSession():
    length = ""
    def __init__(self,urlstr):
        self.urlstr = urlstr;
        self.getLength()
        self.getFileName()
        self.load()
        self.conn()
        pass

    def getFileName(self):
        fileName = unquote(self.url.path.split("/")[-1])
        while os.path.exists(fileName):
            basename = ".".join(fileName.split(".")[:-1])
            extname = fileName.split(".")[-1]
            fileName = basename+"#."+extname
        print("获得文件名称%s"%fileName)
        self.fileName = fileName
    def getDist(self):
        url  = urlparse(self.urlstr.strip())
        try:
            httpClient = None
            if url.scheme=="http":
                httpClient = http.client.HTTPConnection(url.netloc, timeout=3000)
            else:
                httpClient = http.client.HTTPSConnection(url.netloc, timeout=3000)
            con = httpClient.request('HEAD', url.path+"?"+url.query)
            response = httpClient.getresponse()
            if response.status>=200 and response.status <300:
                try:
                    length  = int(response.getheader("Content-Length"))
                    print("获得文件大小%s"%length)
                except Exception as e:
                    length = 0
                    print("获得文件大小失败%s"%str(e))
                self.length = length
                self.url = url
                pass
            elif response.status==301 or response.status==302:
                url= response.getheader("Location")
                print("解析到地址%s"%url)
                self.urlstr = url
                pass
            else:
                print (str(response.status)+" : "+response.reason)
                print(response.read().decode())
                pass
            pass
        except Exception as e:
            print(e)
            pass
        finally:
            if httpClient:
                httpClient.close()
                pass
            pass
        pass
    def getLength(self):
        length = 0;
        while True:
            self.getDist()
            if self.length:
                break
    def load(self):
        fileName = self.fileName
        if os.path.exists(fileName+locExt) and os.path.exists(fileName+tmpExt):
            with open(fileName+locExt,'r') as logfile:
                offset = logfile.read()
                print("读取到上次未完成进度"+offset+"字节")
                if offset == "":
                    self.offset = "0"
                else:
                    self.offset =  offset
        else:
            self.offset = "0"
    def save(self,offset):
        fileName = self.fileName
        with open(fileName+locExt,'w') as logfile:
            logfile.truncate()
            logfile.seek(0)
            logfile.write(str(offset))
    def draw(self,offset):
        length = self.length
        percent = int((offset)*100/(length)*100)/100
        # print("已下载"+str(percent)+"%",end="\r")
        sys.stdout.write("[%s] %.2f%%\r" % (('%%-%ds' % 50) % (int(percent * 50 / 100) * '-'), percent))
    def conn(self):
        # try:
            fileName = self.fileName
            url = self.url
            length = self.length
            start = self.offset
            end = ""
            httpClient = None
            point = int(start)
            if url.scheme=="http":
                httpClient = http.client.HTTPConnection(url.netloc, timeout=3000)
            else:
                httpClient = http.client.HTTPSConnection(url.netloc, timeout=3000)
            headers = {
                "user-agent": "mozilla/4.0 (compatible; msie 5.01; windows nt 5.0)connection: keep-alive",
                "Range": "bytes=%s-%s"%(start,end)
            }
            con = httpClient.request('GET', url.path+"?"+url.query,headers = headers)
            fileContext = None
            #response是HTTPResponse对象
            response = httpClient.getresponse()
            if response.status>=200 and response.status <300:
                try:
                    length = int(response.getheader("Content-Length"))
                except Exception as e:
                    length = 0
                if length!=self.length:
                    #print(length)
                    self.length = length
                    pass
                with open(fileName+tmpExt,'ab') as file:
                    print("正在下载"+fileName)
                    i=0;
                    currentPoz = start
                    while True :
                        fileContext = response.read(buffsize)
                        currentPoz = file.tell()
                        i+=1
                        if len(fileContext)==0:
                            break
                        file.write(fileContext)
                        if self.length != 0:
                            self.save(currentPoz)
                            self.draw(currentPoz)
                        pass
                    pass
                pass
                os.rename(fileName+tmpExt,fileName)
                os.remove(fileName+locExt)
                print("%s"%(100*" "))
                print("下载完成")
        # except Exception as e:
        #     print(e)
        #     pass
        # finally:
        #     if httpClient:
        #         httpClient.close()
        #         pass
        #     pass
        # pass
if __name__ =="__main__":
    try:
        url = ""
        args = sys.argv
        if len(args)>=2:
            url=args[1]
            print ("下载地址:"+args[1])
        else:
            while(url==""):
                url = input("下载地址:")
                pass
        session = DownLoadSession(url);
        pass
    except KeyboardInterrupt as  e:
        print("\n")
        print ("下载停止")
        pass
    pass
pass
