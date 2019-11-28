# LeetCodeCN-Crawler

本项目是一个用来爬取力扣中国上**个人提交**的代码的爬虫。

注意：是爬取【个人】也就是【你自己的账号】提交的代码，不是爬取【他人】的代码，更不是爬取【官方代码】

本项目在JiayangWu的爬虫上进行了改进，不再需要手动维护题目列表，可以切换中英文题目名称，并且会自动生成含有你完成数目统计的README

# 使用方法
1. clone或者download到本地
2. 配置config.json文件，用户名，密码，本地存储地址，时间控制（天），语言选择
3. `pip3 install requests` 安装requests包
4. `python3 main.py`

# 例子

我自己的 LeetCode 题解: https://github.com/VirgilChen97/LeetCode_Sol

# 一些说明
1. 目前支持的语言有：{"cpp": ".cpp", "python3": ".py", "python": ".py", "mysql": ".sql", "golang": ".go", "java": ".java",
                   "c": ".c", "javascript": ".js", "php": ".php", "csharp": ".cs", "ruby": ".rb", "swift": ".swift",
                   "scala": ".scl", "kotlin": ".kt", "rust": ".rs"}
2. 致谢@fyears， 本脚本的login函数来自https://gist.github.com/fyears/487fc702ba814f0da367a17a2379e8ba
3. config.json里的time代表爬多少天之内的submission，比如我每天爬今天提交的题解，就是设置为0.8就好了，如果第一次使用需要爬所有的题解，就设一个大一点的数比如1000之类的。

