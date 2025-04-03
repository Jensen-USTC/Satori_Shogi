import cshogi.KI2 as KI2
#from src.utils import get_html
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from src.utils import searchinfo,addinfo,tokif
import os
import time
DRIVER_PATH = r'/usr/bin/chromedriver'
def toBoard(notations):
    #print(list(reversed(notations)))
    board = KI2.Board()
    parser = KI2.Parser()
    num=1
    for move in reversed(notations):
        try:
            #print(num,move)
            parser.parse_move_str(move,board)
            #print(board)
        except Exception:
            res=searchinfo(num)
            if not res:return num
            try:
                res=tokif(res)
            except Exception:return num
            #print(num,move)
            
            parser.parse_move_str(res,board)
            #print(board)
            
        num+=1
    return board.sfen()
def generateURL(sfen):
    if type(sfen)==int:return sfen
    # https://lishogi.org/editor/lnsgkgsnl/1r5b1/ppp1ppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL_b_-_1
    base='https://lishogi.org/editor/'
    return base+sfen
def capture_element_screenshot(url,path):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')  # 无头参数
    options.add_argument('--disable-gpu')  # 禁用gpu 防止占用资源出现bug
    options.add_argument('window-size=1920x1080')  # 设置分窗口辨率
    options.add_argument('--start-maximized')  # 最大化运行（全屏窗口）,不设置，取元素可能会报错
    options.add_argument('--hide-scrollbars')

    options.binary_location = r'/usr/bin/google-chrome'
    s = Service(DRIVER_PATH)

    # 启动浏览器
    driver = Chrome(service=s, options=options)
    try:
        # 访问页面
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        target_element = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".sg-wrap.d-9x9.orientation-sente.manipulable")
        ))
        driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
        time.sleep(0.5)  # 等待滚动完成
        os.makedirs(os.path.dirname(path), exist_ok=True)
        target_element.screenshot(path)

    except Exception as e:
        print(e)
        driver.close()  # 关闭浏览器
        driver.quit()

# 使用示例
if __name__ == "__main__":
    path=os.path.dirname(os.path.abspath(__file__))
    path=os.path.join(path,'screenshot.png')
    capture_element_screenshot(
        url="https://lishogi.org/editor/lr6l/2k1g1g2/2ns1pnp1/p1pp2p1p/1p2s2P1/P1PP1PP1P/1PSS1GN2/2G4R1/LNK5L_b_BPbp_1",
        path=path
    )
