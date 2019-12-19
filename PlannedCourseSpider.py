import time
import Login as Lg
from lxml import etree
import Lesson
import re


def get_all_lesson(selector):
    lesson_list = []
    lessons_tag_list = selector.xpath('//table[@id="kcmcgrid"]/tr[1]/following-sibling::tr')
    for lesson_tag in lessons_tag_list:
        num = lesson_tag.xpath('td[1]/a/text()')
        # 检验是否为无效的tr标签
        if num:
            num = num[0]
        else:
            break
        code = lesson_tag.xpath('td[1]/a/@onclick')[0]
        pattern = "xkkh(.+?)xh"
        code = re.search(pattern, code).group()[5:-3]
        lesson_name = lesson_tag.xpath('td[2]/a/text()')[0]
        surplus = lesson_tag.xpath('td[10]/text()')[0]
        lesson = Lesson.Lesson(num, lesson_name, code, "待选择", "待选择", surplus)
        lesson_list.append(lesson)
    return lesson_list


def get_all_information_of_lesson(selector, lesson):
    lesson_list = []
    lessons_tag_list = selector.xpath('//table[@id="xjs_table"]/tr[1]/following-sibling::tr')
    for lesson_tag in lessons_tag_list:
        # num = lesson_tag.xpath('td[1]/text()')[0]
        teacher = lesson_tag.xpath('td[3]/a/text()')[0]
        lesson_time = lesson_tag.xpath('td[4]/text()')[0]
        surplus = int(lesson_tag.xpath('td[12]/text()')[0]) - int(lesson_tag.xpath('td[14]/text()')[0])
        code = lesson_tag.xpath('td[1]/input/@value')[0]
        lesson = Lesson.Lesson(code, lesson.name, lesson.code, teacher, lesson_time, str(surplus))
        lesson_list.append(lesson)
    return lesson_list


def show_and_select_lessons(lesson_list):
    for i in range(len(lesson_list)):
        print(i, end=' ')
        lesson_list[i].show()
    select_id = int(input("\n请输入想选的课的id，id为每门课程开头的数字,如果没有课程显示，代表没有获取到计划内课程: "))
    while select_id < 0 or len(lesson_list) <= select_id:
        select_id = int(input("\n错误的ID，请重新输入:"))
    return select_id


class PlannedCourseSpider:
    def __init__(self, stu_number, stu_password):
        self.number = stu_number
        self.password = stu_password
        self.login = Lg.LoginSpider(stu_number, stu_password)
        self.url = 'http://xk.zucc.edu.cn/'
        self.__VIEWSTATE = ''
        # book by default
        self.__BOOK_MATERIAL = '1'

    def hello_zf(self):
        while not self.login.login_ocr():
            continue

        data = {
            'xh': self.number,
            'xm': self.login.name.encode('utf-8'),
            'gnmkdm': 'N121101',
        }

        self.login.headers['Referer'] = self.url + 'xs_main.aspx?xh=' + self.login.number
        response = self.login.s.get(self.url + 'xsxk.aspx', params=data, headers=self.login.headers)

        self.login.headers['Referer'] = response.url
        selector = etree.HTML(response.text)
        try:
            if "选课条例" in selector.xpath('//*[@id="Form1"]/div/div/div[1]/p/text()')[1]:
                self.__VIEWSTATE = selector.xpath('//*[@id="Form1"]/div/input[@id="__VIEWSTATE"]/@value')[0]
                data = {
                    "__VIEWSTATE": self.__VIEWSTATE,
                    "Button1": "%CE%D2%D2%D1%C8%CF%D5%E6%D4%C4%B6%C1%A3%AC%B2%A2%CD%AC%D2%E2%D2%D4%C9%CF%C4%DA%C8%DD",
                    "TextBox1": 0
                }
                response = self.login.s.post(self.login.headers['Referer'], data=data, headers=self.login.headers)
                self.login.headers['Referer'] = response.url
                selector = etree.HTML(response.text)
        except IndexError:
            print("无需确认选课条例")
        self.set_view_state(selector, "xsxk_form")

        return selector

    def hello_lesson(self, xkkh):
        data = {
            'xh': self.number,
            'xkkh': xkkh,
        }

        response = self.login.s.get(self.url + 'clsPage/' + 'xsxjs.aspx', params=data, headers=self.login.headers)
        self.login.headers['Referer'] = response.url
        selector = etree.HTML(response.text)
        self.set_view_state(selector, 'xsxjs_form')

        return selector

    def english_development(self, selector):
        data = {
            'zymc': selector.xpath('//*[@id="zymc"]/@value')[0],
            '__VIEWSTATE': self.__VIEWSTATE,
            'Button3': '%B4%F3%D1%A7%D3%A2%D3%EF%CD%D8%D5%B9%BF%CE'
        }
        response = self.login.s.post(self.login.headers['Referer'], data=data, headers=self.login.headers)
        selector = etree.HTML(response.text)
        return selector

    def select_lesson(self, lesson):
        data = {
            '__EVENTTARGET': 'Button1',
            '__VIEWSTATE': self.__VIEWSTATE,
            'xkkh': lesson.number,
            'RadioButtonList1': self.__BOOK_MATERIAL
        }
        response = self.login.s.post(self.login.headers['Referer'], data=data, headers=self.login.headers)
        if response.status_code != 200:
            print("抢课失败,错误代码:" + str(response.status_code))
        selector = etree.HTML(response.text)
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        Lesson.show_error(selector)
        self.set_view_state(selector, 'xsxjs_form')

    def set_view_state(self, selector, from_name):
        self.__VIEWSTATE = selector.xpath('//*[@id="__VIEWSTATE"]/@value')[0]
        return self.__VIEWSTATE

    def run(self):
        selector = self.hello_zf()

        while True:
            select_id = int(input("\n0:本专业选课\t1:大学英语拓展课\t(跨专业选课和体育课功能待开发)\n请根据ID选择功能: "))
            if select_id == 0:
                break
            elif select_id == 1:
                selector = self.english_development(selector)
                break
            else:
                print("\n输入有误！请重新输入\t")

        lesson_list = get_all_lesson(selector)
        select_id = show_and_select_lessons(lesson_list)
        selector = self.hello_lesson(lesson_list[select_id].code)
        information_list = get_all_information_of_lesson(selector, lesson_list[select_id])
        choose_id = show_and_select_lessons(information_list)
        self.__BOOK_MATERIAL = input("\n是否预定教材?\n0:否\t1:是")
        while True:
            self.select_lesson(information_list[choose_id])


if __name__ == "__main__":
    number, password = Lg.get_information()
    spider = PlannedCourseSpider(number, password)
    spider.run()
