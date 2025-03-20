# -*- encoding=utf8 -*-
__author__ = "shihao.li"

from airtest.core.api import *
import time


# 删除 auto_setup(__file__) 并添加设备连接逻辑
def init_device():
    connect_device("Android:///")  # 显式连接设备


# 定义模板
close_btn = Template(r"tpl1742367847222.png", record_pos=(0.338, -1.0), resolution=(720, 1600), threshold=0.85)
back_btn = Template(r"tpl1742367828722.png", record_pos=(-0.414, -0.965), resolution=(720, 1600), threshold=0.85)
popup = Template(r"tpl1742370712113.png", record_pos=(0.008, -0.053), resolution=(720, 1600), threshold=0.85)
close_popup_btn = Template(r"tpl1742370722473.png", record_pos=(0.314, -0.194), resolution=(720, 1600), threshold=0.85)


# 函数定义（不直接调用）
def close_douyin_ad():
    total_time = 35
    interval = 5
    start_time = time.time()

    while time.time() - start_time < total_time:
        if int(time.time() - start_time) % interval == 0:
            # 优先处理弹窗
            if exists(popup):
                if exists(close_popup_btn):
                    touch(close_popup_btn)
                else:
                    if exists(back_btn):
                        touch(back_btn)
                        break

            # 检查返回按钮
            if exists(back_btn):
                if exists(back_btn):
                    touch(back_btn)
                else:
                    if exists(close_btn):
                        touch(close_btn)
                        break

                        # 检查关闭按钮
            if exists(close_btn):
                touch(close_btn)
                break

        sleep(1)

