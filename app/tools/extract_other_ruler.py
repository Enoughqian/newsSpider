import re
import json
from lxml import etree, html
from bs4 import BeautifulSoup
import requests

# 去除标签属性
def remove_specified_tags_attributes(html_content):
    tags_to_remove = ["<em>", "</em>", "<strong>", "</strong>", "<br>", "<b>", "</b>"]
    # 解析HTML内容
    document = html.fromstring(html_content)

    # 遍历指定的标签并去除属性
    for tag in tags_to_remove:
        # 查找所有指定的标签
        elements = document.xpath(f'//{tag.strip("<>")}')
        
        for element in elements:
            # 清空所有属性
            for attr in list(element.attrib.keys()):  # 使用list()以避免修改字典时出现的问题
                del element.attrib[attr]

    # 返回处理后的HTML
    return etree.tostring(document, pretty_print=True, encoding='unicode')

# 处理a标签中的href
def process_a_tags(html_content):
    # 解析HTML内容
    document = html.fromstring(html_content)
    # 查找所有的<a>标签
    a_tags = document.xpath('//a')

    for a in a_tags:
        # 获取当前<a>标签的href属性
        href = a.get('href')

        # 清空所有属性
        for attr in a.attrib.keys():
            del a.attrib[attr]

        # 如果没有href属性，则增加一个空的href属性
        if href is None:
            a.set('href', '')
        else:
            # 保留原有的href属性
            a.set('href', href)
    # 返回处理后的HTML
    return etree.tostring(document, pretty_print=True, encoding='unicode')

# 处理标签闭合问题
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

# 处理p标签下的span
def process_p_drop_span(html_content):
    return html_content.replace("<span>","").replace("</span>","")

def remove_figure_tags(content):
    # 解析 HTML 内容
    html_content = html.fromstring(content)
    
    # 查找并移除所有 figure 标签及其内容
    for figure in html_content.xpath("//figure"):
        figure.getparent().remove(figure)
    
    # 返回修改后的 HTML 内容
    return etree.tostring(html_content, encoding='unicode', method='html')

def p_filter_a1(content, xpath):
    # 处理标签属性
    content = remove_specified_tags_attributes(content)
    
    # 文章解析数据处理
    for i in ["<em>","</em>","<strong>","</strong>","<br>","<b>","</b>"]:
        content = content.replace(i, "")
                
    content = process_a_tags(content)
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
    content = [i for i in content if i.strip() != ""]
    return content

def p_filter_a2(content, xpath):
    # 处理标签属性
    content = remove_specified_tags_attributes(content)

    for i in ["<em>","</em>","<strong>","</strong>","<br>","<b>","</b>"]:
        content = content.replace(i, "")
    
    content = process_a_tags(content)
    content = remove_figure_tags(content)
    
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
    tag_pattern = r'<a\s+href=[\'"]?(.*?)?[\'"]?\s*>(.*?)<\/a>'
    
    # 替换
    matches = re.findall(tag_pattern, html_string, re.DOTALL)
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
    content = [i for i in content if i.strip() != ""]
    return content

def p_filter_a3(content, xpath):
    # 处理标签属性
    content = remove_specified_tags_attributes(content)
    
    for i in ["<em>","</em>","<strong>","</strong>","<br>","<b>","</b>"]:
        content = content.replace(i, "")
    content = process_a_tags(content)
    # filter标签
    new_xpath = xpath.replace("p/text()","")
    content = content.replace('class="topiclink always-topic" ', "")
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
    content = [i for i in content if i.strip() != ""]
    return content

def p_filter_a_and_span(content, xpath):
    # 处理标签属性
    content = remove_specified_tags_attributes(content)
    
    # 文章解析数据处理
    for i in ["<em>","</em>","<strong>","</strong>","<br>","<b>","</b>"]:
        content = content.replace(i, "")
                
    content = process_a_tags(content)
    content = process_p_drop_span(content)
    
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
    content = [i.replace("\n", " ").strip() for i in content if i.strip() != ""]
    return content

def tag_p_filter_a1(content, xpath):
    for i in ["<em>","</em>","<strong>","</strong>","<br>","<b>","</b>"]:
        content = content.replace(i, "")
    content = process_a_tags(content)
    # filter标签
    new_xpath = xpath.replace("p[@class='story-body-text']/text()","")
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
    
    content = etree.HTML(html_string).xpath("//p[@class='story-body-text']/text()")
    content = [i for i in content if i.strip() != ""]
    return content

def div_filter_a1(content, xpath):
    # 解析HTML内容
    soup = BeautifulSoup(content, 'html.parser')
    
    # 查找所有的a标签
    for a_tag in soup.find_all('a'):
        # 获取a标签的文本内容
        a_text = a_tag.get_text(strip=False)
        
        # 将a标签的文本内容插入到其父元素中a标签的位置
        a_tag.replace_with(a_text)
    content = str(soup)
    html_content = etree.HTML(content)
    content = html_content.xpath(xpath)
    content = [i for i in content if i.strip() != ""]
    return content

def p_filter_a_filter_span(content, xpath):
    # 解析HTML内容
    soup = BeautifulSoup(content, 'html.parser')

    # 查找所有 p 标签
    for p_tag in soup.find_all('p'):
        # 创建一个新的 span 标签
        new_span = soup.new_tag('span')
        
        # 遍历 p 标签下的所有直接子节点
        for child in list(p_tag.children):
            if isinstance(child, str):
                # 如果是文本节点，添加到新 span 中
                new_span.append(child)
            elif child.name in ['span', 'a']:
                # 如果是 span 或 a 标签，提取其文本并添加到新 span 中
                new_span.append(child.get_text(strip=False))
                # 移除原标签
                child.decompose()
            else:
                # 其他类型的标签保持不变
                pass
        
        # 如果新 span 包含内容，则添加到 p 标签中
        if new_span.contents:
            p_tag.append(new_span)
    
    content = str(soup).replace("\n"," ").replace("   "," ").replace("  "," ")
    html_content = etree.HTML(content)
    content = html_content.xpath(xpath)
    content = [i for i in content if i.strip() != ""]
    return content
if __name__ == "__main__":
    url = "https://www.aljazeera.com/news/2025/4/14/algeria-orders-exit-of-french-officials-amid-rocky-relations"
    url = "https://www.dawn.com/news/1910183/leadership-responds-with-one-voice-to-indian-attacks"
    url = "https://thedefensepost.com/2025/05/02/collaborative-combat-aircraft-drones-tests/"
    url = "https://www.mining.com/saudi-arabia-and-us-to-sign-mining-deal/"
    url = "https://thedefensepost.com/2025/05/06/us-microwave-weapons-philippines/"
    url = "https://thedefensepost.com/2025/05/09/india-repulsed-pakistan-attacks/"
    url = "https://www.shafaq.com/en/Economy/Kirkuk-s-oil-boom-Iraqi-PM-to-launch-massive-refinery-project"
    url = "https://www.shafaq.com/en/Security/Arab-League-summit-security-first-Iraq-bans-protests-for-ten-days"
    # url = "https://www.shafaq.com/en/Economy/Kirkuk-s-oil-boom-Iraqi-PM-to-launch-massive-refinery-project"

    all_xpath = {"content":" //main[@id='main-content-area']//p/text()","pic_set":"//figure[@class='article-featured-image']/div[@class='responsive-image']/img/@src","publish_date":"//div[@class='article-dates']/div/span[2]/text()"}
    all_xpath = {"content":"//div[contains(@class, 'template__main')]/div[@dir='auto']//p/text()","pic_set":"//div[@class='media__item              ']/picture/img/@src","publish_date":"//span[@class='timestamp--published']/span[@class='timestamp--date']/text()"}
    all_xpath = {"content":"//div[@class='entry-content entry clearfix']/p/span/text() | //div[@class='entry-content entry clearfix']/p/a/span/text() | //div[@class='entry-content entry clearfix']/p/text()","pic_set":"//div[@class='entry-content entry clearfix']/div/a/img/@src","publish_date":"//*[@id='the-post']/header/div/div/span[2]/text()"}
    all_xpath = {"content":"//div[@class='post-inner-content']/div[@class='content']/p/text()","pic_set":"//div[@class='img-content']/img/@src","publish_date":"//div[@class='post-meta mb-4']/text()"}
    all_xpath = {"content":"//div[@class='entry-content entry clearfix']/p/span/text() | //div[@class='entry-content entry clearfix']/p/a/span/text() | //div[@class='entry-content entry clearfix']/p/text()","pic_set":"//div[@class='entry-content entry clearfix']/div/a/img/@src","publish_date":"//*[@id='the-post']/header/div/div/span[2]/text()"}
    all_xpath = {"content":"//article[@id='article']/div/div[@id='newsDetails']//p/text()","pic_set":"//div[@id='articleImg']/img/@src","publish_date":"//span[@id='postDate']/text()"}
    all_xpath = {"content":"//article[@id='article']/div/div[@id='newsDetails']//p/text()","pic_set":"//div[@id='articleImg']/img/@src","publish_date":"//span[@id='postDate']/text()"}
    
    text = requests.get(url).text
    b = p_filter_a_and_span(text, all_xpath["content"])
    print(b)