# -*- encoding=utf8 -*-
__author__ = "shihao.li"

from airtest.core.api import *
import threading
import time

auto_setup(__file__)

# 定义模板（通过字典键名访问）
TEMPLATES = {
    "close_btn": Template(r"tpl1742367847222.png",
                          record_pos=(0.338, -1.0),
                          resolution=(720, 1600),
                          threshold=0.8),  # 降低阈值提高容错
    "back_btn": Template(r"tpl1742367828722.png",
                         record_pos=(-0.414, -0.965),
                         resolution=(720, 1600),
                         threshold=0.8),
    "popup": Template(r"tpl1742370712113.png",
                      record_pos=(0.008, -0.053),
                      resolution=(720, 1600),
                      threshold=0.75),
    "close_popup_btn": Template(r"tpl1742370722473.png",
                                record_pos=(0.314, -0.194),
                                resolution=(720, 1600),
                                threshold=0.8),
#    "close_buttom_AD_btn":Template(r"tpl1742527829192.png", record_pos=(0.353, 1.007), resolution=(720, 1600)),
#     "jump_Pop-up_ad_in_the_middle1": Template(r"tpl1742527895660.png", record_pos=(0.324, 0.043), resolution=(720, 1600)),
#     "close_Pop-up_ad_in_the_middle":Template(r"tpl1742527989848.png", record_pos=(0.339, -0.518), resolution=(720, 1600)),
#     "jump_Pop-up_ad_in_the_middle2":Template(r"tpl1742528050448.png", record_pos=(0.357, -0.721), resolution=(720, 1600)),
#     "close_Pop-up_ad_next":Template(r"tpl1742528485803.png", record_pos=(-0.003, 0.249), resolution=(720, 1600)),
#     "close_Pop-up_ad_in_the_middle2":Template(r"tpl1742528172446.png", record_pos=(0.426, -0.94), resolution=(720, 1600)),
#     #"jump_other_app":Template(r"tpl1742528912999.png", record_pos=(-0.029, 0.233), resolution=(720, 1600)),
#     #"jump_other_app_STEP2":Template(r"tpl1742529110148.png", record_pos=(-0.021, 0.229), resolution=(720, 1600)),
#     "un_Interest":Template(r"tpl1742529387761.png", record_pos=(-0.336, -0.336), resolution=(720, 1600)),
#     "close_right_corner":Template(r"tpl1742529547837.png", record_pos=(0.415, -0.943), resolution=(720, 1600))
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
            time.sleep(0.2)
    return False


def check_and_touch(target_template, action_template=None):
    """检查目标模板是否存在并执行点击操作"""
    if exists(target_template):
        target = action_template if action_template else target_template
        safe_touch(target)


def template_watcher(target_template, action_template=None):
    """独立模板监视器，每秒检查一次"""
    while True:
        check_and_touch(target_template, action_template)
        time.sleep(1)


def run_close_ad_monitor():
    threads = []
    for key, template in TEMPLATES.items():
        if key == "popup":
            action_template = TEMPLATES["close_popup_btn"]
        else:
            action_template = None
        t = threading.Thread(target=template_watcher, args=(template, action_template))
        t.start()
        threads.append(t)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("程序已手动终止")

#把他封装为了其他的脚本调用
if __name__ == "__main__":
    run_close_ad_monitor()