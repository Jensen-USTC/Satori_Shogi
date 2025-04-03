from nonebot.rule import to_me
from nonebot.plugin import on_command,on_notice
from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot import require
from nonebot.adapters.qq import MessageSegment, Message, Bot, Event
import json
Bot_ID='3889611424'
chat_notice = on_notice(priority=10)
@chat_notice.handle()
async def poke(bot:Bot,event:Event,state:T_State):
    description = event.get_event_description()
    values = json.loads(description.replace("'", '"'))
    if values['notice_type'] == 'notify' and values['sub_type'] == 'poke' and str(
            values['target_id']) == Bot_ID:
        await chat_notice.finish("别戳啦~")
