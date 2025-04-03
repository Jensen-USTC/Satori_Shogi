from nonebot.rule import to_me
from nonebot.plugin import on_command
from datetime import datetime
from nonebot.adapters.qq import MessageEvent,Message,MessageSegment
from pathlib import Path
from src.randomize import generate_result
luck = on_command("jrrp",rule=to_me(),priority=10)
tickets=["云开日出照乾坤，玉殿千官拜紫宸。福寿双全天赐予，芝兰满室庆长春。","万里鹏程志未休，耕耘莫问几时收。他山石玉堪为鉴，终得云梯步玉楼。","清风徐徐入珠帘，弱火萤光映夜天。闲庭信步观花月，福禄悄然至门前。","枯木逢春再生枝，根深犹待雨露滋。莫道前程无知己，天涯终有相逢时。","三途川上水湍湍，孤雁离群影自寒。欲渡险滩须借力，莫贪捷径惹波澜。","山穷水尽路无门，柳暗花明亦作尘。百事乖违灾祸至，乾坤倒转待重生。"]
tickets_solve=["上上之兆，主\"富贵荣华天付汝\"。诸事亨通，如\"游龙亲临泽，红叶染河水\"，然需持守本心，勿负天恩。","运势平稳，需\"孝悌忠信为本\"。如\"周孝侯射虎斩蛟\"，逆境中显勇毅，终可化险为夷。","小有顺遂，如\"袖里弱火，袖外光明\"。宜把握机遇，忌得意忘形，谨防\"夏日结霜\"之变。","吉凶参半，如\"平川多弯路，旱池见活鱼\"。需忍耐蛰伏，待秋日\"云开月明\"，自有转机。","主波折重重，财散人离。宜守不宜攻，可求贵人相助，行事需如\"樵夫宽眉手未停\"，稳中求进。","运势极凶，事业倾颓、情感破裂，如履薄冰。需戒骄戒躁，积德行善以求转机，切忌铤而走险。"]
review=["，好评如潮！","，是不错的一天呢！","，还行啦还行啦。","，还…还行吧？","，呜哇……","（没错，是百分制……）"]
def getinfo(value):
    if value>90:
        return 1
    if value>75:
        return 2
    if value>50:
        return 3
    if value>25:
        return 4
    if value>10:
        return 5
    return 6
def getimage(num):
    target_path = (
            Path(__file__).resolve().parent.parent  # 解析当前脚本路径并获取父目录
            / "shogi_emote"  # 拼接子目录
            / (str(num)+".jpg")  # 拼接文件名
    )
    return target_path
def return_msg(uid):
    try:
        uid=int(hash(uid))
    except Exception as e:
        return str(e)
    current_date=datetime.now().strftime("%Y%m%d")
    res = generate_result(int(str(current_date)+str(abs(uid))))
    imgpath = getimage(getinfo(res[2]))
    #('🀀🀆🀈🀉🀊🀍🀎🀑🀒🀓🀜🀠🀡', 2, 7, '提拉米苏')
    content=f"""你好呀,你今天的人品值为：{res[2]}{review[getinfo(res[2])-1]}
签文：{tickets[getinfo(res[2])-1]}
解签：{tickets_solve[getinfo(res[2])-1]}
今日推荐食物：{res[3]}
今日起手：{res[0]}（{res[1]}向听）"""
    return Message([MessageSegment.file_image(imgpath),MessageSegment.text(content)])
@luck.handle()
async def future_battle(message: MessageEvent):
    uid = message.get_user_id()
    await luck.finish(return_msg(uid))
