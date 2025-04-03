from nonebot.rule import to_me
from nonebot.plugin import on_command
# from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import require
from nonebot.adapters.qq import MessageSegment, Message
from datetime import datetime
import requests
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup, PageElement,Tag
from src.utils import clean_html,check_date_pattern,addinfo,searchinfo,tokif
#import src.screenshot as scr
from urllib.parse import urljoin
from src.screenshot import toBoard,generateURL,capture_element_screenshot
import re,os,jsonZ
from pathlib import Path
_script_dir = os.path.dirname(os.path.abspath(__file__))
_file_path = os.path.join(_script_dir,"record.txt")
SENTE='▲'
GOTE='△'


def active_html(main_page_url):
    """处理 动态部分"""
    dynamic_url = "https://fuwalete.com/q11c/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': main_page_url  # 关键：必须携带来源页
    }
    dynamic_response = requests.get(dynamic_url, headers=headers)
    dynamic_response.raise_for_status()
    return dynamic_response.text
#思路：获得动态部分，获得静态部分，(1)判断状态，清除，拼接，提取，整理（根据状态），提取-生成图片
#print(clean_html(active_html('https://fuwalete.com/%e4%bd%90%e8%97%a4%e5%a4%a9%e5%bd%a6-215760/')))
def process_detail_page(url):
    """处理详情页的公共逻辑 处理的是*正常部分*"""
    try:
        # 访问详情页
        detail_response = requests.get(url, timeout=10)
        detail_response.raise_for_status()
        return detail_response.text
    except requests.exceptions.RequestException as e:
        return f"请求错误: {str(e)}"
    except Exception as e:
        return f"处理错误: {str(e)}"
#print(clean_html(process_detail_page('https://fuwalete.com/%e4%bd%90%e8%97%a4%e5%a4%a9%e5%bd%a6-215760/')))
def status(html):
    #html should be cleaned
    if '▲投了' in html or '△投了' in html:
        return 2#ends
    sheet = html.split('\n')
    flag=0
    for line in sheet:
        if '▶'==line.strip():
            flag+=1
        if '1手　%　▲' in line.strip():
            flag+=1
    if flag>=2:
        return 0
    return 1
def filter_lines(text):
    # 按换行符分割字符串
    lines = text.split('\n')
    # 定义正则表达式：行开头为整数 + "手" + 至少一个空白符
    pattern = r'^\d+手\s'
    # 筛选符合正则条件的行
    result = [line for line in lines if (re.match(pattern, line) and '1手　%　▲' != line.strip())]
    return result
def extract(html):
    #html should be cleaned
    text = filter_lines(html)
    lines = []
    hand = 0
    for line in text:
        if '1手　%　▲' in line.strip() and len(line.strip())<=7:continue
        #遍历所有合法行
        if '▶千日手' in line : break
        line=line.split()
        flag=False
        for element in line:
            if element.endswith('手') and '勝' not in element:
                hand=int(element[:-1])
            #print('>>>'+element)
            if len(element)<3 : continue
            if element[0] in ['▲','△'] and element[1] in'123456789同':
                element=tokif(element)
                lines.append(element)
                flag=True
                break
        result = searchinfo(hand)
        if not flag:
            #没有找到合适的
            if result:
                lines.append(tokif(str(result)))
                continue
            else:return hand
        if result:
            lines.pop()
            lines.append(tokif(str(result)))
    return lines
def outputcontent(html,length):
    # 添加 来源可能有错误
    stat = status(html)
    if stat == 0:
        return "今日对局还未开始，请耐心等待~"
    steps = filter_lines(html)
    
    result = []
    #result.append("局面图可能有误，仅供参考")
    sheet = html.split('\n')
    flag = 1
    flag2 = 1
    for line in sheet:
        if '1手　%　▲' in line.strip():continue
        if '1手　%　▲' in line:continue
        if line.strip()=='▶':continue
        if line.strip()[0] in ['▲','△']:
            result.append(line.strip())
        if '先手▲'  in line and '後手△'  in line and flag:
            if len(line.split())==0:continue
            if line.split()[0].strip() in ('先手▲','後手△'):continue
            result.append(line.strip())
            flag = 0
        if line.strip()[0]=='▶' and flag2:
            result.append(line.strip())
            flag2 = 0
    return '\n'.join((result+steps)[:length])
#url='https://fuwalete.com/%e4%bc%8a%e8%97%a4%e5%8c%a0-215886/'
# content=clean_html(active_html(url))+clean_html(process_detail_page(url))
# print(outputcontent(content))
# print(generateURL(toBoard(extract(content))))
def to_normal_date(date:str):
    t=date.split('/')
    t=list(map(int,t))
    return str(t[0])+'/'+str(t[1])
def get(args):
    LEN=15
    content = args.extract_plain_text()
    if content.strip():
        try:
            LEN=int(content)
        except Exception:
            pass
        return setting(content)
    t_today = ''
    t_title = ''
    base_url = "https://fuwalete.com"
    max_check = 5  # 最大检查次数
    today = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%m/%d")  # 获取当天日期格式化为 "月/日"（例如：02/24）
    today = to_normal_date(today)
    t_today = today
    try:
        # 第一步：获取初始页面
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()

        # 解析初始页面
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找所有目标链接（限制最多检查5个）
        target_links = soup.find_all('a', class_='new-entry-card-link widget-entry-card-link a-wrap', limit=max_check)

        # 遍历符合条件的链接
        for link in target_links:
            # 检查title属性是否存在且包含当天日期
            title = link.get('title', '')
            t_title = title
            if check_date_pattern(today,title):
                # 构建完整链接
                detail_url = urljoin(base_url, link['href'])
                active = active_html(detail_url)
                static = process_detail_page(detail_url)
                content = clean_html(active+static)
                stat = status(content)
                steps = extract(content)
                words = outputcontent(content,LEN)
                if not stat:
                    return words
                if type(steps)!=list and status(content):
                    #不是未开始
                    words=f"第{str(steps)}手出现错误，请手动修改。"+words
                    return words
                kifurl = generateURL(toBoard(steps))
                if type(kifurl)==int:
                    words = f"第{str(kifurl)}手出现错误，请手动修改。" + words
                    return words
                current_file_path = os.path.abspath(__file__)
                parent_dir = os.path.dirname(current_file_path)
                image_path = os.path.join(parent_dir, 'screenshot.png')
                capture_element_screenshot(kifurl,image_path)
                #return words
                return Message([MessageSegment.file_image(Path(image_path)),MessageSegment.text(words)])

        # 循环结束未找到符合条件的
        return "今天没有对局~"

    except requests.exceptions.RequestException as e:
        return f"请求错误: {str(e)}"
    except Exception as e:
        return f"发生错误: {str(e)}"
def setting(arg):
    USAGE="""用法：/live n notation
    在信息门户网站产生错误时，人为规定当天对局的第n手为notation。"""
    args=arg.split()
    if len(args)!=2:
        return USAGE
    args=[args[0].strip(),args[1].strip()]
    try:
        args[0]=int(args[0])
    except Exception:
        return USAGE
    if args[1][0] not in (SENTE,GOTE):
        if args[0]%2==0:args[1]=GOTE+args[1]
        else:args[1]=SENTE+args[1]
    addinfo(args[0],args[1])
    return f"已将第{str(args[0])}手设置为{tokif(str(args[1]))}。"
# print(get())

taisen = on_command("live", rule=to_me(), aliases={"live"}, priority=10,block=True)


@taisen.handle()
async def handle_function(args:Message=CommandArg()):
    await taisen.finish(get(args))
#
#


#
# print(setting('4 同步'))
# print(searchinfo(4))
