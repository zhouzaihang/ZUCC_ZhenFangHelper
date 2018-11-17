import requests
import Login as Lg
import PlannedCourseSpider
import PublicCourseSpider

choose_id = ''
while True:
    choose_id = input("输入0进入公选课选课，输入1进入计划内课程选课")
    if choose_id.isdigit():
        choose_id = int(choose_id)
        if 0 <= choose_id <= 1:
            break

while True:
    try:
        number, password, name = Lg.get_information()
        spider = ''
        if choose_id == 0:
            spider = PublicCourseSpider.PublicLessonSpider(number, password, name)
        elif choose_id == 1:
            spider = PlannedCourseSpider.PlannedCourseSpider(number, password, name)
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
