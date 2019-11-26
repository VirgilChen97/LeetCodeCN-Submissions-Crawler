# /usr/bin/env python3
"""
这是一个将力扣中国(leetcode-cn.com)上的【个人提交】的submission自动爬到本地并push到github上的爬虫脚本。
请使用相同目录下的config.json设置 用户名，密码，本地储存目录等参数。
致谢@fyears， 本脚本的login函数来自https://gist.github.com/fyears/487fc702ba814f0da367a17a2379e8ba
"""

import unicodedata
import sys
import os
import time
from ProblemList import GetProblemId
import requests
import json
from bs4 import BeautifulSoup
import json
# ~~~~~~~~~~~~以下是无需修改的参数~~~~~~~~~~~~~~~~·
# 为了避免弹出一万个warning，which is caused by 非验证的get请求
requests.packages.urllib3.disable_warnings()

leetcode_url = 'https://leetcode-cn.com/'

sign_in_url = 'accounts/login/'
sign_in_url = leetcode_url + sign_in_url
submissions_url = 'submissions/'
submissions_url = leetcode_url + submissions_url
dic = {}

with open("config.json", "r") as f:  # 读取用户名，密码，本地存储目录
    temp = json.loads(f.read())
    USERNAME = temp['username']
    PASSWORD = temp['password']
    OUTPUT_DIR = temp['outputDir']
    TIME_CONTROL = 3600 * 24 * temp['time']
# ~~~~~~~~~~~~以上是无需修改的参数~~~~~~~~~~~~~~~~·

# ~~~~~~~~~~~~以下是可以修改的参数~~~~~~~~~~~~~~~~·
START_PAGE = 0  # 从哪一页submission开始爬起，0是最新的一页
sleep_time = 5  # in second，登录失败时的休眠时间
# ~~~~~~~~~~~~以上是可以修改的参数~~~~~~~~~~~~~~~~·


def login(email, password):  # 本函数copy自https://gist.github.com/fyears/487fc702ba814f0da367a17a2379e8ba，感谢@fyears
    client = requests.session()
    client.encoding = "utf-8"

    while True:
        try:
            client.get(sign_in_url, verify=False)
            login_data = {'login': email, 'password': password}
            result = client.post(sign_in_url, data=login_data, headers=dict(Referer=sign_in_url))

            if result.ok:
                print("Login successfully!")
                break

        except:
            print("Login failed! Wait till next round!")
            time.sleep(sleep_time)

    return client


def scraping(client):
    page_num = START_PAGE
    visited = [0 for _ in range(2000)]

    file_format = {"cpp": ".cpp", "python3": ".py", "python": ".py", "mysql": ".sql", "golang": ".go", "java": ".java",
                   "c": ".c", "javascript": ".js", "php": ".php", "csharp": ".cs", "ruby": ".rb", "swift": ".swift",
                   "scala": ".scl", "kotlin": ".kt", "rust": ".rs"}

    page_num == START_PAGE
    while True:
        submissions_url = "https://leetcode-cn.com/api/submissions/?offset=" + str(page_num) + "&limit=1&lastkey="
        print("Now url: ", str(submissions_url))

        h = client.get(submissions_url, verify=False)
        t = time.time()
        invalidset = set()
        html = json.loads(h.text)
        if "submissions_dump" not in html:
            if html["detail"] == '您没有执行该操作的权限。':
                continue
            else:
                print("No further submissions")
                break

        for idx, submission in enumerate((html["submissions_dump"])):
            Status = submission['status_display']
            Title = submission['title'].replace(" ", "")
            Lang = submission['lang']

            if Status != "Accepted":
                print(str(GetProblemId(Title)) + " is not Accepted")
                continue

            # 时间管理，本行代表只记录最近的TIME_CONTROL天内的提交记录
            if t - submission['timestamp'] > TIME_CONTROL:
                return

            try:
                Pid = GetProblemId(Title)

                if Pid == 0 or Title in invalidset:
                    print(str(GetProblemId(Title)) + " Failed ! Due to unknown Pid! ")
                    if Title not in invalidset:  # 第一次没找到
                        with open("Log.txt", "a") as log:
                            log.write("Unknown PID happened for ", Title)
                        invalidset.add(Title)

                else:
                    if visited[Pid] != 1:
                        newpath = OUTPUT_DIR + "/" + \
                            '{:0=4}'.format(Pid) + "." + \
                            str(dic.get(Pid))  # 存放的文件夹名
                        if not os.path.exists(newpath):
                            os.mkdir(newpath)

                        filename = '{:0=4}'.format(
                            Pid) + "-" + str(dic.get(Pid)) + file_format[Lang]  # 存放的文件名
                        totalpath = os.path.join(
                            newpath, filename)  # 把文件夹和文件组合成新的地址

                        if os.path.exists(totalpath):
                            # 跳过本地已记录的submission
                            print(newpath + "exists! Continue for the next submission!")
                            continue

                        with open(totalpath, "w") as f:  # 开始写到本地
                            # print ("Writing begins!", totalpath)
                            f.write(submission['code'])
                            print(str(GetProblemId(Title)) + " Writing ends!")
                            visited[Pid] = 1  # 保障每道题只记录最新的AC解
            except Exception as e:
                print(e.with_traceback)

        page_num += 1


def loadEngName():
    with open("problem.json", "r", encoding='UTF-8') as f:
        problems = json.load(f)["stat_status_pairs"]
        for problem in problems:
            num = problem["stat"]["question_id"]
            title = problem["stat"]["question__title_slug"]
            dic[num] = str(title)


def git_push():
    today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    os.chdir(OUTPUT_DIR)
    print(os.getcwd())
    instructions = ["git add .", "git status",
                    "git commit -m \"" + today, "git push -u origin master"]
    for ins in instructions:
        os.system(ins)
        # print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("~~~~~~~~~~~~~" + ins + " finished! ~~~~~~~~")
        # print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


def main():
    email = USERNAME
    password = PASSWORD
    loadEngName()

    print('login')
    client = login(email, password)

    print('start scrapping')
    scraping(client)
    print('end scrapping')

    git_push()
    print('Git PUSH finished')


if __name__ == '__main__':
    main()
