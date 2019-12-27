import os
import random
import subprocess
import requests
import urllib.request
import re
# noinspection PyUnresolvedReferences
from aip import AipOcr
# noinspection PyUnresolvedReferences
from io import BytesIO
# noinspection PyUnresolvedReferences
from PIL import Image

config = {
    '头脑王者': {
        'title': (80, 500, 1000, 1080),
        'answers': (80, 960, 1000, 1920),
        'point': [
            (300, 1219, 600, 1334),
            (300, 1449, 600, 1564),
            (300, 1633, 600, 1748),
            (300, 1817, 600, 1932),
        ]
    }
}

def get_screenshot():
    process = subprocess.Popen('adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
    # 获取手机截图的二进制内容
    screenshot = process.stdout.read()
    screenshot = screenshot.replace(b'\r\n', b'\n')
    with open('test.png', 'wb') as f:
        f.write(screenshot)
    # 把图片存到电脑内存
    img_fb = BytesIO()
    img_fb.write(screenshot)
    # 图片处理
    img = Image.open(img_fb)
    # 切出题目
    title_img = img.crop((80, 500, 1000, 1080))
    # 切出答案
    answer_img = img.crop((80, 960, 1000, 1920))
    new_img = Image.new('RGBA', (920, 1540))
    new_img.paste(title_img, (0, 0, 920, 580))
    new_img.paste(answer_img, (0, 580, 920, 1540))
    new_img_fb = BytesIO()
    new_img.save(new_img_fb, 'png')
    with open('test.png', 'wb')as f:
        f.write(new_img_fb.getvalue())
    return new_img_fb

def get_word_by_img(img):
    #利用百度接口识别图片文字
    APP_ID = '18103043'
    API_KEY = 'ksTQUG5GDnOn7dI5YCu2rsX6'
    SECRET_KEY = '3fHI93BEG8XhoeN88EmqGQzjzboufxwV'
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    res = client.basicGeneral(img)
    return res

def baidu(question, answers):
    # 利用搜狗搜索题目并找出最佳答案
    url = 'https://www.sogou.com/sogou?'
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
    }
    data = {
        'query': question
    }
    res = requests.get(url, params=data, headers=headers)
    res.encoding = 'utf-8'
    html = res.text
    for i in range(len(answers)):
        answers[i] = (html.count(answers[i]), answers[i], i)
    answers.sort(reverse=True)
    return answers

def click(point):
    #点击手机的正确答案
    cmd = 'adb shell input swipe %s %s %s %s %s' % (
        point[0],
        point[1],
        point[0] + random.randint(0, 3),
        point[1] + random.randint(0, 3),
        200
    )
    os.system(cmd)

def run():
    print("准备答题!")
    while True:
        input("输入回车开始答题:")
        img = get_screenshot()
        info = get_word_by_img(img.getvalue())
        if info['words_result_num'] < 5:
            continue
        answers = [x['words'] for x in info['words_result'][-4:]]
        question = ''.join([x['words'] for x in info['words_result'][:-4]])
        res = baidu(question, answers)
        print(question)
        print(res)
        click(config['头脑王者']['point'][res[0][2]])

if __name__ == '__main__':
    run()
