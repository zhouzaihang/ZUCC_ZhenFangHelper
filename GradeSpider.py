import Login as Lg
from lxml import etree
import time


class Course:
    def __init__(self, academic_year, semester, course_code, course_name, credit, grade_point, grade):
        self.academic_year = academic_year
        self.semester = semester
        self.course_code = course_code
        self.course_name = course_name
        self.credit = credit
        self.grade_point = grade_point
        self.grade = grade

    def tostring(self):
        return ('(\'课程名: ' + self.course_name + '\', \'学期: ' + self.semester
                + '\', \'课程代码: ' + self.course_code + '\', \'学年: ' + self.academic_year
                + '\', \'学分: ' + self.credit + '\', \'绩点: ' + self.grade_point
                + '\', \'成绩: ' + self.grade + '\')')


class GradeSpider:
    def __init__(self, stu_number, stu_password):
        self.number = stu_number
        self.password = stu_password
        self.login = Lg.LoginSpider(stu_number, stu_password)
        self.url = 'http://xk.zucc.edu.cn/'
        self.years = []
        self.semester = []
        self.params = {
            'xh': self.number,
            'xm': self.login.name.encode('gb2312'),
            'gnmkdm': 'N121617',
        }
        self.data = {
            '__VIEWSTATE': '',
            'ddlXN': '',
            'ddlXQ': '',
            'Button2': '',
        }
        self.features = ['0-按学期查询', '1-按学年查询', '2-在校学习成绩查询', '3-根据课程名称查询']

    @staticmethod
    def get_grade(response_text):
        selector = etree.HTML(response_text)
        all_grade = selector.xpath('//*[@id="Datagrid1"]/tr[1]/following-sibling::tr')
        courses = []
        for tr in all_grade:
            academic_year = tr.xpath('td[1]/text()')[0]
            semester = tr.xpath('td[2]/text()')[0]
            course_code = tr.xpath('td[3]/text()')[0]
            course_name = tr.xpath('td[4]/text()')[0]
            credit = tr.xpath('td[7]/text()')[0]
            grade_point = tr.xpath('td[8]/text()')[0][3:]
            grade = tr.xpath('td[9]/text()')[0]
            courses.append(Course(academic_year, semester, course_code, course_name, credit, grade_point, grade))
        return courses

    @staticmethod
    def get_select(options):
        result = []
        for option in options:
            if option is not None:
                result.append(option.xpath('@value')[0])
        return result

    @staticmethod
    def query_by_name(course_name, courses):
        result = []
        for course in courses:
            if course_name in course.course_name:
                result.append(course)
        return result

    @staticmethod
    def query_by_xq(courses, xq):
        result = []
        if courses is not None:
            for course in courses:
                if xq == course.semester:
                    result.append(course)
        return result

    @staticmethod
    def query_by_xn(courses, xn):
        result = []
        for course in courses:
            if xn == course.academic_year:
                result.append(course)
        return result

    @staticmethod
    def list_course(courses):
        if len(courses) == 0:
            print("没有查询到课程的成绩信息")
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            return
        for course in courses:
            print(course.tostring())

    def hello_grade(self):
        self.login.headers['Referer'] = self.url + 'xs_main.aspx?xh=' + self.login.number
        response = self.login.s.get(self.url + 'xscj_gc2.aspx', params=self.params, headers=self.login.headers)
        self.login.headers['Referer'] = response.url
        selector = etree.HTML(response.text)
        self.data['__VIEWSTATE'] = selector.xpath('//*[@id="Form1"]/input/@value')[0]
        self.years = self.get_select(selector.xpath('//*[@id="ddlXN"]/option[1]/following-sibling::option'))
        self.semester = self.get_select(selector.xpath('//*[@id="ddlXQ"]/option[1]/following-sibling::option'))[:-1]

    def query_all_grade(self, button, ddl_xn='', ddl_xq=''):
        self.data['Button2'] = button.encode('gb2312')
        self.data['ddlXN'] = ddl_xn
        self.data['ddlXQ'] = ddl_xq
        response = self.login.s.post(self.url + 'xscj_gc2.aspx', params=self.params,
                                     headers=self.login.headers, data=self.data)
        return response.text

    def input_xn(self):
        print("当前可查询的学年有:")
        for i in range(len(self.years)):
            print(str(i) + " . " + self.years[i])
        return self.years[int(input("请根据数字先选择学年: "))]

    def input_xq(self):
        print("当前可查询的学期有:")
        for i in range(len(self.semester)):
            print(str(i) + " . " + self.semester[i])
        return self.semester[int(input("请根据数字选择学期: "))]

    def get_final_grade(self):
        print(self.features)
        cmd = int(input("回复数字选择功能:"))
        xn = xq = course_name = ''
        if cmd == 0:
            xn = self.input_xn()
            xq = self.input_xq()
        elif cmd == 1:
            xn = self.input_xn()
        elif cmd == 3:
            course_name = input('请输入要查询的课程名称:')
        elif cmd != 2:
            print("输入错误的数字!请重新输入!")
        while True:
            content = self.query_all_grade(self.features[2][2:])
            courses = self.get_grade(content)
            if cmd == 0:
                courses = self.query_by_xn(courses, xn)
                courses = self.query_by_xq(courses, xq)
            elif cmd == 1:
                courses = self.query_by_xn(courses, xn)
            elif cmd == 3:
                courses = self.query_by_name(course_name, courses)
            elif cmd != 2:
                print("输入错误的数字!请重新输入!")
            print(time.strftime('\n %Y-%m-%d %H:%M:%S \n', time.localtime(time.time())))
            if len(courses) != 0:
                self.list_course(courses)
                if cmd == 3:
                    break
            else:
                print("没有查询到相关课程成绩")
            time.sleep(5)

    def run(self):
        while not self.login.login_ocr():
            continue
        self.hello_grade()
        self.get_final_grade()


if __name__ == "__main__":
    number, password = Lg.get_information()
    spider = GradeSpider(number, password)
    spider.run()
