import copy
import time
import Login as Lg
from lxml import etree
import Lesson


def get_lessons(selector):
    lesson_list = []
    lessons_tag_list = selector.xpath('//table[@id="kcmcGrid"]/tr[1]/following-sibling::tr')
    for lessons_tag in lessons_tag_list:
        code = lessons_tag.xpath('td[1]/input/@name')[0]
        # num = lessons_tag.xpath('td[2]/a/@onclick')[0][52:81]
        class_name = lessons_tag.xpath('td[2]/a/text()')[0]
        num = lessons_tag.xpath('td[3]/text()')[0]
        teacher_name = lessons_tag.xpath('td[4]/a/text()')[0]
        lesson_time = lessons_tag.xpath('td[5]/@title')
        if lesson_time:
            lesson_time = lesson_time[0]
        else:
            lesson_time = "空"
        surplus = lessons_tag.xpath('td[11]/text()')[0]
        lesson = Lesson.Lesson(num, class_name, code, teacher_name, lesson_time, surplus)
        lesson_list.append(lesson)
    return lesson_list


def already(selector):
    selected_lessons_pre_tag = selector.xpath('//table[@id="DataGrid2"]/tr')
    print('\n你好！已经选择的公选课为：')
    count = 0
    for i in selected_lessons_pre_tag:
        course = i.xpath('td[1]/text()') + i.xpath('td[7]/text()') + i.xpath('td[8]/text()')
        print(course)
        count += 1
    return count


class PublicLessonSpider:
    def __init__(self, stu_number, stu_password):
        self.number = stu_number
        self.password = stu_password
        self.login = Lg.LoginSpider(stu_number, stu_password)
        self.url = 'http://xk.zucc.edu.cn/'
        self.base_data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': '',
            'ddl_kcxz': '',
            'ddl_ywyl': '',
            'ddl_kcgs': '',
            'ddl_xqbs': '1',
            'ddl_sksj': '',
            'TextBox1': '',
            'dpkcmcGrid:txtChoosePage': '1',
            'dpkcmcGrid:txtPageSize': '200',
        }
        self.count_lesson = 0

    @property
    def hello_zf(self):
        while not self.login.login_ocr():
            continue

        data = {
            'xh': self.number,
            'xm': self.login.name.encode('utf-8'),
            'gnmkdm': 'N121102',
        }

        self.login.headers['Referer'] = self.url + 'xs_main.aspx?xh=' + self.login.number
        response = self.login.s.get(self.url + 'xf_xsqxxxk.aspx', params=data, headers=self.login.headers)

        self.login.headers['Referer'] = response.url
        selector = etree.HTML(response.text)
        time.sleep(4)
        if "选课条例" in selector.xpath('//*[@id="Form1"]/div/div/div[1]/p/text()')[1]:
            data = {
                "__VIEWSTATE": selector.xpath('//*[@id="Form1"]/div/input[@id="__VIEWSTATE"]/@value')[0],
                "Button1": "我已认真阅读，并同意以上内容".encode("utf-8"),
                "TextBox1": 0
            }
            response = self.login.s.post(self.login.headers['Referer'], data=data, headers=self.login.headers)
            self.login.headers['Referer'] = response.url
            selector = etree.HTML(response.text)
        # print(response.text)
        self.set_view_state(selector)
        return selector

    def set_view_state(self, selector):
        __VIEWSTATE = selector.xpath('//*[@id="xsyxxxk_form"]/div/input[@id="__VIEWSTATE"]/@value')[0]
        self.base_data['__VIEWSTATE'] = __VIEWSTATE

    def search_lessons(self, lesson_name=""):
        self.base_data['TextBox1'] = lesson_name.encode('utf-8')
        self.base_data['Button2'] = '确定'.encode('utf-8')
        response = self.login.s.post(self.login.headers['Referer'], data=self.base_data, headers=self.login.headers)
        selector = etree.HTML(response.text)
        self.set_view_state(selector)
        del self.base_data['Button2']
        del self.base_data['TextBox1']
        return selector

    def select_lesson(self, lesson_list):
        data = copy.deepcopy(self.base_data)
        data['Button1'] = '  提交  '.encode('utf-8')
        print("\n正在抢课：")
        for lesson in lesson_list:
            data[lesson.code] = 'on'
            print(lesson.name)
        response = self.login.s.post(self.login.headers['Referer'], data=data, headers=self.login.headers)
        selector = etree.HTML(response.text)
        Lesson.show_error(selector)
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        self.set_view_state(selector)
        self.count_lesson = already(selector)
        return len(lesson_list)

    def run(self):
        selector = self.hello_zf
        self.count_lesson = already(selector)
        print('请输入课程名字进行搜索(准确查找|直接回车显示所有公选课)')
        lesson_name = input()
        lesson_list = get_lessons(self.search_lessons(lesson_name))
        select_list = []

        while True:
            for i in range(len(lesson_list)):
                print(i, end='\t')
                lesson_list[i].show()
            print('\n请输入想选的课的ID ID为每门课程开头的数字(每次输入一个ID 可以多次输入)'
                  ' 丨 选完课程后，回车开始自动抢课 丨 如果没有课程显示，代表没有获取公选课')
            select_id = input()
            if select_id.isdigit():
                select_id = int(select_id)
                if 0 <= select_id < len(lesson_list):
                    select_list.append(lesson_list[select_id])
                else:
                    break
            else:
                break

        num = self.count_lesson
        while True:
            want = self.select_lesson(select_list)
            if self.count_lesson >= num + want:
                break
            else:
                print("\n抢课失败")


if __name__ == "__main__":
    number, password = Lg.get_information()
    spider = PublicLessonSpider(number, password)
    spider.run()
