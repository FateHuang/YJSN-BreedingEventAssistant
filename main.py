print("工具打开的时候会有点慢，耐心等待一会儿")
print("开头会显示一些警告信息，无视即可。")
import cv2
import numpy as np
from cnocr import CnOcr, read_img, line_split
import pyautogui
import time
from pynput import mouse
from fuzzywuzzy import fuzz
import json
import os
import base
from ctypes import windll
with open("./config.json", "r", encoding="utf-8") as f:
    sys_cfg = json.load(f)
ocr = CnOcr(rec_vocab_fp='.\label_cn.txt', rec_root='.\cnocr', det_root='.\cnstd')  # 所有参数都使用默认值
# 定时截图的间隔（以秒为单位）
interval = 1  # 1秒
handle = windll.user32.FindWindowW(None, sys_cfg["模拟器窗口名"])
# base.resize_client(handle, 540, 960)

def on_click(x, y, button, pressed):
    if pressed:
        print(f'鼠标点击在 ({x}, {y})，按下的按钮是 {button}')
        # 如果需要在此处执行其他操作，请添加您的代码
    else:
        # 单击已释放
        return False  # 停止监听

def get_region(region_name):
    # 提示用户点击左上角
    print(f"请设置{region_name}区域的左上角")
    # 创建鼠标监听器
    mouse_listener1 = mouse.Listener(on_click=on_click)
    mouse_listener1.start()
    mouse_listener1.join()
    left_top = pyautogui.position()  # 获取左上角坐标

    # 提示用户点击右下角
    print(f"请设置{region_name}区域的右下角")
    # 创建鼠标监听器
    mouse_listener2 = mouse.Listener(on_click=on_click)
    mouse_listener2.start()
    mouse_listener2.join()
    right_bottom = pyautogui.position()  # 获取右下角坐标

    return (left_top[0], left_top[1], right_bottom[0], right_bottom[1])

if sys_cfg["校准模式"] == 1:
    base.move_window(handle, 0, 0)
    region1 = get_region("事件类型")
    print("region1", region1)
    sys_cfg["事件类型区域"] = list(region1)
    region2 = get_region("事件名")
    sys_cfg["事件名区域"] = list(region2)
    print("region2", region2)
    # 获取屏幕截图
    image = base.window_shot(handle, region=region1)
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    cv2.imwrite("event_type.png", image_bgr)
    image2 = base.window_shot(handle, region=region2)
    image_bgr2 = cv2.cvtColor(image2, cv2.COLOR_RGBA2BGR)
    cv2.imwrite("event_name.png", image_bgr2)
    # 将数据保存到JSON文件
    with open("config.json", "w", encoding="utf-8") as json_file:
        json.dump(sys_cfg, json_file, ensure_ascii=False, indent=4)
    exit(0)

event_type_region = tuple(sys_cfg["事件类型区域"])
event_name_region = tuple(sys_cfg["事件名区域"])

def get_region_text(region, name):
    # 获取屏幕截图
    image = base.window_shot(handle, region=region)
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    cv2.imwrite(name+".png", image_bgr)
    # 识别截图中的文字
    out = ocr.ocr(image)
    # 合并所有text
    out = [elem["text"] for elem in out]
    # 把数组转成字符串，用空格隔开
    out = "".join(out)
    # 删除空格
    out = out.replace(" ", "")
    # 把事件名的所有标点符号去掉
    for punc in "，。！？、；,!?;":
        out = out.replace(punc, "")
    return out

# 读取json文件
with open("./data/data1.json", "r", encoding="utf-8") as f:
    role_config = json.load(f)
with open("./data/card_data.json", "r", encoding="utf-8") as f:
    card_config = json.load(f)

os.system('cls')
print("""
## 注意
+ 使用前需要修改output/config.json中的“模拟器窗口名”字段，改为需要监听的模拟器窗口名
  + win+tab 选择程序窗口的时候，左上角就是各自窗口的名字
+ 为了达到最好的效果，请把模拟器分辨率设置成竖屏 720*1280分辨率
+ 设置好分辨率后，就不要再手动拉伸窗口的大小了，会导致识别错误。
+ 不要最小化模拟器窗口，会导致识别出错。（不要最小化就行，被遮挡或者模拟器窗口不在最上层是没有影响的）

## 如遇到识别问题
+ 打开config.json文件，修改“校准模式”字段为1
+ 再次打开软件就会进入 “校准模式”，根据提示选择对应的识别区域
+ 然后把“校准模式”字段改回0，再次打开工具
""")

# 等待玩家输入
role_name = input("请输入角色名：")
if role_name not in role_config:
    # role_name列表
    role_name_list = []
    # 遍历role_config
    for tmp_role_name in role_config:
        # 找到包含role_name的所有字符串
        if role_name in tmp_role_name:
            role_name_list.append(tmp_role_name)
    print(f"{role_name}未找到，找到如下候选名：")
    # 打印role_name_list同时输出编号
    for i, tmp_role_name in enumerate(role_name_list):
        print(f"{i} {tmp_role_name}")
    role_idx = input(f"请输入对应编号选择:")
    role_name = role_name_list[int(role_idx)]
        
cur_role_cfg = role_config[role_name]
print(f"当前角色为：{role_name}")

# 定义一个表
event_type = {
    "card_event": "协助卡事件",
    "role_event": "养成优俊少女事件",
}
def get_event_type(cur_event_type):
    if cur_event_type == event_type["card_event"]:
        return event_type["card_event"]
    if cur_event_type == event_type["role_event"]:
        return event_type["role_event"]
    if fuzz.ratio(cur_event_type, event_type["card_event"]) > 50:
        return event_type["card_event"]
    if fuzz.ratio(cur_event_type, event_type["role_event"]) > 50:
        return event_type["role_event"]
    return ""

def is_event_change(cur_event_type, last_event_type, cur_event_name, last_event_name):
    if cur_event_type != last_event_type:
        return True
    if cur_event_name != last_event_name:
        return True
    return False

cur_event_type = ""
cur_event_name = ""
last_event_name = ""
last_event_type = ""
try:
    while True:
        # 等待指定的时间间隔
        last_event_name = cur_event_name
        last_event_type = cur_event_type
        time.sleep(interval)
        event_type_name = get_region_text(event_type_region, "event_type")
        cur_event_type = get_event_type(event_type_name)
        cur_event_name = get_region_text(event_name_region, "event_name")
        if not is_event_change(cur_event_type, last_event_type, cur_event_name, last_event_name):
            continue
        os.system('cls')
        if cur_event_type == "":
            print(f"未找到匹配的事件类型: {event_type_name}")
            continue
        if cur_event_name == "":
            print(f"当前事件类型为：[{cur_event_type}]")
            print(f"未检测到事件名: {cur_event_name}")
            continue
        print(f"当前事件类型为：[{cur_event_type}]")
        print(f"当前事件名为：[{cur_event_name}]")
        options = None
        if cur_event_type == "协助卡事件":
            # 遍历所有role_events进行匹配
            max_similarity = 0
            match_event_name = ""
            for role_name, role_cfg in card_config.items():
                if cur_event_name in role_cfg["role_events"]:
                    options = role_cfg["role_events"][cur_event_name]
                    break
                # 进行模糊匹配
                for event_name in role_cfg["role_events"]:
                    # 计算两个字符串的相似度
                    similarity = fuzz.ratio(cur_event_name, event_name)
                    # print(f"[{role_name}] 匹配到的事件名：[{event_name}]，相似度为：{similarity}")
                    if similarity > max_similarity:
                        max_similarity = similarity
                        match_event_name = event_name
                if max_similarity > 50:
                    print(f"匹配的事件名为：[{match_event_name}]，相似度为：{max_similarity}")
                    options = role_cfg["role_events"][match_event_name]
                    break
            if options == None:
                print("未匹配到事件")
                continue
        else:
            if cur_event_name not in cur_role_cfg["role_events"]:
                # 进行模糊匹配
                max_similarity = 0
                match_event_name = ""
                # 遍历role_cfg["role_events"]中的所有事件名
                for event_name in cur_role_cfg["role_events"]:
                    # 计算两个字符串的相似度
                    similarity = fuzz.ratio(cur_event_name, event_name)
                    if similarity > max_similarity:
                        max_similarity = similarity
                        match_event_name = event_name
                if max_similarity < 50:
                    print(f"事件名[{cur_event_name}]不在配置文件中")
                    # 等待指定的时间间隔
                    time.sleep(interval)
                    continue
                print(f"匹配的事件名为：[{match_event_name}]，相似度为：{max_similarity}")
                options = cur_role_cfg["role_events"][match_event_name]
            else:
                options = cur_role_cfg["role_events"][cur_event_name]
        # 遍历options
        for option in options:
            # \n 替换成 \t\n
            option = option.replace("\n", "\n\t")
            print(option)
except KeyboardInterrupt:
    print("结束")