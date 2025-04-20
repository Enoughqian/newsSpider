import re
import json
from lxml import etree, html
from bs4 import BeautifulSoup
import requests

def remove_incomplete_tags(html):
    # 解析 HTML 内容
    soup = BeautifulSoup(html, 'html.parser')

    # 找到所有标签
    for tag in soup.find_all(True):  # True 表示查找所有标签
        # 检查标签是否自闭合
        if tag.name in ['br', 'img', 'hr', 'input', 'meta', 'link']:
            continue  # 跳过自闭合标签
        # 如果标签没有闭合，尝试修复
        if tag.name in soup.find_all(tag.name):
            # 删除不完整的标签
            if tag.contents and isinstance(tag.contents[0], str):
                # 替换原标签的内容
                tag.unwrap()  # 移除当前标签
            else:
                tag.decompose()  # 从文档树中删除该标签

    return str(soup)

def p_filter_a1(content, xpath):
    # filter标签
    new_xpath = xpath.replace("p/text()","")
    for i in range(-2,0,1):
        if new_xpath[i] == "/":
            new_xpath = new_xpath[:-1]
    
    # 获得p标签上一级内容
    html_content = etree.HTML(content)
    div_element = html_content.xpath(new_xpath)[0]
    html_string = html.tostring(div_element, encoding='unicode')
    
    # 检查a标签
    tag_pattern = r'<a\s+href=[\'"]?(.*?)?[\'"]?>(.*?)<\/a>'
    
    # 替换
    matches = re.findall(tag_pattern, html_string)
    all_match = [[f'{text}', f'<a href="{href}">{text}'] for href, text in matches]
    
    # 检验第一个p标签的位置
    judge_index = html_string.index("<p")
    
    # 检验匹配出来的tag的位置
    for temp in all_match:
        temp_origin = temp[0]
        temp_replace = temp[1].split(">")[0] + ">"
        
        temp_index = html_string.index(temp_origin)
        if temp_index > judge_index:
            html_string = html_string.replace(temp_replace, "")
    html_string = remove_incomplete_tags(html_string)
    
    content = etree.HTML(html_string).xpath("//p/text()")
    return content


if __name__ == "__main__":
    url = "https://www.aljazeera.com/news/2025/4/14/algeria-orders-exit-of-french-officials-amid-rocky-relations"

    all_xpath = {"content":" //main[@id='main-content-area']//p/text()","pic_set":"//figure[@class='article-featured-image']/div[@class='responsive-image']/img/@src","publish_date":"//div[@class='article-dates']/div/span[2]/text()"}

    text = requests.get(url).text

    b = p_filter_a1(text, all_xpath["content"])
    print(b)

    a = '''Sitting centre-right President Daniel Noboa has won the run-off round of Ecuador\'s presidential election, meaning he will now serve a full four-year term.\nNoboa, who described his victory as "historic", has only been in power since November 2023 after winning a snap election.\nHe has defined his presidency, so far, through a tough military crackdown on violent criminal gangs in the country, which has become the most violent in the region.\nHis left-wing challenger, Luisa González, said she did not accept the result and claimed fraud, without providing evidence.'''
    print(a)