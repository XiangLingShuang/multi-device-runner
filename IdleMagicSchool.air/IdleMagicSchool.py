from airtest.core.android.adb import *
from airtest.core.api import *
from my_lib.common import create_button_monitor, set_project_root


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
    popup = Template(r"Pictures/weixin_popup.png", record_pos=(0.002, -0.002), resolution=(1440, 3200))
    popup_confirm = Template(r"tpl1746512224460.png", record_pos=(0.222, 0.463), resolution=(1440, 3200))

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
    close_btn = Template(r"Pictures/douyin_ad_close.png",
                         record_pos=(0.34, -0.944), resolution=(1264, 2780), threshold=0.85)
    back_btn = Template(r"Pictures/douyin_ad_back.png",
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
    close_btn = Template(r"Pictures/weixin_ad_close.png", record_pos=(0.401, -0.957), resolution=(1440, 3200))
    monitor = create_button_monitor(
        main_template=close_btn,
        sub_templates=[],
        timeout=60,
        initial_wait=35
    )
    monitor()



def click_offline_ad_reward():
    offline_reward_interface = Template(r"Pictures/offline_reward_interface.png", record_pos=(0.011, -0.001), resolution=(1440, 3200))
    offline_continue_button = Template(r"Pictures/offline_continue_button.png", record_pos=(-0.001, 0.776), resolution=(1440, 3200))
    offline_ad_reward_button = Template(r"Pictures/offline_ad_reward_button.png", record_pos=(-0.007, -0.15), resolution=(1440, 3200))

    if exists(offline_reward_interface):
        offline_ad_reward_button_pos = assert_exists(offline_ad_reward_button)
        touch(offline_ad_reward_button_pos)
        close_ad()
        touch(offline_continue_button)
        log("点击离线奖励领取按钮")


    
        

def check_main_screen():
    shop_task = Template(r"tpl1746513643908.png", record_pos=(-0.403, 0.943), resolution=(1440, 3200))
    close_button = Template(r"tpl1746513656988.png", record_pos=(0.381, -0.313), resolution=(1440, 3200))
    if exists(shop_task) and not exists(close_button):
        return True
    else:
        return False





if __name__ == "__main__":
    set_project_root()


    # 初始化设备
    auto_setup(__file__)
    connect_device("Android:///")
    device = device()
    PACKAGE_NAME = check_app()

    click_popup()

    click_offline_ad_reward()

    print(check_main_screen())

 



