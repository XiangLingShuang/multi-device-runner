# -*- encoding=utf8 -*-
__author__ = "shihao.li"

from airtest.core.api import *
import threading
import time

auto_setup(__file__)

TEMPLATES = {
    "Boom": Template(r"tpl1742956640569.png", record_pos=(0.355, 0.931), resolution=(1080, 2376)),
    "share_game": Template(r"tpl1742957751260.png", record_pos=(-0.002, 0.235), resolution=(1080, 2376)),
    "shihao_wx": Template(r"tpl1742957521028.png", record_pos=(-0.236, -0.172), resolution=(1080, 2376)),
    "send": Template(r"tpl1742957662680.png", record_pos=(0.168, 0.879), resolution=(1080, 2376)),
    "Next": Template(r"tpl1742960355078.png", record_pos=(0.223, 0.48), resolution=(1080, 2376)),
    "NextStep": Template(r"tpl1742960380053.png", record_pos=(-0.002, 0.686), resolution=(1080, 2376))
}


def ADWX():
    touch(TEMPLATES["share_game"])
    touch(TEMPLATES["shihao_wx"])
    touch(TEMPLATES["send"])


def monitor_next():
    while True:
        if exists(TEMPLATES["Next"]):
            touch(TEMPLATES["Next"])
        if exists(TEMPLATES["NextStep"]):
            touch(TEMPLATES["NextStep"])
        time.sleep(0.1)


if __name__ == "__main__":
    # 启动主逻辑线程
    def main_logic():
        while True:
            if exists(TEMPLATES["Boom"]):
                touch(TEMPLATES["Boom"])
            if exists(TEMPLATES["share_game"]):
                ADWX()
            time.sleep(0.1)

    # 创建并启动主逻辑线程
    main_thread = threading.Thread(target=main_logic)
    main_thread.start()

    # 创建并启动 Next 和 NextStep 监测线程
    next_monitor_thread = threading.Thread(target=monitor_next)
    next_monitor_thread.start()

    try:
        # 让主线程等待子线程结束
        main_thread.join()
        next_monitor_thread.join()
    except KeyboardInterrupt:
        print("程序已手动终止")
