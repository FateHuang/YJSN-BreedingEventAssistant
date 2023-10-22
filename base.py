import os
import time
import pyautogui
import win32gui
import win32con
from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND
import numpy as np
import cv2

GetDC = windll.user32.GetDC
CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
GetClientRect = windll.user32.GetClientRect
CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
SelectObject = windll.gdi32.SelectObject
BitBlt = windll.gdi32.BitBlt
SRCCOPY = 0x00CC0020
GetBitmapBits = windll.gdi32.GetBitmapBits
DeleteObject = windll.gdi32.DeleteObject
ReleaseDC = windll.user32.ReleaseDC

# 排除缩放干扰
windll.user32.SetProcessDPIAware()

""" 
+ win10截图快捷键： win+shift+s
 """

imgPath = "../img/"

def waitFor(iconName, conf=None, isNotClick=False):
    path = imgPath+iconName
    print("wait for "+iconName)
    while True:
        picLocation = None
        if conf == None:
            picLocation = pyautogui.locateOnScreen(path)
        else:
            picLocation = pyautogui.locateOnScreen(path, confidence=conf)
        if picLocation:
            if not isNotClick:
                centerPos = pyautogui.center(picLocation)
                pyautogui.click(centerPos)
                print("clicked "+iconName)
            break
        time.sleep(1)

def click(left, top, right, bottom, left_right='left'):
    width = right - left
    height = bottom - top
    click_x = left + width // 2
    click_y = top + height // 2
    pyautogui.click((click_x, click_y), button=left_right)


# 获取鼠标的当前坐标
def getMousePos():
    return pyautogui.position()

# 打印鼠标所在控件的信息
def dump_cursor_window():
    time.sleep(5)
    # 获取当前鼠标位置
    x, y = win32gui.GetCursorPos()

    # 获取鼠标所在位置的窗口句柄
    hwnd = win32gui.WindowFromPoint((x, y))

    # 获取控件的类名和文本
    class_name = win32gui.GetClassName(hwnd)
    text = win32gui.GetWindowText(hwnd)

    # 获取控件的坐标信息
    rect = win32gui.GetWindowRect(hwnd)
    left, top, right, bottom = rect

    print(f"Mouse Position: ({x}, {y})")
    print(f"Control Information:")
    print(f"  Class Name: {class_name}")
    print(f"  Text: {text}")
    print(f"  Control Position: Left={left}, Top={top}, Right={right}, Bottom={bottom}")


def goto_file_path(file_path):
    # 找到文件资源管理器窗口
    className = "CabinetWClass"
    hWnd = win32gui.FindWindow(className, None)
    if hWnd:
        print(f"Found window with class '{className}': {hWnd}")
    else:
        print(f"No window with class '{className}' found")
        exit(1)
    # 设置窗口为最顶层
    win32gui.SetForegroundWindow(hWnd)
    # 窗口最大化
    win32gui.ShowWindow(hWnd, win32con.SW_MAXIMIZE)
    # 定义回调函数来处理每个控件
    def click_addr_bar(hwnd, lParam):
        text = win32gui.GetWindowText(hwnd)
        if text.find('地址:') != -1:
            print(f"Found address bar: {text}")
            # 点击控件
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            click(left, top, right, bottom)
            pyautogui.write(file_path)
            pyautogui.press('enter')
            return True
        # 打印控件信息
        # print(f"Class: {win32gui.GetClassName(hwnd)}, Text: {text}")
    win32gui.EnumChildWindows(hWnd, click_addr_bar, None)
    return hWnd

def capture(handle: HWND):
    """窗口客户区截图

    Args:
        handle (HWND): 要截图的窗口句柄

    Returns:
        numpy.ndarray: 截图数据
    """
    # 获取窗口客户区的大小
    r = RECT()
    GetClientRect(handle, byref(r))
    width, height = r.right, r.bottom
    # 开始截图
    dc = GetDC(handle)
    cdc = CreateCompatibleDC(dc)
    bitmap = CreateCompatibleBitmap(dc, width, height)
    SelectObject(cdc, bitmap)
    BitBlt(cdc, 0, 0, width, height, dc, 0, 0, SRCCOPY)
    # 截图是BGRA排列，因此总元素个数需要乘以4
    total_bytes = width*height*4
    buffer = bytearray(total_bytes)
    byte_array = c_ubyte*total_bytes
    GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))
    DeleteObject(bitmap)
    DeleteObject(cdc)
    ReleaseDC(handle, dc)
    # 返回截图数据为numpy.ndarray
    return np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)

def window_shot(handle, region):
    image = capture(handle)
    if region:
        left, top, right, bottom = region
        image = image[top:bottom, left:right]
    return image

SetWindowPos = windll.user32.SetWindowPos
GetClientRect = windll.user32.GetClientRect
GetWindowRect = windll.user32.GetWindowRect
EnableWindow = windll.user32.EnableWindow

SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0X0002
SWP_NOZORDER = 0x0004

def resize_window(handle: HWND, width: int, height: int):
    """设置窗口大小为width × height

    Args:
        handle (HWND): 窗口句柄
        width (int): 宽
        height (int): 高
    """
    SetWindowPos(handle, 0, 0, 0, width, height, SWP_NOMOVE | SWP_NOZORDER)

def resize_client(handle: HWND, width: int, height: int):
    """设置客户区大小为width × height

    Args:
        handle (HWND): 窗口句柄
        width (int): 宽
        height (int): 高
    """
    client_rect = RECT()
    GetClientRect(handle, byref(client_rect))
    delta_w = width - client_rect.right
    delta_h = height - client_rect.bottom
    window_rect = RECT()
    GetWindowRect(handle, byref(window_rect))
    current_width = window_rect.right - window_rect.left
    current_height = window_rect.bottom - window_rect.top
    resize_window(handle, current_width+delta_w, current_height+delta_h)

def move_window(handle: HWND, x: int, y: int):
    """移动窗口到坐标(x, y)

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    SetWindowPos(handle, 0, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER)