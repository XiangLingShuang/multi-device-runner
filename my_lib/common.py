import threading

from airtest.core.api import *


def touch_template(template, timeout=30, interval=2, stop_thread=None):
    """
    通用的点击模板函数
    :param template: Template对象，表示要点击的模板
    :param timeout: 超时时间，单位为秒
    :param interval: 检查间隔，单位为秒
    :param stop_thread: threading.Event对象，用于控制线程的停止
    """
    while stop_thread is None or not stop_thread.is_set():
        if wait(template, timeout=timeout, interval=interval):
            touch(template)
            break


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
                # sleep(1)

        # 子按钮监控
        def sub_monitor(template):
            sleep(initial_wait)
            while not global_stop.is_set() and not sub_stops[template].is_set():

                if exists(template):
                    touch(template)
                    sub_stops[template].set()
                    break
                # sleep(1)

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

# def close_douyin_ad():
#     """
#     抖音广告关闭优化方案（精确控制版）
#     1. 关闭按钮线程拥有最高优先级，点击后终止所有监控
#     2. 返回按钮线程独立运行，点击后仅终止自己
#     3. 主线程设置总超时时间
#     """
#     # 模板定义
#     close_btn = Template(r"close_ad_button.png", record_pos=(0.34, -0.944), resolution=(1264, 2780))
#     back_btn = Template(r"back_ad_button.png", record_pos=(-0.422, -0.921), resolution=(1264, 2780))
#
#     # 事件控制
#     global_stop = threading.Event()  # 全局停止信号
#     back_stop = threading.Event()  # 返回按钮专用停止信号
#
#     def monitor_close():
#         """ 关闭按钮监控线程 """
#         while not global_stop.is_set():
#             if exists(close_btn):
#                 touch(close_btn)
#                 global_stop.set()  # 触发全局停止
#                 break
#             sleep(1)
#
#     def monitor_back():
#         """ 返回按钮监控线程 """
#         while not global_stop.is_set() and not back_stop.is_set():
#             if exists(back_btn):
#                 touch(back_btn)
#                 back_stop.set()  # 仅停止本线程
#                 break
#             sleep(1)
#
#     # 启动监控
#     sleep(25)  # 25秒后开始监控（总30秒广告-5秒缓冲）
#
#     close_thread = threading.Thread(target=monitor_close)
#     back_thread = threading.Thread(target=monitor_back)
#
#     close_thread.start()
#     back_thread.start()
#
#     # 设置总超时（最长等待60秒）
#     start_time = time.time()
#     while time.time() - start_time < 60:
#         if global_stop.is_set():
#             break
#         sleep(1)
#
#     # 最终清理
#     global_stop.set()
#     back_stop.set()
#     close_thread.join(timeout=5)
#     back_thread.join(timeout=5)
