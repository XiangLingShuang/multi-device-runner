# -*- encoding=utf8 -*-
__author__ = "shihao.li"

from airtest.core.api import *
import threading
import time

auto_setup(__file__)

TEMPLATES = {
    "Shanghuo": Template(r"tpl1742546453126.png", record_pos=(-0.264, 0.972), resolution=(720, 1600)),
    "Songhuo": Template(r"tpl1742546447284.png", record_pos=(0.237, 0.979), resolution=(720, 1600)),
    "Xiehuo": Template(r"tpl1742546415906.png", record_pos=(0.007, 0.293), resolution=(720, 1600)),
    "Chenggongjinhuo": Template(r"tpl1742549914833.png", record_pos=(-0.008, 0.432), resolution=(720, 1600)),
    "Enter": Template(r"tpl1742549968872.png", record_pos=(-0.007, 0.469), resolution=(720, 1600)),
    "Next_STEP": Template(r"tpl1742550487157.png", record_pos=(0.0, 0.379), resolution=(720, 1600)),
    "no_Level_up": Template(r"tpl1742550607684.png", record_pos=(-0.01, 0.944), resolution=(720, 1600)),
    "share_game": Template(r"tpl1742799100714.png", record_pos=(0.013, 0.224), resolution=(720, 1600)),
    "shihao_wx": Template(r"tpl1742871647433.png", record_pos=(-0.238, -0.181), resolution=(1080, 2376)),
    "send": Template(r"tpl1742799159140.png", record_pos=(0.156, 0.887), resolution=(720, 1600)),
    "Freebuhuo": Template(r"tpl1742803785852.png", record_pos=(0.0, 0.379), resolution=(720, 1600))
}


def safe_touch(template):
    """带异常处理的点击操作"""
    for retry_count in range(3):
        try:
            if exists(template):
                touch(template)
                print(f"成功点击：{template}")
                return True
        except Exception as e:
            print(f"第 {retry_count + 1} 次点击 {template} 失败，错误信息: {str(e)}")
            # 缩短点击失败后的等待时间
            time.sleep(0.01)
    return False


def handle_xiehuo():
    while True:
        if exists(TEMPLATES["Xiehuo"]):
            safe_touch(TEMPLATES["Xiehuo"])
            safe_touch(TEMPLATES["share_game"])
            safe_touch(TEMPLATES["shihao_wx"])
            safe_touch(TEMPLATES["send"])
            safe_touch(TEMPLATES["Songhuo"])
        # 缩短循环等待时间
        time.sleep(0.01)


def handle_random_templates():
    random_templates = ["Freebuhuo", "no_Level_up", "Next_STEP", "Enter", "Chenggongjinhuo"]
    while True:
        for template_name in random_templates:
            if exists(TEMPLATES[template_name]):
                safe_touch(TEMPLATES[template_name])
        # 缩短循环等待时间
        time.sleep(0.01)


def main():
    # 启动 Xiehuo 处理线程
    xiehuo_thread = threading.Thread(target=handle_xiehuo)
    xiehuo_thread.start()

    # 启动随机模板处理线程
    random_thread = threading.Thread(target=handle_random_templates)
    random_thread.start()

    # 持续点击 Shanghuo
    while True:
        safe_touch(TEMPLATES["Shanghuo"])
        # 缩短循环等待时间
        time.sleep(0.01)


if __name__ == "__main__":
    main()
    