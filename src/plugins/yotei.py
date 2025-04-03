from nonebot.rule import to_me
from nonebot.plugin import on_command
# from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import require
from nonebot.adapters.qq import MessageSegment, Message
#import requests
import aiohttp
from bs4 import BeautifulSoup,Tag
mirai_taisen = on_command("preview",rule=to_me(),priority=10)
# mirai_taisen = on_command("preview",rule=to_me(),aliases={"preview"},priority=10,block=True)


@mirai_taisen.handle()
async  def future_battle():
    info = await parse_info()
    await mirai_taisen.finish(info if info.strip() else '现在还没有预定对局~')
async def parse_info():
    url = "https://shogidata.info/list/broadcast.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        response=''

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                #resp.raise_for_status()
                response = await resp.text()
        # 发送HTTP请求
        # response = requests.get(url, headers=headers)
        # #await response.raise_for_status()  # 检查HTTP错误

        # 解析HTML
        soup = BeautifulSoup(response, 'html.parser')
        container = soup.find(class_="box-content broadcast_plan")

        if not container:
            return "目标容器未找到"

        result = []

        # 遍历直接子元素
        for child in container.children:
            # 过滤非标签元素（如换行符文本节点）
            if not isinstance(child, Tag):
                continue

            # 处理DIV标签
            if child.name == 'div':
                text = child.get_text(strip=True)
                if text:
                    result.append(text)

            # 处理SECTION标签
            elif child.name == 'section':
                ul = child.find('ul')
                if ul:
                    # 提取前两个li的内容
                    tmp= ul.find_all('li', limit=3)
                    for li in tmp:
                        li_text = li.get_text(strip=True)
                        if li_text:
                            result.append(li_text)

        # 用换行符连接结果
        return '\n'.join(result)
    except Exception as e:
        return f"请求失败: {str(e)}"
