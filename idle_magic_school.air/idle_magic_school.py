import sys
import os
# 获取当前脚本的绝对路径并解析符号链接
script_path = os.path.realpath(__file__)
# 获取脚本所在目录
current_dir = os.path.dirname(script_path)
# 获取上级目录作为项目根目录
project_root = os.path.dirname(current_dir)
print(f"项目根目录: {project_root}")
sys.path.append(project_root)


from airtest.core.android.adb import *
from airtest.core.api import *
from my_lib.common import create_button_monitor


def check_app():
    """
    获取当前手机前台运行的应用包名

    功能说明:
    1. 通过ADB获取当前前台运行的完整应用信息
    2. 从完整信息中提取主包名部分
    3. 记录日志并返回结果

    返回值:
        str: 当前前台应用的包名（仅主包名）
        None: 当获取失败时返回

    使用示例:
        current_app = check_app()
        if current_app == "com.tencent.mm":
            print("当前运行微信")

    注意:
        - 依赖ADB连接和device对象
        - 会自动记录调试日志
        - 异常时会返回None并记录错误日志
    """
    try:
        # 获取当前前台应用包名和界面路径
        current_app = device.get_top_activity_name()

        # 提取主包名（分割斜杠前的部分）
        package_name = current_app.split("/")[0]  # 关键修改点
        log(f"当前前台应用包名: {package_name}")
        return package_name
    except Exception as e:
        log(f"获取前台应用失败: {str(e)}")
        return None


def click_popup():
    """
    根据当前APP包名选择对应的弹窗关闭方式

    功能说明:
    1. 根据全局变量PACKAGE_NAME判断当前运行的应用
    2. 调用对应应用的弹窗监控函数
    3. 非支持应用会记录日志并终止脚本

    支持应用:
        - 微信(com.tencent.mm): 调用weixin_popup_monitor()
        - 抖音(com.ss.android.ugc.aweme): 调用douyin_popup_monitor()

    使用示例:
        click_popup()  # 自动根据当前APP选择处理方式

    注意:
        - 依赖全局变量PACKAGE_NAME
        - 需要提前定义各应用的监控函数
        - 非支持应用会终止脚本执行
    """
    if PACKAGE_NAME == "com.tencent.mm":
        weixin_popup_monitor()
    elif PACKAGE_NAME == "com.ss.android.ugc.aweme":
        douyin_popup_monitor()
    else:
        log("当前平台非微信或抖音，脚本终止")
        sys.exit(1)  # 非零退出码表示异常终止


def weixin_popup_monitor(timeout=400):
    """
    持续监控并关闭微信弹窗的守护线程

    功能说明:
    1. 创建后台线程持续监控微信特定弹窗
    2. 检测到弹窗后自动点击关闭按钮
    3. 支持设置超时时间自动终止监控

    参数:
        timeout: int - 监控超时时间(秒)，None表示无限等待

    返回值:
        threading.Event - 线程停止事件对象，可用于外部控制线程终止

    使用示例:
        # 启动监控，最多等待400秒
        stop_event = weixin_popup_monitor(timeout=400)

        # 需要时手动停止监控
        stop_event.set()

    注意:
        - 使用前需确保已正确定义弹窗模板图片路径
        - 点击位置基于1440×3200分辨率设备适配
        - 返回的stop_event可用于外部控制线程终止
        - 线程设置为daemon模式，主线程退出时会自动终止
    """
    print("weixin_popup_monitor")
    stop_event = threading.Event()
    popup = Template(r"pictures/weixin_popup.png", record_pos=(0.002, -0.002), resolution=(1440, 3200))
    popup_confirm = Template(r"pictures/weixin_popup_confirm.png", record_pos=(0.222, 0.463), resolution=(1440, 3200))

    def _monitor():
        start_time = time.time()
        while not stop_event.is_set():
            # 超时检测
            if timeout and (time.time() - start_time > timeout):
                log("弹窗监控已超时")
                stop_event.set()
                break

            if exists(popup):
                touch(popup_confirm)
                stop_event.set()  # 触发停止信号
                break
            else:
                log("检测到弹窗并已关闭")
            sleep(1)

    # 启动守护线程
    monitor_thread = threading.Thread(target=_monitor, daemon=True)
    monitor_thread.start()
    return stop_event


def douyin_popup_monitor():
    """
    (预留)抖音弹窗监控函数

    功能说明:
    待实现的抖音弹窗监控功能

    注意:
        - 当前为占位函数，实际功能待开发
        - 建议参考weixin_popup_monitor实现
    """
    pass


def close_ad():
    """
    根据当前APP包名选择对应的广告关闭方式

    功能说明:
    1. 根据全局变量PACKAGE_NAME判断当前运行的应用
    2. 调用对应应用的广告关闭函数

    支持应用:
        - 微信(com.tencent.mm): 调用close_weixin_ad()
        - 抖音(com.ss.android.ugc.aweme): 调用close_douyin_ad()

    使用示例:
        close_ad()  # 自动根据当前APP选择广告关闭方式

    注意:
        - 依赖全局变量PACKAGE_NAME
        - 需要提前定义各应用的广告关闭函数
        - 不支持的APP会静默跳过
    """
    if PACKAGE_NAME == "com.tencent.mm":
        close_weixin_ad()
    elif PACKAGE_NAME == "com.ss.android.ugc.aweme":
        close_douyin_ad()


def close_douyin_ad():
    """
    抖音广告关闭处理函数

    功能说明:
    1. 定义关闭按钮和返回按钮的模板
    2. 创建按钮监控器并执行
    3. 主关闭按钮点击后终止所有监控
    4. 返回按钮点击后仅终止自己线程

    参数配置:
        - 关闭按钮位置: (0.34, -0.944)
        - 返回按钮位置: (-0.422, -0.921)
        - 分辨率适配: 1264×2780
        - 匹配阈值: 0.85
        - 总超时时间: 60秒
        - 初始等待: 25秒

    使用示例:
        close_douyin_ad()  # 开始监控并关闭抖音广告

    注意:
        - 依赖create_button_monitor函数
        - 需要准备对应的模板图片
        - 按钮位置基于1264×2780分辨率设备
    """
    close_btn = Template(r"pictures/douyin_ad_close.png",
                         record_pos=(0.34, -0.944), resolution=(1264, 2780), threshold=0.825)
    back_btn = Template(r"pictures/douyin_ad_back.png",
                        record_pos=(-0.422, -0.921), resolution=(1264, 2780), threshold=0.85)

    monitor = create_button_monitor(
        main_template=close_btn,
        sub_templates=[back_btn],
        timeout=60,
        initial_wait=25
    )
    monitor()


def close_weixin_ad():
    """
    微信广告关闭处理函数

    功能说明:
    1. 定义关闭按钮模板
    2. 创建按钮监控器并执行
    3. 检测到关闭按钮后点击并终止

    参数配置:
        - 关闭按钮位置: (0.401, -0.957)
        - 分辨率适配: 1440×3200
        - 总超时时间: 60秒
        - 初始等待: 35秒

    使用示例:
        close_weixin_ad()  # 开始监控并关闭微信广告

    注意:
        - 依赖create_button_monitor函数
        - 需要准备对应的模板图片
        - 按钮位置基于1440×3200分辨率设备
    """
    close_btn = Template(r"pictures/weixin_ad_close.png", record_pos=(0.401, -0.957), resolution=(1440, 3200))
    monitor = create_button_monitor(
        main_template=close_btn,
        sub_templates=[],
        timeout=60,
        initial_wait=35
    )
    monitor()


def my_assert(condition: bool, message: str) -> None:
    """
    自定义断言方法，集成Airtest断言功能

    Args:
        condition: 待验证的布尔条件
        message: 断言描述信息（成功/失败时均显示）

    Raises:
        AssertionError: 当条件不满足时抛出
    """
    try:
        if condition:
            # 成功断言：验证两个True相等，展示成功信息
            assert_equal(True, True, msg=message)
        else:
            # 失败断言：强制触发False比较，展示失败信息
            assert_equal(True, False, msg=message)
    except AssertionError as ae:
        # 捕获并处理断言错误（会触发airtest的截图机制）
        log(f"断言失败跟踪: {str(ae)}")


def click_offline_ad_reward():
    offline_reward_interface = Template(r"pictures/offline_reward_interface.png", record_pos=(0.011, -0.001), resolution=(1440, 3200))
    offline_continue_button = Template(r"pictures/offline_continue_button.png", record_pos=(-0.001, 0.776), resolution=(1440, 3200))
    offline_ad_reward_button = Template(r"pictures/offline_ad_reward_button.png", record_pos=(-0.007, -0.15), resolution=(1440, 3200))


    try:
        log("离线奖励:开始")
        if exists(offline_reward_interface):
            offline_ad_reward_button_pos = assert_exists(offline_ad_reward_button)
            touch(offline_ad_reward_button_pos)
            close_ad()
            touch(offline_continue_button)
            log("点击离线奖励领取按钮")
        else:
            log("离线奖励:未开启")
        my_assert(True, "离线奖励:测试通过")
    except Exception as e:
        log(f"离线奖励:执行出错: {str(e)}")
        my_assert(False, "离线奖励:测试失败")
    finally:
        log("离线奖励:结束")

    
        

def check_main_screen():
    shop_task = Template(r"pictures/main_screen.png", record_pos=(-0.403, 0.943), resolution=(1440, 3200))
    close_button = Template(r"pictures/task_close.png", record_pos=(0.381, -0.313), resolution=(1440, 3200))
    if exists(shop_task) and not exists(close_button):
        return True
    else:
        return False


def click_shop():
    shop_interface = Template(r"pictures/shop_interface.png", record_pos=(-0.404, 0.851), resolution=(1440, 3200), threshold=0.80)
    shop_gift_receive = Template(r"pictures/shop_gift_receive.png", record_pos=(0.344, 0.328), resolution=(1440, 3200), threshold=0.85)
    shop_gift_ad = Template(r"pictures/shop_gift_ad.png", record_pos=(-0.001, 0.954), resolution=(1440, 3200), threshold=0.85)
    shop_receive_button = Template(r"pictures/shop_receive_button.png", record_pos=(0.003, 0.381), resolution=(1440, 3200), threshold=0.85)
    
    shop_tab_mysterious_shop = Template(r"pictures/shop_tab_mysterious_shop.png", record_pos=(-0.003, -0.603), resolution=(1440, 3200), threshold=0.85)
    shop_purchase_goods = Template(r"pictures/shop_purchase_goods.png", record_pos=(0.003, 0.749), resolution=(1440, 3200), threshold=0.85)
    pos_list = [(0.12,0.62),(0.4,0.62),(0.6,0.62),(0.9,0.62)]

    shop_tab_gem = Template(r"tpl1747279393604.png", record_pos=(0.102, -0.601), resolution=(1440, 3200))
    shop_gem_5 = Template(r"pictures/shop_gem_5.png", record_pos=(-0.16, -0.315), resolution=(1440, 3200), threshold=0.85)
    shop_gem_5_2 = Template(r"pictures/shop_gem_5_2.png", record_pos=(-0.153, -0.386), resolution=(1440, 3200), threshold=0.85)
    shop_gem_20 = Template(r"pictures/shop_gem_20.png", record_pos=(-0.162, 0.019), resolution=(1440, 3200), threshold=0.85)
    shop_gem_88 = Template(r"pictures/shop_gem_88.png", record_pos=(0.25, 0.015), resolution=(1440, 3200), threshold=0.85)
    shop_close = Template(r"pictures/shop_close.png", record_pos=(-0.436, -0.74), resolution=(1440, 3200), threshold=0.85)
    
    try:
        log("商店:开始")

        if not check_main_screen():
            log("不在主界面")
            return

        shop_interface_pos = exists(shop_interface)
        if shop_interface_pos:
            touch(shop_interface_pos)

            # 礼包界面
            gift_ad_pos = exists(shop_gift_ad)
            if gift_ad_pos:
                touch(gift_ad_pos)
                close_ad()
                get_gift_rewards_pos = exists(shop_gift_receive)
                if get_gift_rewards_pos:
                    touch(get_gift_rewards_pos)

                    touch(shop_receive_button)

                else:
                    log("礼包:不可领取")
            else:
                log("礼包:未开启")
            my_assert(True, "商店-礼包:测试通过")

            # 神秘商店
            tab_mysterious_shop_pos = exists(shop_tab_mysterious_shop)
            if tab_mysterious_shop_pos:
                touch(tab_mysterious_shop_pos)

                for pos in pos_list:
                    touch(pos)

                sleep(5)
                shop_purchase_goods_pos = exists(shop_purchase_goods)
                if shop_purchase_goods_pos:
                    touch(shop_purchase_goods_pos)
                    close_ad()
                else:
                    log("神秘商店:不可进货/cd中")
            else:
                log("神秘商店:未开启")
            my_assert(True, "商店-神秘商店:测试通过")

            # 宝石商店
            tab_gem_pos = exists(shop_tab_gem)
            if tab_gem_pos:
                touch(tab_gem_pos)
                gem_5_2_pos = exists(shop_gem_5_2)
                if gem_5_2_pos:
                    touch(gem_5_2_pos)
                    close_ad()
                    touch(shop_receive_button)
                gem_20_pos = exists(shop_gem_20)
                if gem_20_pos:
                    touch(gem_20_pos)
                    close_ad()
                    touch(shop_receive_button)
                gem_88_pos = exists(shop_gem_88)
                if gem_88_pos:
                    touch(gem_88_pos)
                    close_ad()
                    shop_gem_88_pos = exists(shop_gem_88)
                    if shop_gem_88_pos:
                        touch(shop_gem_88_pos)
            else:
                log("宝石商店:未开启")

            touch(shop_close)
        else:
            log("商店:未开启")
    except Exception as e:
        log(f"商店:执行出错: {str(e)}")
        my_assert(False, "商店:测试失败")
    finally:
        log("商店:结束")


def click_task():
    task_interface = Template(r"tpl1747018098786.png", record_pos=(-0.399, 1.011), resolution=(1440, 3200), threshold=0.85)
    task_receive_button = Template(r"tpl1747018060335.png", record_pos=(-0.005, 0.24), resolution=(1440, 3200), threshold=0.85)
    task_close_button = Template(r"tpl1747018068358.png", record_pos=(0.349, -0.336), resolution=(1440, 3200), threshold=0.85)

    try:
        if check_main_screen():
            task_interface_pos = exists(task_interface)
            if task_interface_pos:
                touch(task_interface_pos)
                task_receive_button_pos = exists(task_receive_button)
                if task_receive_button_pos:
                    touch(task_receive_button_pos)
                    my_assert(True, "任务：领取奖励成功")
                else:
                    log("任务:未完成")
                task_close_button_pos = exists(task_close_button)
                if task_close_button_pos:
                    touch(task_close_button_pos)
            else:
                log("任务:未开启")
                my_assert(True,"任务：未有完成的任务")
        else:
            log("不在主界面")
    except Exception as e:
        log(f"任务:执行出错: {str(e)}")
        my_assert(False, "任务:测试失败")
    finally:
        log("任务:结束")


def click_risk():
    risk_interface = Template(r"tpl1747019728377.png", record_pos=(0.061, 1.011), resolution=(1440, 3200))
    risk_battle = Template(r"tpl1747019750162.png", record_pos=(0.042, 0.153), resolution=(1440, 3200))
    risk_close = Template(r"tpl1747019759508.png", record_pos=(0.406, -0.15), resolution=(1440, 3200))

    risk_go = Template(r"tpl1747019793502.png", record_pos=(0.382, 0.032), resolution=(1440, 3200))
    
    risk_receive = Template(r"tpl1747281281367.png", record_pos=(-0.008, 0.249), resolution=(1440, 3200))
    risk_receive_ad = Template(r"tpl1747281301218.png", record_pos=(0.252, 0.25), resolution=(1440, 3200))
    
    
    try:
        log("冒险:开始")
        if check_main_screen():
            risk_interface_pos = exists(risk_interface)
            if risk_interface_pos:
                touch(risk_interface_pos)
                risk_battle_pos = exists(risk_battle)
                if risk_battle_pos:
                    touch(risk_battle_pos)
                else:
                    log("冒险:进行中")
                    
                risk_receive_pos = exists(risk_receive)
                if risk_receive_pos:
                    touch(risk_receive_pos)
                    
                risk_go_pos = exists(risk_go)
                if risk_go_pos:
                    touch(risk_go_pos)
                    
            else:
                log("冒险:未开启")
        else:
            log("不在主界面")
    except Exception as e:
        log(f"冒险:执行出错: {str(e)}")
        my_assert(False, "冒险:测试失败")
    finally:
        log("冒险:结束")

if __name__ == "__main__":




    # 初始化设备
    auto_setup(__file__)
    connect_device("Android:///")
    device = device()
    PACKAGE_NAME = check_app()

    # click_popup()
    #
    # click_offline_ad_reward()
    # click_shop()
    # click_task()
    
    click_risk()




