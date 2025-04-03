import requests
from bs4 import BeautifulSoup,Tag
import os
import re,json
from datetime import datetime
from zoneinfo import ZoneInfo
_script_dir = os.path.dirname(os.path.abspath(__file__))
_file_path = os.path.join(_script_dir,"kishi_names.txt")
_file_path2 = os.path.join(_script_dir,"record.txt")
SENTE='▲'
GOTE='△'
def tokif(element):
    num1 = '１２３４５６７８９'
    num2 = '一二三四五六七八九'
    element = element.replace('步', '歩')
    element = element.replace('银', '銀')
    element = element.replace('飞', '飛')
    if element.strip()[-2:] == '成桂':
        element = element[:-2] + '圭'
    if element.strip()[-2:] == '成香':
        element = element[:-2] + '杏'
    if element.strip()[-2:] == '成銀':
        element = element[:-2] + '全'
    # 合法
    if element[1] != '同':
        element = element[0] + num1[ord(element[1]) - ord('1')] + num2[ord(element[2]) - ord('1')] + element[3:]
    return element

def addinfo(handnumber,kifu):
    #保证了合法
    data=None
    with open(_file_path2,'r',encoding='utf-8') as f:
        try:
            data=json.load(f)
        except Exception:pass
    today = str(datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%m/%d"))  # 获取当天日期格式化为 "月/日"（例如：02/24）
    # print(data)
    nowdata = []
    if type(data) != list or data[0] != today:
        nowdata = [today, dict()]
    else:
        nowdata = data
    nowdata[1][handnumber] = kifu
    with open(_file_path2,'w',encoding='utf-8') as f:
        json.dump(nowdata,f)

def searchinfo(hand):
    data=None
    with open(_file_path2,'r',encoding='utf-8') as f:
        try:
            data=json.load(f)
        except Exception:pass
        if (not data) or type(data)!=list:return None
        today = str(datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%m/%d"))
        if data[0]!=today:
            return None
        dictionary = data[1]
        return dictionary.get(str(hand))
def check_date_pattern(target_date, text):
    """
    检查文本是否包含特定日期模式
    :param target_date: 目标日期字符串，格式为"月/日"(如"3/9")
    :param text: 待检测的文本
    :return: bool类型，满足任一条件返回True
    """
    try:
        # 解析目标日期
        month, day = map(int, target_date.split('/'))

        # 基础校验（非精确月份天数校验）
        if not (1 <= month <= 12) or not (1 <= day <= 31):
            raise ValueError("日期格式错误")

        prev_day = day - 1
        prev_date = f"{month}/{prev_day}"

    except (ValueError, AttributeError):
        raise ValueError("无效日期格式，请使用'月/日'格式（如：3/9）")

    # 构建正则表达式模式
    patterns = [
        # 模式1：直接包含目标日期
        re.escape(target_date),

        # 模式2：前一天日期 + 汉字括号 + 目标日
        re.escape(prev_date) +  # 前一天的日期
        r'[\(（]' +  # 左括号（支持全角/半角）
        r'[\u4e00-\u9fff]{1}' +  # 单个汉字
        r'[\)）]' +  # 右括号（支持全角/半角）
        re.escape(str(day))  # 目标日期的日部分
    ]

    # 组合成正则表达式
    regex_pattern = r'|'.join(patterns)

    # 执行正则匹配
    return re.search(regex_pattern, text) is not None
def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text
def seiri(html):
    lst = html.split('\n')
    res=[]
    for line in lst:
        if '今日棋局可能还未开始或尚在布局阶段，还请各位等待后续变化~' in line:
            res.append(line.strip())
            continue
        if line.strip()[0] in ('▲','△','▶'):
            res.append(line.strip())
            continue
        if len(line)<=3:continue
        if '自動更新中' in line:continue
        if len(line)>7 and line[1]!='手' and line[2]!='手' and line[3]!='手' and ('先手▲' not in line or '後手△' not in line):
            continue
        res.append(line.strip())
    res=res[:20]
    return '\n'.join(res)

def findtitle(content):
    lines = content.split('\n')
    for line in lines:
        if '後手△' in line and '先手▲' in line:
            return line.strip()
    return ''
def remove_html_tags(html):
    soup = BeautifulSoup(html, "html.parser")
    # 获取纯文本并去除首尾空白
    return soup.get_text(strip=True)

def clean_html(html_content, keep_linebreaks=True):
    """
    清理HTML标签并保留可读文本
    参数：
        html_content: 原始HTML内容
        keep_linebreaks: 是否保留换行格式（默认保留）
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 删除不需要的元素（可选）
    for element in soup(['script', 'style', 'noscript', 'meta', 'link']):
        element.decompose()

    # 获取纯文本
    text = soup.get_text(separator=('\n' if keep_linebreaks else ' '))

    # 进一步清理空白
    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:  # 跳过空行
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)
def find_max_similarity_link(name):
    url = "https://shogidata.info/list/rateranking.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    names = []
    corr = []
    try:
        # 获取网页内容
        with open(_file_path,"r",encoding="utf-8") as f:
            corr=f.readlines()
            for i in range(len(corr)):
                corr[i]=corr[i].split()
                corr[i][0]=corr[i][0].strip()
                corr[i][1] = corr[i][1].strip()
            corr=dict(corr)
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # 解析HTML结构
            soup = BeautifulSoup(response.text, 'html.parser')
            main_table = soup.find(class_="table table-rateranking")
            #print(main_table)
            if not main_table:
                return "目标表格未找到"

            # 定位tbody
            #print(main_table.find('table'))
            tbody = main_table.find('table')
            if not tbody:
                return "tbody未找到"

            max_similarity = -1
            target_tr = None

            # 遍历所有tr
            for tr in tbody.find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) < 2:
                    continue

                # 提取第二个td的文本
                target_td = tds[1]
                s = target_td.get_text(strip=True).split()[0]
                chn = corr.get(s)
                if not chn:continue
                if len(name)!=len(s):continue
                flag=0
                for i in range(len(name)):
                    if name[i]!=s[i] and name[i]!=chn[i]:
                        flag=1
                        break
                if flag:continue
                #找到
                target_tr=tr
                break


            # 获取最终链接
            if target_tr:
                link = target_tr.find_all('td')[1].find('a')
                return (link.get('href'),s) if link else "链接未找到"
            return "匹配项不存在。如果输入名称为新注册的职业棋士，请联系管理员。"

    except requests.exceptions.RequestException as e:
        return f"请求失败: {str(e)}"
    except Exception as e:
        return f"解析异常: {str(e)}"


def find_match_record(name, urls):
    # 双人战绩
    #print(url)
    # url = "https://shogidata.info/list/rateranking.html"  # 假设目标网址
    url = urls[0]
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        with open(_file_path,"r",encoding="utf-8") as f:
            corr = f.readlines()
            for i in range(len(corr)):
                corr[i] = corr[i].split()
                corr[i][0] = corr[i][0].strip()
                corr[i][1] = corr[i][1].strip()
            corr = dict(corr)
            # 获取网页内容
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # 解析HTML结构
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找第三个box-content
            boxes = soup.find_all(class_="box-content")
            if len(boxes) < 3:
                return "目标容器未找到"

            # 定位目标t元素（三级子结构）
            target_div = boxes[2]
            for _ in range(2):  # 三次取第一个子元素
                children = [child for child in target_div.children if isinstance(child, Tag)]
                target_div = children[0] if children else None
                if not target_div:
                    return "结构解析失败"
                #print(target_div)
            #print(target_div)

            # 遍历所有tr
            for tr in target_div.find_all('tr'):
                tds = tr.find_all(['td', 'th'])  # 兼容td/th标签
                if len(tds) < 2:
                    continue

                # 提取第一个子元素的文字内容
                first_text = tds[0].get_text(strip=True)
                first_text = first_text.split(" ")[0].strip()
                #print(first_text)
                flag = 1
                if len(first_text) != len(name): continue
                chs = corr.get(first_text)
                if not chs:continue
                for i in range(len(first_text)):
                    if name[i]!=first_text[i] and name[i]!=chs[i]:
                        flag=0
                        break
                if not flag:continue
                return urls[1]+"对"+first_text+"的战绩：\n"+tds[1].get_text(strip=True)

            # 未找到匹配项
            return "网络出现问题，名称输入错误，或两人没有对局记录。如果为新登录棋士，请联系管理员。"

    except requests.exceptions.RequestException as e:
        return f"网络请求失败: {str(e)}"
    except Exception as e:
        return f"解析异常: {str(e)}"
def convert_url(url):
    sheet=url[0].split('/')
    res="https://shogidata.info/result/"
    return (res+sheet[-1],url[1])
def single_score(urls):
    # 单人战绩
    try:
        url = urls[0]
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        target_h3 = None
        for h3 in soup.find_all('h3'):
            if h3.get_text(strip=True) == '年度別成績':
                target_h3 = h3
                break
        if target_h3:
            siblings_content = []
            for sibling in target_h3.find_next_siblings():
                siblings_content.append(str(sibling))
                break
            result = ''.join(siblings_content)
            return urls[1]+"的近年对局战绩：\n"+clean_html(result)
        else:
            result = '未找到指定H3标签'
            return result
    except Exception as e:
        return "网络出现问题或名称输入错误。如果为新登录棋士，请联系管理员。"
#print(tokif(SENTE+'45飞'))