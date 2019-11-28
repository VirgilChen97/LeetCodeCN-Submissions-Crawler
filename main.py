# /usr/bin/env python3
import sys
import os
import time
import requests
import json
# ~~~~~~~~~~~~以下是无需修改的参数~~~~~~~~~~~~~~~~·
# 为了避免弹出一万个warning，which is caused by 非验证的get请求
requests.packages.urllib3.disable_warnings()

leetcode_url = 'https://leetcode-cn.com/'

sign_in_url = leetcode_url + 'accounts/login/'
submissions_url = leetcode_url + 'submissions/'
engDic = {}
chnDic = {}
easy = set()
medium = set()
hard = set()
visited = set()

with open("config.json", "r") as f:  # 读取用户名，密码，本地存储目录
    temp = json.loads(f.read())
    USERNAME = temp['username']
    PASSWORD = temp['password']
    OUTPUT_DIR = temp['outputDir']
    TIME_CONTROL = 3600 * 24 * temp['time']
    LANGUAGE = temp['language']
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
            result = client.post(sign_in_url, data=login_data,
                                 headers=dict(Referer=sign_in_url))

            if result.ok:
                print("Login successfully!")
                break

        except:
            print("Login failed! Wait till next round!")
            time.sleep(sleep_time)

    return client


def scraping(client):
    page_num = START_PAGE

    file_format = {"cpp": ".cpp", "python3": ".py", "python": ".py", "mysql": ".sql", "golang": ".go", "java": ".java",
                   "c": ".c", "javascript": ".js", "php": ".php", "csharp": ".cs", "ruby": ".rb", "swift": ".swift",
                   "scala": ".scl", "kotlin": ".kt", "rust": ".rs"}

    page_num == START_PAGE
    hasNext = True

    while hasNext:
        submissions_url = "https://leetcode-cn.com/api/submissions/?offset=" + \
            str(page_num) + "&limit=20&lastkey="
        print("Now url: ", str(submissions_url))

        h = client.get(submissions_url, verify=False)
        t = time.time()

        html = json.loads(h.text)
        if "submissions_dump" not in html:
            print(html)
            time.sleep(5)
            continue

        for idx, submission in enumerate((html["submissions_dump"])):
            Status = submission['status_display']
            Title = submission['title'].replace(" ", "")
            Lang = submission['lang']

            if Status != "Accepted":
                continue

            # 时间管理，本行代表只记录最近的TIME_CONTROL天内的提交记录
            if t - submission['timestamp'] > TIME_CONTROL:
                return

            try:
                Pid = chnDic.get(Title)

                if Pid in visited:
                    continue

                elif Pid not in visited:
                    if LANGUAGE == 'en_US':
                        problem_name = str(engDic.get(Pid))
                    elif LANGUAGE == 'zh_CN':
                        problem_name = str(Title)
                    else:
                        print('Invalid Language.')
                        return

                    if Pid in easy:
                        difficulty = 'Easy'
                    elif Pid in medium:
                        difficulty = 'Medium'
                    else:
                        difficulty = 'Hard'

                    newpath = OUTPUT_DIR + "/" + difficulty 
                    if not os.path.exists(newpath):
                        os.mkdir(newpath)

                    filename = '{:0=4}'.format(
                        Pid) + "-" + problem_name + file_format[Lang]
                    totalpath = os.path.join(
                        newpath, filename)

                    if os.path.exists(totalpath):
                        # 跳过本地已记录的submission
                        print(
                            str(Pid) + " Already Exists")
                        continue

                    with open(totalpath, "w") as f:  # 开始写到本地
                        # print ("Writing begins!", totalpath)
                        f.write(submission['code'])
                        print(str(Pid) + " Saved")

            except Exception as e:
                print(e.with_traceback)
            
            visited.add(Pid)

        hasNext = html['has_next']
        page_num += 20


def loadEngProblemList(client):
    response = client.get(
        "https://leetcode-cn.com/api/problems/all/", verify=False)
    data = json.loads(response.text)

    generateReadme(data['ac_easy'], data['ac_medium'], data['ac_hard'])

    if "stat_status_pairs" not in data:
        print("Failed to get problem list")
    else:
        problems = data["stat_status_pairs"]
        for problem in problems:
            num = problem["stat"]["question_id"]
            title = problem["stat"]["question__title_slug"]
            if problem['difficulty']['level'] == 1:
                easy.add(num)
            elif problem['difficulty']['level'] == 2:
                medium.add(num)
            else:
                hard.add(num)

            engDic[num] = str(title)


def loadChnProblemList(client):
    query = {
        "operationName": "getQuestionTranslation",
        "variables": {},
        "query": "query getQuestionTranslation($lang: String) {\n  translations: allAppliedQuestionTranslations(lang: $lang) {\n    title\n    questionId\n    __typename\n  }\n}\n"}
    headers = {
        "content-type": "application/json",
        "origin": "https://leetcode-cn.com",
        "referer": "https://leetcode-cn.com/problemset/all/"
    }
    response = requests.post(
        "https://leetcode-cn.com/graphql", headers=headers, data=json.dumps(query))
    data = json.loads(response.text)
    for problem in data['data']['translations']:
        Pid = problem['questionId']
        title = problem['title']
        chnDic[str(title)] = int(Pid)

def generateReadme(easy, medium, hard):
       
    path = os.path.join(OUTPUT_DIR, "README.md")
    content =  "# LeetCode Solutions\n\n" + \
            "This is all my accepted code on LeetCodeCN\n\n" + \
            "Currently solved: \n\n" + \
            "|Difficulty |Count|\n|-|-|\n" + \
            "|**Easy**|`" + str(easy) + "`|\n" + \
            "|**Medium**|`" + str(medium) + "`|\n" + \
            "|**Hard**|`" + str(hard) + "`|\n" + \
            "|Total|`" + str(easy+medium+hard) + "`|"

    with open(path, "w") as f:
        f.write(content)

def git_push():
    today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    os.chdir(OUTPUT_DIR)
    print(os.getcwd())
    instructions = ["git add .", "git status",
                    "git commit -m" + today, "git push -u origin master"]
    for ins in instructions:
        os.system(ins)


def main():
    email = USERNAME
    password = PASSWORD

    print('login')
    client = login(email, password)

    print('Get Problem List')
    loadEngProblemList(client)
    loadChnProblemList(client)

    print('Start fetching')
    scraping(client)

    print('Generate README')

    git_push()
    print('Git PUSH finished')


if __name__ == '__main__':
    main()
