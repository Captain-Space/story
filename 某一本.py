from lxml import etree
import requests
import re
import threading
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',

}
f = 1
ff = 0


def get_book_url():  # 获取书名和书的链接
    url = 'http://m.biqikan.com/top/allvisit_{}/'
    for i in range(1, 2):
        url2 = url.format(i)
        response = requests.get(url2, headers, verify=False)
        pa = re.compile(r'<div class="content_link"><p class="p1"><a href=".*?a href="(.*?)".*?title="(.*?)"', re.S)
        results = re.findall(pa, response.text)
        for _ in results:
            _ = list(_)
            _[0] = 'http://m.biqikan.com' + str(_[0])
            yield {
                '链接': _[0],
                '书名': _[1],
            }


def get_chapter_url(book_url):  # 获取章节链接

    response = requests.get(book_url, headers=headers, verify=False)
    pa = re.compile(r'章节列表.*?"p2">(.*?)</ul>', re.S)
    time.sleep(2)
    response.close()

    response = re.findall(pa, response.text)

    pattern2 = re.compile(r'<li><a href="(.*?)" title="(.*?)"', re.S)
    results = re.findall(pattern2, response[0])
    for result in results:
        result = list(result)
        result[0] = 'http://m.biqikan.com/' + str(result[0])

        yield {
            '链接': result[0],
            '章节名': result[1],
        }


def get_sum_page(page_url):  # 获取本章节共有多少页

    response2 = requests.get(page_url, headers=headers, verify=False)
    html = etree.HTML(response2.text)
    sum_page = html.xpath("/html/body/div[@id='novelbody']/div[@class='nr_function']/h1/text()")
    sum_page = re.search(r"(?<=/)\d+", sum_page[0])
    response2.close()
    if sum_page is not None:
        return sum_page.group()


def get_content(uurl, book_name, flag, sum_page):  # 获取正文内容
    global f, ff

    response3 = requests.get(uurl, headers=headers, verify=False)
    response3.close()
    pattern = re.compile(r"&nbsp;&nbsp;&nbsp;&nbsp;(.*?)<br/>", re.S)
    content = re.findall(pattern, response3.text)
    with open(book_name + '.txt', 'a+') as a:
        if flag == 0:  # 不翻页
            for i in content:
                a.write("        " + str(i) + '\n')
        else:
            num = re.search(r"(?<=-)\d+", uurl)
            num = int(num.group())
            for i in content:
                if (content.index(i) == len(content) - 2) & (f == 1):  # 如果需要翻页的，打印列表的倒数第二项不换行
                    a.write("        " + str(i))
                    continue
                elif '本章未完，请翻页' in str(i):  # 判断是否需要翻页，如果需要，不打印那句话，直接翻页，给ff赋值为1
                    ff = 1
                    num += 1
                    continue
                elif ff == 0:  # 常规情况
                    a.write("        " + str(i) + '\n')
                else:  # 如果是需要翻页的，就不用开头空格了
                    a.write(str(i + '\n'))
                    ff = 0  # 在这之后变成常规情况
                    if num == int(sum_page):  # 最后一页的时候
                        f = 0


def main(book_url, book_name):
    urls = get_chapter_url(book_url)
    global f
    for url in urls:
        chapter_url = str(url['链接'])
        chapter_name = str(url['章节名'])
        sum_page = get_sum_page(chapter_url)
        with open(book_name + '.txt', 'a+') as a:
            a.write(chapter_name + '\n')

        f = 1

        if sum_page is not None:
            for num in range(1, int(sum_page) + 1):
                page_url = re.sub('.html', "-" + str(num) + '.html', chapter_url)

                get_content(page_url, book_name, 1, sum_page)

            with open(book_name + '.txt', 'a+') as a:
                a.write('\n')  # 两章之间空一行
        else:

            get_content(chapter_url, book_name, 0, 1)

            with open(book_name + '.txt', 'a+') as a:
                a.write('\n')  # 两章之间空一行


def main2(i):
    book_url = str(urls[i]['链接'])
    book_name = str(urls[i]['书名'])
    main(book_url, book_name)


if __name__ == '__main__':

    urls = get_book_url()
    urls = list(urls)

    for _ in range(0, 1):
        t = threading.Thread(target=main2, args=(_,))
        t.start()
