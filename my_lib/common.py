import sys
import threading
from airtest.core.android.adb import *
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
        # 1. 初始化线程控制事件
        # 全局停止事件，用于控制所有线程
        global_stop = threading.Event()
        # 为每个子模板创建独立停止事件
        sub_stops = {template: threading.Event() for template in sub_templates}

        # 2. 定义主按钮监控线程函数
        def main_monitor():
            # 等待初始延迟
            sleep(initial_wait)
            # 持续监控直到全局停止
            while not global_stop.is_set():
                # 检查主按钮是否存在
                if exists(main_template):
                    # 点击主按钮并设置全局停止
                    touch(main_template)
                    global_stop.set()
                    break
                # 注释掉的sleep(1)可根据需要取消注释以降低CPU使用率

        # 3. 定义子按钮监控线程函数
        def sub_monitor(template):
            # 等待初始延迟
            sleep(initial_wait)
            # 持续监控直到全局停止或本线程被停止
            while not global_stop.is_set() and not sub_stops[template].is_set():
                # 检查子按钮是否存在
                if exists(template):
                    # 点击子按钮并设置本线程停止
                    touch(template)
                    sub_stops[template].set()
                    break
                # 注释掉的sleep(1)可根据需要取消注释以降低CPU使用率

        # 4. 启动所有监控线程
        # 创建并启动主按钮监控线程
        main_thread = threading.Thread(target=main_monitor)
        # 为每个子模板创建并启动监控线程
        sub_threads = [threading.Thread(target=sub_monitor, args=(t,)) for t in sub_templates]

        main_thread.start()
        for t in sub_threads:
            t.start()

        # 5. 超时控制逻辑
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 如果全局已停止则提前退出
            if global_stop.is_set():
                break
            sleep(1)  # 每秒检查一次

        # 6. 清理资源
        # 设置全局停止标志
        global_stop.set()
        # 设置所有子线程停止标志
        for stop in sub_stops.values():
            stop.set()
        # 等待主线程结束（最多5秒）
        main_thread.join(timeout=5)
        # 等待所有子线程结束（最多5秒）
        for t in sub_threads:
            t.join(timeout=5)

    return monitor


def set_project_root():
    """自动设置项目根目录并添加到Python模块搜索路径。

    该函数通过以下步骤确定项目根目录：
    1. 获取当前脚本的绝对路径（解析符号链接）
    2. 获取脚本所在目录
    3. 获取上级目录作为项目根目录
    4. 将项目根目录添加到sys.path中

    使用示例:
        set_project_root()
        # 之后可以直接导入项目根目录下的模块

    注意:
        - 该函数假设项目根目录是当前脚本所在目录的上级目录
        - 调用后会打印出项目根目录路径
    """
    # 获取当前脚本的绝对路径并解析符号链接
    script_path = os.path.realpath(__file__)
    # 获取脚本所在目录
    current_dir = os.path.dirname(script_path)
    # 获取上级目录作为项目根目录
    project_root = os.path.dirname(current_dir)
    print(f"项目根目录: {project_root}")
    sys.path.append(project_root)










# def close_douyin_ad():
#     """
#     抖音广告关闭优化方案（精确控制版）
#     1. 关闭按钮线程拥有最高优先级，点击后终止所有监控
#     2. 返回按钮线程独立运行，点击后仅终止自己
#     3. 主线程设置总超时时间
#     """
#     # 模板定义
#     close_btn = Template(r"douyin_ad_close.png", record_pos=(0.34, -0.944), resolution=(1264, 2780))
#     back_btn = Template(r"douyin_ad_back.png", record_pos=(-0.422, -0.921), resolution=(1264, 2780))
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