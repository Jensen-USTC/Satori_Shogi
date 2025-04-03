from nonebot.rule import to_me
from nonebot.plugin import on_command
# from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import require
from nonebot.adapters.qq import MessageSegment, Message
import requests
data = on_command("dojo",rule=to_me(),aliases={"dojo"},priority=10)
def check(name):
    styles = ['棋风未知', '居飞车党', '纯粹居飞车党', '振飞车党', '纯粹振飞车党', '全能型棋手',
     '真正全能型棋手', '対抗形倾向', '対抗形迷', '力战派', '矢仓迷', '角换迷', '横歩取迷',
     '三间飞车党', '三间飞车迷', '四间飞车党', '四间飞车迷', '中飞车党', '中飞车迷']
    template = "https://system.81dojo.com/api/v2/players/detail/"
    try:
        url = template + name + '.json'
        value = requests.get(url, timeout=10)
        if len(value.text) < 100:
            value = eval(value.text)
        else:
            return '请求错误,请联系管理员'
        if type(value) != dict:return "请求错误,可能是用户不存在"
        return f"""{name}的81道场战绩：
棋风：{styles[int(value['style_id'])]}
最高R值：{str(value['max_rate'])}
胜场-负场：{str(value['wins'])}-{str(value['losses'])}
连胜：{str(value['streak'])}
最高连胜：{str(value['streak_best'])}"""
    except Exception as e:
        return '请求错误,'+str(e)
@data.handle()
async def dojo_data(args:Message=CommandArg()):
    if name := args.extract_plain_text():
        await data.finish(check(name))
    else:
        await data.finish("用法:@Satori /道场数据 name\n查询用户名为name的81道场对战数据。")
