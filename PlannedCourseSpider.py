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
    # print(lessons_tag_list)
    for lesson_tag in lessons_tag_list:
        # num = lesson_tag.xpath('td[1]/text()')[0]
        teacher = lesson_tag.xpath('td[2]/a/text()')[0]
        time = lesson_tag.xpath('td[6]/text()')[0]
        surplus = int(lesson_tag.xpath('td[12]/text()')[0]) - int(lesson_tag.xpath('td[15]/text()')[0])
        code = lesson_tag.xpath('td[16]/input/@value')[0]
        lesson = Lesson.Lesson(code, lesson.name, lesson.code, teacher, time, str(surplus))
        lesson_list.append(lesson)
        # lesson.show()
    return lesson_list


def show_and_select_lessons(lesson_list):
    for i in range(len(lesson_list)):
        print(i, end=' ')
        lesson_list[i].show()
    select_id = int(input("请输入想选的课的id，id为每门课程开头的数字,如果没有课程显示，代表没有获取到计划内课程: "))
    while select_id < 0 or len(lesson_list) <= select_id:
        select_id = int(input("错误的ID，请重新输入: "))
    return select_id


class PlannedCourseSpider:
    def __init__(self, stu_number, stu_password, stu_name):
        self.number = stu_number
        self.password = stu_password
        self.name = stu_name
        self.login = Lg.LoginSpider(stu_number, stu_password)
        self.url = 'http://xk.zucc.edu.cn/'
        self.__VIEWSTATE = ''

    def hello_zf(self):
        while not self.login.login_ocr():
            continue

        data = {
            'xh': self.number,
            'xm': self.name.encode('gb2312'),
            'gnmkdm': 'N121103',
        }

        self.login.headers['Referer'] = self.url + 'xs_main.aspx?xh=' + self.login.number
        response = self.login.s.get(self.url + 'xsxk.aspx', params=data, headers=self.login.headers)

        self.login.headers['Referer'] = response.url
        selector = etree.HTML(response.text)
        self.set_view_state(selector, 'xsxk_form')

        return selector

    def hello_lesson(self, xkkh):
        data = {
            'xh': self.number,
            'xkkh': xkkh,
        }

        response = self.login.s.get(self.url + 'xsxjs.aspx', params=data, headers=self.login.headers)

        self.login.headers['Referer'] = response.url
        selector = etree.HTML(response.text)
        self.set_view_state(selector, 'xsxjs_form')

        return selector

    def select_lesson(self, lesson):
        data = {
            '__EVENTTARGET': 'Button1',
            '__VIEWSTATE': self.__VIEWSTATE,
            'xkkh': lesson.code
        }
        response = self.login.s.post(self.login.headers['Referer'], data=data, headers=self.login.headers)
        selector = etree.HTML(response.text)
        Lesson.show_error(selector)
        self.set_view_state(selector, 'xsxjs_form')

    def set_view_state(self, selector, from_name):
        self.__VIEWSTATE = selector.xpath('//*[@id="' + from_name + '"]/input[3]/@value')[0]
        return self.__VIEWSTATE

    def run(self):
        selector = self.hello_zf()
        lesson_list = get_all_lesson(selector)
        select_id = show_and_select_lessons(lesson_list)
        selector = self.hello_lesson(lesson_list[select_id].code)
        information_list = get_all_information_of_lesson(selector, lesson_list[select_id])
        choose_id = show_and_select_lessons(information_list)
        while True:
            self.select_lesson(information_list[choose_id])


if __name__ == "__main__":
    number, password, name = Lg.get_information()
    spider = PlannedCourseSpider(number, password, name)
    spider.run()
