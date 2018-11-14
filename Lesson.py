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



