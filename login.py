import requests
from lxml import etree
import os
from PIL import Image
import matplotlib.pyplot as plt
# from http import cookiejar


class Login:
    def __init__(self, number, password):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/70.0.3538.77 Safari/537.36 '
        }
        self.data = {
            '__VIEWSTATE': '',
            'txtUserName': number,
            'Textbox1': '',
            'TextBox2': password,
            'txtSecretCode': '',
            'RadioButtonList1': '%D1%A7%C9%FA',
            'Button1': '',
            'lbLanguage': '',
            'hidPdrs': '',
            'hidsc': ''
        }
        self.indexurl = 'http://xk.zucc.edu.cn/default2.aspx'
        self.imgUrl = 'http://xk.zucc.edu.cn/CheckCode.aspx?'
        self.s = requests.session()
        self.cookie = 'ASP.NET_SessionId=MzS1OBoWx_LMLXqUl3uzb4vjqVbAeqCcby3nnh40Vyil1UKZDtE*; AntiLeech=2681179348'

    def loginCookie(self):
        self.headers['Cookie'] = self.cookie
        response = self.s.get(self.indexurl, headers=self.headers)
        if response.status_code == requests.codes.ok:
            if loginstate(response):
                print("Login By Cookie")
                print(response.text)
                return True
            else:
                print("Cookie is invalid")
                return False
        else:
            print(response.status_code)
            del self.headers['Cookie']
            return False

    def loginManual(self):
        # 访问首页
        response = self.s.get(self.indexurl, headers=self.headers)

        # 用Lxml库解析网页，通过Xpath语法定位__VIEWSTATE
        selector = etree.HTML(response.content)
        __VIEWSTATE = selector.xpath('//*[@id="form1"]/input/@value')[0]

        # 获取验证码并下载(通过抓包，可以看到请求链接，并且没刷新一次二维码，后面就多一个？)
        imageResponese = self.s.get(self.imgUrl, stream=True)
        image = imageResponese.content
        imgDir = os.getcwd() + "/"
        print("Saved in " + imgDir + "code.gif")
        try:
            with open(imgDir + "code.gif", "wb") as codegif:
                codegif.write(image)
            codegif.close()
        except IOError:
            print("IO ERROR!")

        # 手动输入验证码
        image = Image.open(imgDir + "code.gif")
        plt.figure("CODE")
        plt.imshow(image)
        plt.show()
        code = input("The code is:")

        # POST数据发送
        self.data['__VIEWSTATE'] = __VIEWSTATE
        self.data['txtSecretCode'] = code
        # print(self.data)
        # print(self.headers)

        response = self.s.post(self.indexurl, headers=self.headers, data=self.data)

        if response.status_code == requests.codes.ok:
            if loginstate(response):
                self.cookie = 'ASP.NET_SessionId' +\
                              requests.utils.dict_from_cookiejar(self.s.cookies)['ASP.NET_SessionId']
                print("Login By Manual")
                # print(response.text)
                return True
            else:
                print("Bad Code!")
                return False
        else:
            print(response.status_code)
            return False


def loginstate(response):
    selector = etree.HTML(response.content)
    state = selector.xpath('/html/head/title/text()')[0]
    # print(state)
    if state == "正方教务管理系统":
        print("登录成功")
        return True
    elif state == "欢迎使用正方教务管理系统！请登录":
        print("登录失败")
        return False


if __name__ == "__main__":
    number = input("Your number:")
    password = input("Your password:")
    spider = Login(number, password)

    spider.loginManual()
    spider.loginCookie()
    # for i in range(1, 20):
    #     print(i)
    #     if spider.loginCookie():
    #         continue
    #     else:
    #         spider.loginManual()
