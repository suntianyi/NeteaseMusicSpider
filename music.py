import threading
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils import Utils
from utils.Utils import Conf, Redis, DbUtils

'''
自动化测试抓取网易云音乐
'''


# 获取所有歌单
def get_all_play_list(browser):
    url = 'https://music.163.com/#/discover/playlist'
    browser.get(url)
    # 切换到内容页
    browser.switch_to.frame('contentFrame')
    for e in browser.find_elements_by_class_name('msk'):
        title = e.get_attribute('title')
        href = e.get_attribute('href')
        print(title, href)
        Redis.push_url(href)
    e = browser.find_elements_by_class_name('znxt')[0]
    while 'js-disabled' not in e.get_attribute('class'):
        e.click()
        for e in browser.find_elements_by_class_name('msk'):
            title = e.get_attribute('title')
            href = e.get_attribute('href')
            Redis.push_url(href)
            print(title, href)
        e = browser.find_elements_by_class_name('znxt')[0]
    browser.close()


# 获取歌单下的音乐
def get_song_by_play_list(browser, url):
    browser.get(url)
    browser.switch_to.frame('contentFrame')
    for e in browser.find_elements_by_class_name('txt'):
        title = e.find_element_by_tag_name('b').get_attribute('title')
        href = e.find_element_by_tag_name('a').get_attribute('href')
        print(title, href)
        Redis.push_url(href)


# 获取音乐详情
# 编号
# 歌曲名<em class="f-ff2">Unique</em>
# 作者<span title="Headhunterz / Conro / Clara Mae">
# 专辑
# 评论数<span id="cnt_comment_count">11128</span>
def get_song_detail(browser, url):
    browser.get(url)
    browser.switch_to.frame('contentFrame')
    e = browser.find_element_by_class_name('cnt')
    song_id = url.split('=')[-1]
    title = e.find_element_by_tag_name('em').text
    author = e.find_element_by_tag_name('span').get_attribute('title')
    album = e.find_elements_by_tag_name('p')[1].find_element_by_tag_name('a').text
    comment_count = e.find_element_by_id('cnt_comment_count').text
    print('编号：%s，名称：%s，歌手：%s，专辑：%s，评论数：%s' % (song_id, title, author, album, comment_count))
    # 保存
    DbUtils.insert_music((song_id, title, author, album, comment_count, url))
    # 获取相似歌曲
    for e in browser.find_elements_by_class_name('s-fc1'):
        title = e.get_attribute('title')
        href = e.get_attribute('href')
        print(title, href)
        # 放入redis队列
        Redis.push_url(href)


def run():
    browser = webdriver.Chrome(Conf.driver_path)
    status = 0
    while True:
        url = Redis.pop_url()
        if 'playlist' in url:
            get_song_by_play_list(browser, url)
        elif 'song' in url:
            get_song_detail(browser, url)
        else:
            print('队列中无任务')
            status += 1
            time.sleep(5)
        if status == 3:
            break
    browser.close()


if __name__ == '__main__':
    Utils.Utils.load_config()
    Redis.connect()
    DbUtils.connect()
    chrome_options = Options()
    # Chrome-headless 模式， Google 针对 Chrome 浏览器 59版 新增加的一种模式，可以让你不打开UI界面的情况下使用 Chrome 浏览器，所以运行效果与 Chrome 保持完美一致。
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(Conf.driver_path, chrome_options=chrome_options)
    get_all_play_list(browser)
    for i in range(5):
        t = threading.Thread(target=run)
        t.start()
