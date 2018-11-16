import re


def show_error(selector):
    error_tags = selector.xpath('/html/head/script/text()')
    for error_tag in error_tags:
        if error_tag:
            r = "alert\('(.+?)'\);"
            for s in re.findall(r, error_tag):
                print('\n' + s)


class Lesson:
    def __init__(self, num, name, code, teacher_name, time, surplus):
        self.number = num
        self.name = name
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
