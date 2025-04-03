# for codepoint in range(0x1F000, 0x1F022):
#     print(chr(codepoint), end=' ')
from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter
import random
tiles = TilesConverter.string_to_34_array(man='13569', pin='123459', sou='443')
print(tiles)
chinese_dishes = [
    "宫保鸡丁", "鱼香肉丝", "麻婆豆腐", "水煮牛肉", "糖醋排骨",
    "回锅肉", "东坡肉", "辣子鸡丁", "清蒸鲈鱼", "红烧狮子头",
    "干煸四季豆", "蒜蓉粉丝虾", "梅菜扣肉", "毛血旺", "蚂蚁上树",
    "三杯鸡", "京酱肉丝", "酸菜鱼", "樟茶鸭子", "咕咾肉",
    "北京烤鸭", "小笼包", "白切鸡", "夫妻肺片", "剁椒鱼头",
    "地三鲜", "汽锅鸡", "羊肉泡馍", "兰州牛肉面", "佛跳墙",
    "盐水鸭", "西湖醋鱼", "辣子鸡", "新疆大盘鸡", "三杯鱿鱼",
    "老鸭汤", "玉米排骨汤", "酸辣汤", "牛肉羹", "冬瓜薏米老鸭汤",
    "乌鸡汤", "罗宋汤", "莲藕猪骨汤", "竹荪炖鸡汤", "番茄蛋花汤",
    "扬州炒饭", "担担面", "热干面", "刀削面", "过桥米线",
    "生煎包", "葱油拌面", "韭菜盒子", "锅贴", "驴肉火烧",
    "糍粑", "肠粉", "炸酱面", "油条", "驴打滚",
    "拍黄瓜", "凉拌木耳", "蒜泥白肉", "红油抄手", "凉拌海带丝",
    "醋溜白菜", "干锅花菜", "虎皮青椒", "蚝油生菜", "上汤娃娃菜",
    "荷塘小炒", "清炒莴笋", "酱香茄子", "五香毛豆", "凉拌蕨根粉",
    "麻辣香锅", "干锅牛蛙", "香辣蟹", "砂锅粥", "腊味煲仔饭",
    "糖醋鲤鱼", "椒盐皮皮虾", "蟹黄豆腐", "红烧划水", "四喜丸子",
    "八宝鸭", "蜜汁叉烧", "豉汁蒸凤爪", "陈皮骨", "避风塘炒蟹",
    "酱牛肉", "糟熘鱼片", "赛螃蟹", "手撕包菜", "蒜蓉空心菜",
    "红焖羊肉", "香煎藕盒", "脆皮烧肉", "酒酿圆子", "糖油粑粑",
    "艾草青团", "蛋黄酥", "红糖糍粑", "豌豆黄", "龙须糖"
]

western_dishes = [
    "惠灵顿牛排", "红酒烩鸡", "番茄肉酱面", "西班牙海鲜饭", "德式烤猪肘",
    "美式BBQ烤肋排", "匈牙利炖牛肉", "香煎鹅肝", "烟熏三文鱼", "芝士焗龙虾",
    "凯撒沙拉", "希腊沙拉", "牛油果鸡肉沙拉", "金枪鱼尼斯沙拉", "烤南瓜藜麦沙拉",
    "洋葱汤", "奶油蘑菇汤", "罗宋汤", "西班牙冷汤", "南瓜浓汤",
    "汉堡套餐", "美式热狗", "塔可", "炸鱼薯条", "芝士通心粉",
    "玛格丽特披萨", "香肠拼盘", "可丽饼", "司康饼", "吉事果",
    "提拉米苏", "焦糖布蕾", "芝士蛋糕", "马卡龙", "苹果派",
    "布朗尼", "冰淇淋", "华夫饼配枫糖浆", "摩卡咖啡", "热巧克力",
    "烤羊排配薄荷酱", "香草烤鸡胸", "焗烤千层面", "黑松露烩饭", "蓝莓松饼"
]
dishes=chinese_dishes+western_dishes
def tohai(char):
    return chr(0x1F000+char//4)
def calculate_shanten(hand):
    # 将136张牌的索引转换为34种牌类型（每4张为一种）
    hand_types = [tile // 4 for tile in hand]
    for i in range(len(hand_types)):
        if hand_types[i]<=6:hand_types[i]=27+hand_types[i]
        else:hand_types[i]=hand_types[i]-7
    counts = [0] * 34
    for tile_type in hand_types:
        counts[tile_type] += 1
    return Shanten().calculate_shanten(counts)

def generate_full_mahjong_tiles():
    # 日本麻将：万/筒/条各1-9×4，字牌（东南西北白发中）×4
    return list(range(136))
def generate_result(seed):
    rng = random.Random(seed)

    # 1. 选13张麻将牌
    tiles = generate_full_mahjong_tiles()
    hand = rng.sample(tiles, 13)
    shanten = calculate_shanten(hand)

    # 2. 选数字（-1和1-100共101个数）
    number = rng.choice([-1] + list(range(1, 101)))
    food = rng.choice(dishes)
    return ''.join([tohai(i) for i in sorted(hand)]), shanten, number, food
print(generate_result(114514))


