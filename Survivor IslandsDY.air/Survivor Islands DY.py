# -*- encoding=utf8 -*-
__author__ = "shihao.li"

from airtest.core.api import *
import sys
import time
import logging
import threading

# 初始化设备连接
connect_device("Android:///")  # 显式连接设备
auto_setup(__file__)

# 导入模块
# sys.path.append(r'C:\SHIHAO\AirtestIDE\Scripts\Survivor IslandsDY.air\CloseAD.air')
using(r"Survivor IslandsDY.air/CloseAD.air/CloseAD.py")
from CloseAD import close_douyin_ad, init_device

# 初始化设备（确保连接）
init_device()

def code_A():
    touch(Template(r"tpl1742283671257.png", record_pos=(-0.408, 0.708), resolution=(720, 1600)))
    sleep(1)
    if exists(Template(r"tpl1742283757134.png", record_pos=(0.003, 0.164), resolution=(720, 1600))):
        touch(Template(r"tpl1742283772961.png", record_pos=(-0.26, 0.84), resolution=(720, 1600)))
        sleep(1)
        close_douyin_ad()
        sleep(1)
        if exists(Template(r"tpl1742284053071.png", record_pos=(0.0, 0.889), resolution=(720, 1600))):  # 修复行：添加冒号
            touch(Template(r"tpl1742284053071.png", record_pos=(0.0, 0.889), resolution=(720, 1600)))
            sleep(1)
            if exists(Template(r"tpl1742293962300.png", record_pos=(0.424, -0.789), resolution=(720, 1600))):
                touch(Template(r"tpl1742291549047.png", record_pos=(0.418, -0.792), resolution=(720, 1600)))
        elif exists(Template(r"tpl1742293962300.png", record_pos=(0.424, -0.789), resolution=(720, 1600))):
            touch(Template(r"tpl1742291549047.png", record_pos=(0.418, -0.792), resolution=(720, 1600)))

def code_B():
    if exists(Template(r"tpl1742452116118.png", record_pos=(0.418, -0.669), resolution=(720, 1600))) or \
       exists(Template(r"tpl1742286023776.png", record_pos=(0.417, -0.65), resolution=(720, 1600))):
        if exists(Template(r"tpl1742286023776.png", threshold=0.8)):
            touch(Template(r"tpl1742286023776.png"))
        elif exists(Template(r"tpl1742452116118.png", threshold=0.8)):
            touch(Template(r"tpl1742452116118.png"))
        sleep(1)
        if exists(Template(r"tpl1742286042790.png", record_pos=(-0.003, 0.344), resolution=(720, 1600))):
            touch(Template(r"tpl1742286042790.png"))
        close_douyin_ad()
        sleep(5)

def code_C():
    touch(Template(r"tpl1742283671257.png", record_pos=(-0.408, 0.708), resolution=(720, 1600)))
    sleep(1)
    if exists(Template(r"tpl1742283757134.png", record_pos=(0.003, 0.164), resolution=(720, 1600))):
        touch(Template(r"tpl1742287159759.png", record_pos=(-0.315, -0.406), resolution=(720, 1600)))
        sleep(1)
        if exists(Template(r"tpl1742288268861.png", record_pos=(-0.011, 0.322), resolution=(720, 1600))):
            close_douyin_ad()
            sleep(40)
            touch(Template(r"tpl1742288357121.png", record_pos=(-0.006, 0.714), resolution=(720, 1600)))
            sleep(1)
            touch(Template(r"tpl1742288385557.png", record_pos=(0.367, -0.365), resolution=(720, 1600)))
            sleep(1)
            touch(Template(r"tpl1742287859442.png", record_pos=(0.419, -0.792), resolution=(720, 1600)))
            touch(Template(r"tpl1742288268861.png", record_pos=(-0.011, 0.322), resolution=(720, 1600)))
        elif exists(Template(r"tpl1742292469738.png", record_pos=(-0.019, 0.311), resolution=(720, 1600))):
            touch(Template(r"tpl1742292490806.png", record_pos=(-0.015, 0.318), resolution=(720, 1600)))
            close_douyin_ad()
            sleep(40)
            touch(Template(r"tpl1742288357121.png", record_pos=(-0.006, 0.714), resolution=(720, 1600)))
            sleep(1)
            touch(Template(r"tpl1742292769942.png", record_pos=(-0.003, 0.311), resolution=(720, 1600)))
            close_douyin_ad()
            sleep(40)
            touch(Template(r"tpl1742288357121.png", record_pos=(-0.006, 0.714), resolution=(720, 1600)))
            sleep(1)
            touch(Template(r"tpl1742288385557.png", record_pos=(0.367, -0.365), resolution=(720, 1600)))
            sleep(1)
            touch(Template(r"tpl1742287859442.png", record_pos=(0.419, -0.792), resolution=(720, 1600)))

start_time = time.time()

while True:
    try:
        elapsed_time = time.time() - start_time
        if elapsed_time % 247 < 1:
            code_B()
        elif elapsed_time % 7300 < 1:
            code_C()
        elif elapsed_time % 400 < 1:
            code_A()
        time.sleep(1)
    except Exception as e:
        print(f"发生异常: {str(e)}")
        init_device()