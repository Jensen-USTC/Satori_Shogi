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
from src.utils import clean_html,seiri,findtitle,check_date_pattern
from urllib.parse import urljoin

#规定：[title,dict] title为标题，用check_date_patter来判定是否是今天。dict是int->str的映射
#需要实现：最新对局，单人：年度胜率，总胜率；双人：对局胜率

def get_first_child_src(tag) -> str | None:
    """
    获取 Tag 对象的第一个子标签的 src 属性
    返回：
        - 存在子标签且含 src 属性时返回属性值
        - 其他情况返回 None
    """
    # 获取第一个子标签（跳过字符串等非标签节点）
    first_child = tag.find(True)  # True 表示匹配任何标签

    if first_child and hasattr(first_child, 'attrs'):
        return first_child.get('src', None)
    return None

def extract_specific_content(html: str) -> str:
    """
    解析HTML并提取指定内容
    返回结果包含所有匹配标签的字符串
    """
    soup = BeautifulSoup(html, 'html.parser')
    result = []
    pic = None
    # 步骤1：找到包含"自動更新"的标题标签
    target_heading = None
    for heading in soup.find_all(class_='wp-block-heading'):
        if "自動更新" in heading.get_text(strip=True):
            target_heading = heading
            break

    if not target_heading:
        return "未找到标题标签"

    # 步骤2：收集目标标签及其后续标签
    current_tag = target_heading
    while True:
        # 添加当前标签到结果
        result.append(str(current_tag))

        # 找到下一个兄弟标签（跳过空白等非标签元素）
        next_tag = current_tag.find_next_sibling()

        # 终止条件判断
        if not next_tag:  # 没有后续标签
            break
        if next_tag.name == 'figure':  # 遇到figure标签
            pic = next_tag
            nnext_tag = next_tag.find_next_sibling()
            if nnext_tag:
                result.append(str(nnext_tag))
            return ('\n'.join(result), get_first_child_src(pic))


        current_tag = next_tag

    return ('\n'.join(result),'')

def to_normal_date(date:str):
    t=date.split('/')
    t=list(map(int,t))
    return str(t[0])+'/'+str(t[1])


def find_p_figure_pairs(html: str) -> list:
    """解析 HTML 并返回所有符合 (p标签 + figure标签) 组合的列表
    用于静态情况的分析
    """
    soup = BeautifulSoup(html, 'html.parser')
    #results = []
    title = findtitle(clean_html(html))
    # 查找所有 figure 标签（按文档顺序）
    for figure in soup.find_all('figure'):
        # 获取前一个同级标签（跳过文本节点等非标签元素）
        prev_tag = figure.find_previous_sibling(True)  # True 表示仅匹配标签

        # 检查前驱标签是否为 p 标签
        if prev_tag and prev_tag.name == 'p':
            # 拼接两个标签的完整 HTML
            r = [prev_tag, get_first_child_src(figure),title]
            if not r[1] : continue
            return r
            # pair = f"{prev_tag}\n{figure}"
            # results.append(pair)
            # break

    return ['今日棋局可能还未开始或尚在布局阶段，还请各位等待后续变化~','','']
def process_detail_page(url):
    """处理详情页的公共逻辑 处理的是*正常部分*"""
    try:
        # 访问详情页
        detail_response = requests.get(url, timeout=10)
        detail_response.raise_for_status()
        res=find_p_figure_pairs(detail_response.text)
        return res
    except requests.exceptions.RequestException as e:
        return f"详情页请求错误: {str(e)}"
    except Exception as e:
        return f"详情页处理错误: {str(e)}"
def active_html(main_page_url):
    """处理 动态部分"""
    dynamic_url = "https://fuwalete.com/q11c/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': main_page_url  # 关键：必须携带来源页
    }
    dynamic_response = requests.get(dynamic_url, headers=headers)
    dynamic_response.raise_for_status()

    # 解析动态返回的HTML
    dynamic_soup = BeautifulSoup(dynamic_response.content, 'html.parser')

    content_div = dynamic_soup.find('div', class_='entry-content cf')
    #return str(len(str(dynamic_soup)))+str(dynamic_soup)[:200]+str(len(clean_html(str(dynamic_soup))))
    return extract_specific_content(str(dynamic_soup))
def get():
    """总处理函数"""
    t_today=''
    t_title=''
    base_url = "https://fuwalete.com"
    max_check = 5  # 最大检查次数
    today = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%m/%d")  # 获取当天日期格式化为 "月/日"（例如：02/24）
    today = to_normal_date(today)
    t_today=today
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
            t_title=title
            if check_date_pattern(today,title):
                # 构建完整链接
                detail_url = urljoin(base_url, link['href'])
                front = active_html(detail_url)
                latter = process_detail_page(detail_url)
                cleaned = clean_html(str(latter[0]))
                flag = '△投了' in cleaned or '▲投了' in cleaned
                if front[1]:
                    return Message([MessageSegment.text(seiri(clean_html((str(front[0]) if not flag else latter[2])+str(latter[0])))),
                                    MessageSegment.image(front[1])])
                elif latter[1]:
                    return Message([MessageSegment.text(seiri(clean_html((str(front[0]) if not flag else latter[2]) + str(latter[0])))),
                                    MessageSegment.image(latter[1])])
                else:
                    return Message([MessageSegment.text(seiri(clean_html((str(front[0]) if not flag else latter[2]) + str(latter[0]))))])


        # 循环结束未找到符合条件的
        return "今天没有对局~"

    except requests.exceptions.RequestException as e:
        return f"请求错误: {str(e)}"
    except Exception as e:
        return f"发生错误: {str(e)}"


taisen = on_command("live", rule=to_me(), aliases={"live"}, priority=10)


@taisen.handle()
async def handle_function(args:Message=CommandArg()):
    await taisen.finish(get())
# print(get())




