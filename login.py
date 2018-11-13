import requests
from lxml import etree
import os
from PIL import Image
import matplotlib.pyplot as plt


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
        self.cookie = 'AntiLeech=2676002516; ASP.NET_SessionId=fMJw1iyVvE1wK4fCasJXsTVj4hJ233tBpe-vyUTQYgk5Dnpg0kE*'

    def login_cookie(self):
        self.headers['Cookie'] = self.cookie
        response = self.s.get(self.indexurl, headers=self.headers)

        print("Login By Cookie")
        if login_status(response):
            return True
        else:
            del self.headers['Cookie']
            return False

    def login_manual(self):
        # 访问首页
        response = self.s.get(self.indexurl, headers=self.headers)

        # 用Lxml库解析网页，通过Xpath语法定位__VIEWSTATE
        selector = etree.HTML(response.content)
        __VIEWSTATE = selector.xpath('//*[@id="form1"]/input/@value')[0]
        img_dir = self.down_code()
        code = input_code(img_dir)

        # POST数据发送
        self.data['__VIEWSTATE'] = __VIEWSTATE
        self.data['txtSecretCode'] = code
        # print(self.data)
        # print(self.headers)
        response = self.s.post(self.indexurl, headers=self.headers, data=self.data)

        print("Login By Manual")
        if login_status(response):
            # 这里的Cookie只能获取到ASP.NET_SessionId，无法获取到AntiLeech，导致了Cookie登录失败，后期尝试selenium获取
            # self.cookie = 'ASP.NET_SessionId' +\
            #               requests.utils.dict_from_cookiejar(self.s.cookies)['ASP.NET_SessionId']
            return True
        else:
            return False

    def down_code(self):
        # 获取验证码并下载(通过抓包，可以看到请求链接，并且没刷新一次二维码，后面就多一个？)
        image_response = self.s.get(self.imgUrl, stream=True)
        image = image_response.content
        img_dir = os.getcwd() + "/"
        print("Saved in " + img_dir + "code.gif")
        try:
            with open(img_dir + "code.gif", "wb") as codegif:
                codegif.write(image)
            codegif.close()
        except IOError:
            print("IO ERROR!")
        finally:
            return img_dir


def input_code(img_dir):
    # 手动输入验证码
    image = Image.open(img_dir + "code.gif")
    plt.figure("CODE")
    plt.imshow(image)
    plt.show()
    code = input("The code is:")
    return code


def login_status(response):
    if response.status_code == requests.codes.ok:
        selector = etree.HTML(response.content)
        state = selector.xpath('/html/head/title/text()')[0]
        # print(state)
        if state == "正方教务管理系统":
            print("登录成功")
            return True
        elif state == "欢迎使用正方教务管理系统！请登录":
            print("登录失败")
            return False
    else:
        print(response.status_code)
        print("登录失败")
        return False


if __name__ == "__main__":
    number = input("Your number:")
    password = input("Your password:")
    spider = Login(number, password)

    # spider.login_manual()
    spider.login_cookie()
