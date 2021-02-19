from lxml import etree
import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',

}
f = 1
ff = 0


def get_chapter_url(book_url):
    response = requests.get(book_url, headers=headers, verify=False)
    pa = re.compile(r'章节列表.*?"p2">(.*?)</ul>', re.S)
    response = re.findall(pa, response.text)

    pattern2 = re.compile(r'<li><a href="(.*?)" title="(.*?)"', re.S)
    results = re.findall(pattern2, response[0])
    for result in results:
        result = list(result)
        result[0] = 'http://m.biqikan.com/' + str(result[0])
        # print(result[0] + '  --' + result[1])

        yield {
            '链接': result[0],
            '章节名': result[1],
        }


def get_sum_page(page_url):  # 获取本章节共有多少页
    response2 = requests.get(page_url, headers=headers, verify=False)
    html = etree.HTML(response2.text)
    sum_page = html.xpath("/html/body/div[@id='novelbody']/div[@class='nr_function']/h1/text()")
    sum_page = re.search(r"(?<=/)\d+", sum_page[0])

    if sum_page is not None:
        return sum_page.group()


def get_content(uurl, flag, sum_page):
    global f, ff
    response3 = requests.get(uurl, headers=headers, verify=False)
    pattern = re.compile(r"&nbsp;&nbsp;&nbsp;&nbsp;(.*?)<br/>", re.S)
    content = re.findall(pattern, response3.text)
    if flag == 0:  # 不翻页
        for i in content:
            print("        ", end='')  # 每段开头空格
            print(i)  # 每段后面加换行符
    else:
        num = re.search(r"(?<=-)\d+", uurl)
        num = int(num.group())
        for i in content:

            if (content.index(i) == len(content) - 2) & (f == 1):  # 如果需要翻页的，打印列表的倒数第二项不换行
                print("        ", end='')
                print(i, end='')
                continue
            elif '本章未完，请翻页' in str(i):  # 判断是否需要翻页，如果需要，不打印那句话，直接翻页，给ff赋值为1
                ff = 1
                num += 1
                continue
            elif ff == 0:  # 常规情况
                print("        ", end='')  # 每段开头空格
                print(i)  # 每段后面加换行符
            else:  # 如果是需要翻页的，就不用开头空格了
                print(i)
                ff = 0  # 在这之后变成常规情况
                if num == sum_page:  # 最后一页的时候
                    f = 0


def main():
    urls = get_chapter_url('http://m.biqikan.com/14/14368.html')

    for url in urls:
        chapter_url = str(url['链接'])
        sum_page = get_sum_page(chapter_url)
        if sum_page is not None:
            for num in range(1, int(sum_page) + 1):
                page_url = re.sub('.html', "-" + str(num) + '.html', chapter_url)
                get_content(page_url, 1, sum_page)

            print()
        else:
            get_content(chapter_url, 0, 1)

            print()


if __name__ == '__main__':

    main()
