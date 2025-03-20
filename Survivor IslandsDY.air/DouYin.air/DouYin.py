import threading
import logging

# logger = logging.getLogger("airtest")
# logger.setLevel(logging.ERROR)

from airtest.core.api import *


def touch_template(template, stop_thread):
    """
    通用的点击模板函数
    :param template: Template对象，表示要点击的模板
    :param stop_thread: threading.Event对象，用于控制线程的停止
    """
    while not stop_thread.is_set():
        if exists(template):
            touch(template)
            break
        sleep(2)  # 每2秒检查一次，减少CPU占用


def create_button_monitor(main_template, sub_templates, timeout=60, initial_wait=0):
    """
    创建通用按钮监控器
    :param main_template: 主按钮模板（点击后停止所有线程）
    :param sub_templates: 子按钮模板列表（点击后仅停止自己线程）
    :param timeout: 总超时时间（秒）
    :param initial_wait: 初始等待时间（秒）
    :return: 执行监控的函数
    """

    def monitor():
        # 事件控制
        global_stop = threading.Event()
        sub_stops = {template: threading.Event() for template in sub_templates}

        # 主按钮监控
        def main_monitor():
            sleep(initial_wait)
            while not global_stop.is_set():
                if exists(main_template):
                    touch(main_template)
                    global_stop.set()
                    break
                sleep(1)

        # 子按钮监控
        def sub_monitor(template):
            sleep(initial_wait)
            while not global_stop.is_set() and not sub_stops[template].is_set():
                if exists(template):
                    touch(template)
                    sub_stops[template].set()
                    break
                sleep(1)

        # 启动线程
        main_thread = threading.Thread(target=main_monitor)
        sub_threads = [threading.Thread(target=sub_monitor, args=(t,)) for t in sub_templates]

        main_thread.start()
        for t in sub_threads:
            t.start()

        # 超时控制
        start_time = time.time()
        while time.time() - start_time < timeout:
            if global_stop.is_set():
                break
            sleep(1)

        # 清理资源
        global_stop.set()
        for stop in sub_stops.values():
            stop.set()
        main_thread.join(timeout=5)
        for t in sub_threads:
            t.join(timeout=5)

    return monitor


# 原close_douyin_ad函数可改造为：
def close_douyin_ad():
    close_btn = Template(r"tpl1742367847222.png", record_pos=(0.338, -1.0), resolution=(720, 1600),threshold=0.85)
    back_btn = Template(r"tpl1742367828722.png", record_pos=(-0.414, -0.965), resolution=(720, 1600),threshold=0.85)   


    monitor = create_button_monitor(
        main_template=close_btn,
        sub_templates=[back_btn],
        timeout=60,
        initial_wait=25
    )
    monitor()
    
if __name__ == "__main__":

    close_douyin_ad()