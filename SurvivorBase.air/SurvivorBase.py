import threading

from airtest.core.android import Android, android
from airtest.core.android.adb import ADB
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


def click_offline_reward():
    """
    点击离线奖励按钮
    """
    offline_reward_button = Template(r"Pictures/offline_reward_button.png",
                                     record_pos=(-0.241, 0.677), resolution=(1264, 2780), threshold=0.85)
    offline_reward_interface = Template(r"Pictures/offline_reward_interface.png",
                                        record_pos=(0.0, 0.0), resolution=(1264, 2780), threshold=0.85)

    if exists(offline_reward_interface):
        touch(offline_reward_button)
        log("点击离线奖励领取按钮")
        sleep(2)


def click_offline_ad_reward():
    """
    点击离线广告奖励按钮
    """
    offline_ad_reward_button = Template(r"Pictures/offline_ad_reward_button.png",
                                        record_pos=(0.237, 0.679), resolution=(1264, 2780), threshold=0.85)
    offline_reward_interface = Template(r"Pictures/offline_reward_interface.png",
                                        record_pos=(0.0, 0.0), resolution=(1264, 2780), threshold=0.85)
    try:
        if exists(offline_reward_interface):
            offline_ad_reward_button_pos = assert_exists(offline_ad_reward_button)
            touch(offline_ad_reward_button_pos)
            close_douyin_ad()
            log("点击离线奖励领取按钮")
    except AssertionError as e:
        log(f"断言错误: {str(e)}")
    except Exception as e:
        log(f"点击离线广告奖励按钮时发生错误: {str(e)}")


# 原close_douyin_ad函数可改造为：
def close_douyin_ad():
    close_btn = Template(r"Pictures/close_ad_button.png",
                         record_pos=(0.34, -0.944), resolution=(1264, 2780), threshold=0.85)
    back_btn = Template(r"Pictures/back_ad_button.png",
                        record_pos=(-0.422, -0.921), resolution=(1264, 2780), threshold=0.85)

    monitor = create_button_monitor(
        main_template=close_btn,
        sub_templates=[back_btn],
        timeout=60,
        initial_wait=25
    )
    monitor()


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


def check_main_screen():
    """
    检查是否进入主界面
    """
    '''
    代办：后续替换成下方全部截图，提高准确度
    '''

    build_button = Template(r"Pictures/build.png",
                            record_pos=(0.001, 0.986), resolution=(1264, 2780), threshold=0.85)
    right_button = Template(r"Pictures/setting.png",
                            record_pos=(0.435, 0.06), resolution=(1080, 2376), threshold=0.85)

    wait(build_button)
    if exists(right_button):
        log("进入主界面")
        return True
    else:
        log("未进入主界面")
        return False


def click_work_efficiency_ad():
    """
    工作效率的广告领取按钮
    """
    work_efficiency_entrance = Template(r"Pictures/work_efficiency_entrance.png",
                                        record_pos=(0.406, -0.601), resolution=(1264, 2780), threshold=0.85)
    diamond_increases_time = Template(r"Pictures/diamond_increases_time.png",
                                      record_pos=(-0.236, 0.356), resolution=(1264, 2780), threshold=0.85)
    ad_increases_time = Template(r"Pictures/ad_increases_time.png",
                                 record_pos=(0.237, 0.345), resolution=(1264, 2780), threshold=0.85)
    close_button = Template(r"Pictures/close_button.png",
                            record_pos=(0.428, -0.545), resolution=(1080, 2376), threshold=0.85)  # 弹窗关闭按钮
    try:
        if check_main_screen():
            touch(work_efficiency_entrance)
            ad_increases_time_pos = exists(diamond_increases_time)
            if ad_increases_time_pos:
                touch(ad_increases_time_pos)
                close_douyin_ad()
            else:
                log("未找到广告按钮")
                close_button_pos = exists(close_button)
                if close_button_pos:
                    touch(close_button_pos)
                return
        else:
            log("未进入主界面，无法点击工作效率的广告领取按钮")
            return
    except Exception as e:
        log(f"点击工作效率广告时发生错误: {str(e)}")

        return


def click_to_search():
    """
    点击搜寻按钮（主界面功能）
    处理游戏中的幸存者搜寻流程，包含正常搜寻和广告搜寻两种路径
    执行逻辑：
    1. 检查是否在主界面
    2. 进入搜寻界面并点击搜寻按钮
    3. 根据是否存在广告按钮决定执行路径：
       - 有广告按钮：点击广告并关闭后续弹窗
       - 无广告按钮：关闭当前界面
    :return: 无返回值
    """
    # 界面元素模板定义（分辨率1080x2376对应测试设备）
    search_entrance = Template(r"Pictures/search_entrance.png",
                               record_pos=(0.403, -0.467), resolution=(1080, 2376), threshold=0.85)  # 主界面入口按钮
    search_button = Template(r"Pictures/search_button.png",
                             record_pos=(0.003, 0.289), resolution=(1080, 2376), threshold=0.85)  # 普通搜寻按钮
    search_ad_button = Template(r"Pictures/search_ad_button.png",
                                record_pos=(0.0, 0.29), resolution=(1080, 2376), threshold=0.85)  # 广告立刻完成搜寻按钮
    search_close_button = Template(r"Pictures/search_close_button.png",
                                   record_pos=(0.423, -0.363), resolution=(1080, 2376), threshold=0.85)  # 搜寻窗口关闭按钮

    try:
        if check_main_screen():
            # 进入搜寻界面并执行首次点击
            touch(search_entrance)
            touch(search_button)

            # 判断广告按钮存在状态

            if exists(search_button):
                # 无可用广告时的处理
                touch(search_close_button)
                log("暂无幸存者需要搜寻")
            else:
                # 广告搜寻流程
                touch(search_entrance)  # 重新进入确保界面状态
                touch(search_ad_button)
                close_douyin_ad()  # 处理广告关闭
        else:
            log("未进入主界面，无法点击搜寻按钮")
            return
    except Exception as e:
        log(f"点击搜寻按钮时发生错误: {str(e)}")


def click_sign_in_reword():
    """
    处理游戏签到功能
    功能流程：
    1. 进入签到界面并完成签到
    2. 领取可用奖励
    3. 尝试补签并观看广告
    4. 领取补签奖励
    5. 关闭签到界面
    """
    # 定义所需的UI模板
    sign_in_entrance = Template(r"Pictures/sign_in_entrance.png",
                                record_pos=(0.411, -0.31), resolution=(1080, 2376), threshold=0.85)  # 主界面签到入口按钮
    sign_in_button = Template(r"Pictures/sign_in_button.png",
                              record_pos=(-0.254, 0.506), resolution=(1080, 2376), threshold=0.85)  # 签到弹窗中的确认签到按钮
    claim_button = Template(r"Pictures/claim_button.png",
                            record_pos=(-0.003, 0.869), resolution=(1080, 2376), threshold=0.85)  # 奖励领取按钮
    supplementary_signature_button = Template(r"Pictures/supplementary_signature_button.png",
                                              record_pos=(0.251, 0.488), resolution=(1080, 2376),
                                              threshold=0.85)  # 补签操作按钮
    close_button = Template(r"Pictures/close_button.png",
                            record_pos=(0.428, -0.545), resolution=(1080, 2376), threshold=0.85)  # 弹窗关闭按钮

    try:
        # 检查是否在主界面
        if not check_main_screen():
            log("未在主界面，无法进行签到操作")
            return

        # 进入签到界面流程
        try:
            touch(sign_in_entrance)  # 点击签到入口
            sleep(1)  # 等待界面加载

            sign_in_button_pos = exists(sign_in_button)
            if sign_in_button_pos:
                touch(sign_in_button_pos)  # 执行签到
                # 处理奖励领取逻辑
                claim_button_pos = exists(claim_button)
                if claim_button_pos:
                    touch(claim_button_pos)
                    log("领取签到奖励")
                log("完成每日签到")
            else:
                log("未找到签到按钮")
        except Exception as e:
            log(f"签到过程出错: {str(e)}")

        # 执行补签操作
        try:
            supplementary_button_pos = exists(supplementary_signature_button)
            if supplementary_button_pos:
                touch(supplementary_button_pos)
                log("开始补签流程")
                close_douyin_ad()  # 处理广告
                # 领取奖励
                claim_button_pos = exists(claim_button)
                if claim_button_pos:
                    touch(claim_button_pos)
                    log("领取补签奖励")
            else:
                log("无需补签或补签按钮未找到")
        except Exception as e:
            log(f"补签过程出错: {str(e)}")

        # 关闭界面
        close_button_pos = exists(close_button)
        if close_button_pos:
            touch(close_button_pos)
            log("签到流程完成")
        else:
            log("未找到关闭按钮")

    except Exception as e:
        log(f"签到功能执行出错: {str(e)}")
        # 尝试关闭界面
        close_button_pos = exists(close_button)
        if close_button_pos:
            touch(close_button_pos)


def click_shop():
    shop_entrance = Template(r"Pictures/shop_entrance.png",
                             record_pos=(-0.41, 0.836), resolution=(1080, 2376), threshold=0.85)
    shop_close_button = Template(r"Pictures/shop_close_button.png", record_pos=(-0.448, -0.988),
                                 resolution=(1080, 2376), threshold=0.85)
    material_supply = Template(r"Pictures/material_supply.png",
                               record_pos=(-0.001, -0.549), resolution=(1080, 2376), threshold=0.85)
    diamond_10 = Template(r"Pictures/diamond_10.png",
                          record_pos=(-0.16, 0.67), resolution=(1080, 2376), threshold=0.85)
    diamond_88 = Template(r"Pictures/diamond_88.png",
                          record_pos=(0.162, 0.657), resolution=(1080, 2376), threshold=0.85)
    claim_button = Template(r"Pictures/claim_button.png",
                            record_pos=(0.002, 0.881), resolution=(1080, 2376), threshold=0.85)

    try:
        if check_main_screen():
            # pos = (0.09,0.88)
            # shop_entrance_pos = exists(shop_entrance)
            shop_entrance_pos = False
            if shop_entrance_pos:
                touch(shop_entrance_pos)
            else:
                touch([0.09, 0.88])
            if exists(diamond_10):
                touch(diamond_10)
                close_douyin_ad()
                if exists(claim_button):
                    touch(claim_button)
            else:
                pass

            if exists(diamond_88):
                touch(diamond_88)
                close_douyin_ad()
                if exists(claim_button):
                    touch(claim_button)
                    return
            touch(shop_close_button)
            log("商店功能执行完成")
    except Exception as e:
        log(f"商店功能执行出错: {str(e)}")


def click_build():
    # 初始化UI元素模板
    build_entrance = Template(filename=r"Pictures/build.png",
                              record_pos=(0.001, 0.986), resolution=(1264, 2780), threshold=0.85)
    build_close_button = Template(filename=r"Pictures/close_button.png",
                                  record_pos=(0.436, -0.397), resolution=(1080, 2376), threshold=0.85)
    build_button = Template(filename=r"build_button.png",
                            record_pos=(0.356, 0.136), resolution=(1080, 2376), threshold=0.85)

    try:
        # 检查主界面状态
        if check_main_screen():
            # 点击建造入口
            touch(build_entrance)
            sleep(1)

            # 检测建造按钮是否存在
            if exists(build_button):
                # 执行建造操作
                touch(build_button)
                touch([0.56, 0.56])  # 点击确认位置
                log("建造成功")
            else:
                # 关闭建造界面
                touch(build_close_button)
    except Exception as e:
        # 异常处理
        log(f"建造功能执行出错: {str(e)}")


if __name__ == "__main__":
    # 初始化设备
    auto_setup(__file__)

    click_offline_ad_reward()
    click_work_efficiency_ad()
    click_to_search()
    click_sign_in_reword()
    click_shop()
    click_build()
    log("脚本运行结束")
