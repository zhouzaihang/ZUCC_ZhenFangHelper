import copy
import time

import login as lg
from lxml import etree


def already(selector):
    selected_lessons_pre_tag = selector.xpath('//table[@id="DataGrid2"]/tr')
    print('正方你好！已经选择的公选课为：')
    count = 0
    for i in selected_lessons_pre_tag:
        course = i.xpath('td[1]/text()') + i.xpath('td[7]/text()') + i.xpath('td[8]/text()')
        print(course)
        count += 1
    return count


class LessonSpider:
    class Lesson:
        def __init__(self, num, nam, code, teacher_name, time, surplus):
            self.number = num
            self.name = nam
            self.code = code
            self.teacher_name = teacher_name
            self.time = time
            self.surplus = surplus

        def show(self):
            print('课程代码:' + self.number
                  + '\t课程名:' + self.name
                  # + '\t课程码:' + self.code[10:-3]
                  + '\t教师:' + self.teacher_name
                  + '\t时间:' + self.time
                  + '\t余量:' + self.surplus)

    def __init__(self, number, password, name):
        self.number = number
        self.password = password
        self.name = name
        self.login = lg.LoginSpider(number, password)
        self.url = 'http://xk.zucc.edu.cn/'
        self.base_data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': '',
            'ddl_kcxz': '',
            'ddl_ywyl': '%D3%D0',
            'ddl_kcgs': '',
            'ddl_xqbs': '1',
            'ddl_sksj': '',
            'TextBox1': '',
            'dpkcmcGrid:txtChoosePage': '1',
            'dpkcmcGrid:txtPageSize': '200',
        }
        self.count_lesson = 0

    def hello_zf(self):
        while not self.login.login_manual():
            continue

        data = {
            'xh': self.number,
            'xm': self.name.encode('gb2312'),
            'gnmkdm': 'N121103',
        }

        self.login.headers['Referer'] = self.url + 'xs_main.aspx?xh=' + self.login.number
        response = self.login.s.get(self.url + 'xf_xsqxxxk.aspx', params=data, headers=self.login.headers)

        self.login.headers['Referer'] = response.url
        selector = etree.HTML(response.text)
        self.set_view_state(selector)
        self.count_lesson = already(selector)

    def set_view_state(self, selector):
        __VIEWSTATE = selector.xpath('//*[@id="xsyxxxk_form"]/input[3]/@value')[0]
        self.base_data['__VIEWSTATE'] = __VIEWSTATE

    def search_lessons(self, lesson_name=""):
        self.base_data['TextBox1'] = lesson_name.encode('gb2312')
        self.base_data['Button2'] = '确定'.encode('gb2312')
        response = self.login.s.post(self.login.headers['Referer'], data=self.base_data, headers=self.login.headers)
        selector = etree.HTML(response.text)
        # print(response.text)
        self.set_view_state(selector)
        del self.base_data['Button2']
        del self.base_data['TextBox1']
        return self.get_lessons(selector)

    def get_lessons(self, selector):
        lesson_list = []
        lessons_tag_list = selector.xpath('//table[@id="kcmcGrid"]/tr[1]/following-sibling::tr')
        for lessons_tag in lessons_tag_list:
            code = lessons_tag.xpath('td[1]/input/@name')[0]
            num = lessons_tag.xpath('td[2]/a/@onclick')[0][52:81]
            na = lessons_tag.xpath('td[2]/a/text()')[0]
            teacher_name = lessons_tag.xpath('td[4]/a/text()')[0]
            time = lessons_tag.xpath('td[5]/@title')[0]
            surplus = lessons_tag.xpath('td[11]/text()')[0]
            lesson = self.Lesson(num, na, code, teacher_name, time, surplus)
            lesson_list.append(lesson)
        # print(lesson_list[0].show())
        return lesson_list

    def select_lesson(self, lesson_list):
        data = copy.deepcopy(self.base_data)
        data['Button1'] = '  提交  '.encode('gb2312')
        for lesson in lesson_list:
            code = lesson.code
            data[code] = 'on'
        response = self.login.s.post(self.login.headers['Referer'], data=data, headers=self.login.headers)
        selector = etree.HTML(response.text)
        self.set_view_state(selector)
        print(response.text)
        self.count_lesson = already(selector)

    def run(self):
        self.hello_zf()
        print('请输入搜索课程名字')
        lesson_name = input()
        lesson_list = self.search_lessons(lesson_name)
        for i in range(len(lesson_list)):
            print(i, end='\t')
            lesson_list[i].show()
        print('请输入想选的课的id，id为每门课程开头的数字,如果没有课程显示，代表暂时没有公选课')
        select_id = int(input())
        lesson_list = lesson_list[select_id:select_id + 1]
        while True:
            num = self.count_lesson
            self.select_lesson(lesson_list)
            if self.count_lesson > num:
                break
            else:
                print("抢课失败")
                time.sleep(0.1)


if __name__ == "__main__":
    number = input("学号:")
    password = input("密码:")
    name = input("姓名：")
    spider = LessonSpider(number, password, name)
    spider.run()
    spider.select_lesson(spider.search_lessons())