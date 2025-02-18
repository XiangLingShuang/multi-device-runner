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