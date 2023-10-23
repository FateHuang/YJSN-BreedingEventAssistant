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
base.resize_client(handle, 540, 960)
# base.move_window(handle, 0, 0)

event_type_region = (90, 185, 251, 206)
event_name_region = (90, 206, 411, 241)

def get_region_text(region):
    # 获取屏幕截图
    image = base.window_shot(handle, region=region)
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
        event_type_name = get_region_text(event_type_region)
        cur_event_type = get_event_type(event_type_name)
        cur_event_name = get_region_text(event_name_region)
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