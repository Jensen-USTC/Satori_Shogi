from nonebot.rule import to_me
from nonebot.plugin import on_message
from src.deepseek import getresponse
from nonebot.adapters.qq import MessageEvent
import random
from nonebot.params import CommandArg
from nonebot import require
from nonebot.adapters.qq import MessageSegment, Message

chat = on_message(rule=to_me(),priority=1,block=True)
facelang="""ฅ^•ﻌ•^ฅ
(=｀ω´=)
(◍•ᴗ•◍)ﾉ♡
(=^･ｪ･^=)
(=ＴェＴ=)
(^._.^)ﾉ
(=⌒‿‿⌒=)
(≧◡≦) ♡
(⁎˃ᆺ˂)
(=^‥^=)""".split('\n')
@chat.handle()
async def deepseek(message: MessageEvent):
    if content := message.extract_plain_text():
        await chat.finish(getresponse(content))
    else:
        await chat.finish(random.choice(facelang))