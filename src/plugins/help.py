from nonebot.rule import to_me
from nonebot.plugin import on_command
# from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import require
from nonebot.adapters.qq import MessageSegment, Message
import os
from pathlib import Path
test = on_command("help",rule=to_me(),priority=10)
def return_path():
    current_script_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_script_path)
    parent_dir = os.path.dirname(current_dir)
    help_png_path = os.path.join(parent_dir, 'help.png')
    return help_png_path
@test.handle()
async def future_battle():
    await test.finish(Message([MessageSegment.file_image(Path(return_path()))]))