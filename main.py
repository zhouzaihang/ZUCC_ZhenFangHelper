import Login as Lg
import PlannedCourseSpider
import PublicCourseSpider


def run(choose):
    if choose == 0:
        spider = PublicCourseSpider.PublicLessonSpider(number, password, name)
        spider.run()
    elif choose == 1:
        spider = PlannedCourseSpider.PlannedCourseSpider(number, password, name)
        spider.run()


number, password, name = Lg.get_information()
choose_id = ''

while True:
    choose_id = input("输入0进入公选课选课，输入1进入计划内课程选课")
    if choose_id.isdigit():
        choose_id = int(choose_id)
        if 0 <= choose_id <= 1:
            break

while True:
    try:
        run(choose_id)
    except Exception:
        print("Error: 网络好像有点问题")
        continue
