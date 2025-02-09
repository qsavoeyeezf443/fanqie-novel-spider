import requests
import re
import os
import csv
import json
from bs4 import BeautifulSoup


def get_novel_info(url, headers):
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ValueError(f"网址未能访问，error code：{response.status_code}")

    # 转换为soup对象
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    # print(soup)

    # 获取html中的title
    long_name = soup.find('title').text

    # 从title中提取小说名字
    name_match = re.search(r'_(.*?)小说_', long_name)
    if name_match:
        novel_name = name_match.group(1)
        # print(f'==================== novel_name : {novel_name} ====================')
    else:
        raise ValueError("No title match found")

    # 创建相关文件夹
    global save_path
    save_path = f'{os.getcwd()}\download\{novel_name}'
    show_path = f'./download/{novel_name}/'
    if os.path.exists(save_path):
        print(f'文件夹之前已创建, go on')
    else:
        print(f'{show_path}  未创建, 开始build')
        os.mkdir(save_path)
        print('文件夹已创建完毕')

    # 获取小说info的json
    novel_info = soup.find('script', type="application/ld+json").text
    parsed_info = json.loads(novel_info)

    # 获取img封面的url
    img_url = parsed_info['image'][0]

    img_response = requests.get(img_url, headers=headers)
    img = img_response.content

    # 保存图像到本地文件
    if os.path.exists(f'{save_path}\cover.jpg'):
        print('封面已存在, go on')
    else:
        with open(f"{save_path}\cover.jpg", "wb") as f:
            f.write(img)
            print('封面已保存完毕')

    # 获取每章的name、href
    chapter_title_all = soup.find_all('a', class_='chapter-item-title', target='_blank')
    chapter_list = []
    for chapter_title in chapter_title_all[1:]:
        chapter_name = chapter_title.get_text()
        chapter_href = 'https://fanqienovel.com' + chapter_title['href']
        chapter_id = re.search(r'\d+', chapter_title['href']).group()
        chapter_api = (f"https://novel.snssdk.com/api/novel/book/reader/full/v1/?device_platform=android&"
                       f"parent_enterfrom=novel_channel_search.tab.&aid=2329&platform_id=1&group_id={chapter_id}&item_id={chapter_id}")
        chapter_list.append([chapter_name, chapter_href, chapter_api])

    # 写入CSV文件
    csv_filename = f'{save_path}\chapter_data.csv'

    with open(csv_filename, 'w', newline='', encoding="utf_8_sig") as csv_file:
        csv_writer = csv.writer(csv_file)

        # 写入表头
        csv_writer.writerow(['Title', 'URL', 'Api'])

        # 写入数据
        csv_writer.writerows(chapter_list)

    print(f'Chapter info has been written to {show_path}chapter_data.csv')

# # test
# if __name__ == '__main__':
#     url = 'https://fanqienovel.com/page/7299902479909522494'
#     headers = {
#         "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
#     }
#     get_novel_info(url, headers)