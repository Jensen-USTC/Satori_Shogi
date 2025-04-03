import cshogi
import cshogi.KI2 as KI2
import re
import matplotlib.pyplot as plt
from shogi import Board

# board = cshogi.Board()
# plt.figure(figsize=(6, 6))
# board.plot()  # 假设该库有 plot 方法
# plt.savefig('shogi_board.png', dpi=300, bbox_inches='tight')
board = KI2.Board()
parser = KI2.Parser()
num1 = '１２３４５６７８９'
num2 = '一二三四五六七八九'
tmp = parser.parse_move_str('▲２六歩',board)
#parser.parse_move_str('△３四歩',board)
#parser.parse_move_str('▲２五歩',board)
print(tmp,'\n',board)
print(board.sfen())
from selenium import webdriver

chromedriver_path = r"C:\Users\Li\Downloads\chrome-win64\chrome-win64\chromedriver.exe"
driver = webdriver.Chrome()


# 登录百度
def main():
    driver.get("https://baidu.com/")


if __name__ == '__main__':
    main()