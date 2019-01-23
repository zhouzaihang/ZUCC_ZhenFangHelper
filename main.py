import requests
import Login as Lg
import PlannedCourseSpider
import PublicCourseSpider
import GradeSpider

choose_id = ''
while True:
    choose_id = input("0-公选课选课 丨 1-计划内课程选课 丨 2-成绩查询")
    if choose_id.isdigit():
        choose_id = int(choose_id)
        if 0 <= choose_id <= 2:
            break

while True:
    try:
        number, password = Lg.get_information()
        if choose_id == 0:
            spider = PublicCourseSpider.PublicLessonSpider(number, password)
        elif choose_id == 1:
            spider = PlannedCourseSpider.PlannedCourseSpider(number, password)
        elif choose_id == 2:
            spider = GradeSpider.GradeSpider(number, password)
        # noinspection PyUnboundLocalVariable
        spider.run()
    except requests.exceptions.ConnectionError:
        print("Error: 网络好像有点问题")
        continue
    except FileNotFoundError:
        print("文件读取异常，检查字模和information.json")
        break
    except KeyboardInterrupt:
        print("结束")
        break
