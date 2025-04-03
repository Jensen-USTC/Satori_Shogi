from nonebot.rule import to_me
from nonebot.plugin import on_command
# from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import require
from nonebot.adapters.qq import MessageSegment, Message
import requests
from bs4 import BeautifulSoup
from src.utils import find_max_similarity_link,convert_url,single_score,find_match_record
score = on_command("score",rule=to_me(),priority=10)
# score = on_command("score",rule=to_me(),aliases={"score"},priority=10,block=True)
async def innerfunc(args):
    if name := args.extract_plain_text():
        sheet = (name.strip()).split()
        if len(sheet) >= 3:
            return "用法：\n/score 棋士 查询棋士近年的战绩\n/score 棋士1 棋士2 查询两位棋士的对局历史成绩"
        elif len(sheet) == 2:
            return find_match_record(sheet[1].strip(), convert_url(find_max_similarity_link(sheet[0].strip())))
        elif len(sheet) == 1:
            return single_score(find_max_similarity_link(sheet[0].strip()))
        else:
            return "用法：\n/score 棋士 查询棋士近年的战绩\n/score 棋士1 棋士2 查询两位棋士的对局历史成绩"


    else:
        return "用法：\n/score 棋士 查询棋士近年的战绩\n/score 棋士1 棋士2 查询两位棋士的对局历史成绩"
@score.handle()
async def get_score(args:Message=CommandArg()):
    info = await innerfunc(args)
    await score.finish(info)
