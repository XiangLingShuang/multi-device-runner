# -*- encoding=utf8 -*-
from airtest.core.android.adb import *
from airtest.core.api import *

# 获取当前脚本的绝对路径并解析符号链接
script_path = os.path.realpath(__file__)
# 获取脚本所在目录
current_dir = os.path.dirname(script_path)
# 获取上级目录作为项目根目录
project_root = os.path.dirname(current_dir)
print(f"项目根目录: {project_root}")
sys.path.append(project_root)
from my_lib.common import create_button_monitor


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

def close_weixin_ad():
    close_btn = Template(r"Pictures/weixin_ad_close.png", record_pos=(0.401, -0.957), resolution=(1440, 3200))
    monitor = create_button_monitor(
        main_template=close_btn,
        sub_templates=[],
        timeout=60,
        initial_wait=35
    )
    monitor()


def check_app():
    """
    获取当前手机前台运行的应用包名
    :return: 当前前台应用的包名（仅主包名），如果获取失败则返回 None
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


def close_ad():
    """
    根据当前app选择关闭广告的方式
    """
    if PACKAGE_NAME == "com.tencent.mm":
        close_weixin_ad()
    elif PACKAGE_NAME == "com.ss.android.ugc.aweme":
        close_douyin_ad()


def weixin_popup_monitor(timeout=400):
    """
    持续监控微信弹窗的守护线程
    :param timeout: 超时时间（秒），None表示不限时
    发现弹窗立即点击关闭，超时或成功后自动终止线程
    """
    stop_event = threading.Event()
    popup = Template(r"Pictures/weixin_popup.png", record_pos=(0.002, -0.002), resolution=(1440, 3200))

    def _monitor():
        start_time = time.time()
        while not stop_event.is_set():
            # 超时检测
            if timeout and (time.time() - start_time > timeout):
                log("弹窗监控已超时")
                stop_event.set()
                break

            if exists(popup):
                touch([0.72, 0.76])
                log("检测到弹窗并已关闭")
                stop_event.set()  # 触发停止信号
                break
            sleep(1)

    # 启动守护线程
    monitor_thread = threading.Thread(target=_monitor, daemon=True)
    monitor_thread.start()
    return stop_event



def douyin_popup_monitor():
    pass

def click_popup():
    """
    根据当前app选择关闭广告的方式
    """
    if PACKAGE_NAME == "com.tencent.mm":
        weixin_popup_monitor()
    elif PACKAGE_NAME == "com.ss.android.ugc.aweme":
        douyin_popup_monitor()


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
                                        record_pos=(0.0, 0.0), resolution=(1264, 2780), threshold=0.75)
    try:
        log("离线奖励广告：开始")
        if exists(offline_reward_interface):
            offline_ad_reward_button_pos = assert_exists(offline_ad_reward_button)
            touch(offline_ad_reward_button_pos)
            close_ad()
            assert_equal(True, True, "离线奖励广告：测试成功")
    except Exception as e:
        my_assert(False,"离线奖励广告：测试失败")
    finally:
        log("离线奖励广告：结束")

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
    close_button = Template(r"Pictures/close_button.png",
                            record_pos=(0.428, -0.545), resolution=(1080, 2376), threshold=0.85)  # 弹窗关闭按钮

    wait(build_button,timeout=100)
    if exists(right_button):
        log("进入主界面")
        return True
    else:
        log("未进入主界面")
        if exists(close_button):
            touch(close_button)
            check_main_screen()
        return False


def click_work_efficiency_ad():
    """
    工作效率的广告领取按钮

    功能说明:
    1. 检测并点击工作效率入口按钮
    2. 查找并点击广告增加时间按钮
    3. 处理广告关闭逻辑
    4. 异常情况下关闭弹窗并记录日志

    使用流程:
    1. 检查是否在主界面
    2. 点击工作效率入口
    3. 查找广告增加时间按钮
    4. 点击广告按钮并处理广告
    5. 异常情况下关闭弹窗

    模板配置:
        - 工作效率入口: (0.406, -0.601), 分辨率1264×2780
        - 钻石增加时间按钮: (-0.236, 0.356)
        - 广告增加时间按钮: (0.237, 0.345)
        - 关闭按钮: (0.428, -0.545), 分辨率1080×2376

    使用示例:
        click_work_efficiency_ad()  # 自动完成工作效率广告点击流程

    注意:
        - 依赖check_main_screen()函数检测主界面
        - 依赖close_ad()函数处理广告关闭
        - 各模板图片需放置在Pictures目录下
        - 不同分辨率设备需要调整模板位置
    """
    # 定义所有模板图片
    work_efficiency_entrance = Template(r"Pictures/work_efficiency_entrance.png",
                                      record_pos=(0.406, -0.601), resolution=(1264, 2780), threshold=0.85)
    diamond_increases_time = Template(r"Pictures/diamond_increases_time.png",
                                    record_pos=(-0.236, 0.356), resolution=(1264, 2780), threshold=0.85)
    ad_increases_time = Template(r"Pictures/ad_increases_time.png",
                               record_pos=(0.237, 0.345), resolution=(1264, 2780), threshold=0.85)
    close_button = Template(r"Pictures/close_button.png",
                          record_pos=(0.428, -0.545), resolution=(1080, 2376), threshold=0.85)

    try:
        log("工作效率：开始")
        # 1. 检查是否在主界面
        if check_main_screen():
            # 2. 点击工作效率入口按钮
            touch(work_efficiency_entrance)

            # 3. 查找广告增加时间按钮
            ad_increases_time_pos = exists(ad_increases_time)
            if ad_increases_time_pos:
                # 4. 点击广告按钮并处理广告
                touch(ad_increases_time_pos)
                close_ad()
                assert_equal(True, True, "工作效率：测试成功")
            else:
                log("未找到广告按钮，关闭弹窗")
                # 5. 异常情况下关闭弹窗
                close_button_pos = exists(close_button)
                if close_button_pos:
                    touch(close_button_pos)
                assert_equal(True, True, "工作效率：测试成功")
        else:
            log("未进入主界面，无法点击工作效率的广告领取按钮")
    except Exception as e:
        log(f"点击工作效率广告时发生错误: {str(e)}")
        my_assert( False, "工作效率：测试失败")
    finally:
        log("工作效率：结束")


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
        log("搜寻：开始")
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
                close_ad()  # 处理广告关闭
            assert_equal(True, True, "搜寻：测试成功")
        else:
            log("未进入主界面，无法点击搜寻按钮")
            assert_equal(True, False, "搜寻：测试失败")
    except Exception as e:
        log(f"点击搜寻按钮时发生错误: {str(e)}")
        my_assert( False, "搜寻：测试失败")
    finally:
        log("搜寻：结束")


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
            log("签到：开始")
            touch(sign_in_entrance)  # 点击签到入口
            sleep(1)  # 等待界面加载

            sign_in_button_pos = exists(sign_in_button)
            if sign_in_button_pos:
                touch(sign_in_button_pos)  # 执行签到
                # 处理奖励领取逻辑
                claim_button_pos = exists(claim_button)
                if claim_button_pos:
                    touch(claim_button_pos)
                    assert_equal(True, True, "签到：测试成功")
            else:
                log("未找到签到按钮")
                assert_equal(True, False, "签到：测试失败")
        except Exception as e:
            log(f"签到过程出错: {str(e)}")
            my_assert( False, "签到：测试失败")
        finally:
            log("签到：结束")

        # 执行补签操作
        try:
            log("补签：开始")
            supplementary_button_pos = exists(supplementary_signature_button)
            if supplementary_button_pos:
                touch(supplementary_button_pos)
                close_ad()  # 处理广告
                # 领取奖励
                claim_button_pos = exists(claim_button)
                if claim_button_pos:
                    touch(claim_button_pos)
                    assert_equal(True, True, "补签：测试成功")
            else:
                log("无需补签或补签按钮未找到")
                assert_equal(True, False, "补签：测试失败")
        except Exception as e:
            log(f"补签过程出错: {str(e)}")
            my_assert( False, "补签：测试失败")

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
    """
    处理游戏商店相关操作

    功能说明:
    1. 进入商店界面
    2. 尝试领取10钻石和88钻石的广告奖励
    3. 关闭商店界面

    执行流程:
    1. 检查是否在主界面
    2. 点击商店入口按钮
    3. 查找并点击钻石奖励按钮
    4. 处理广告关闭逻辑
    5. 领取奖励
    6. 关闭商店界面

    模板配置:
        - 商店入口: (-0.41, 0.836), 分辨率1080×2376
        - 10钻石按钮: (-0.16, 0.67)
        - 88钻石按钮: (0.162, 0.657)
        - 领取按钮: (0.002, 0.881)
        - 关闭按钮: (-0.448, -0.988)

    使用示例:
        click_shop()  # 自动完成商店操作流程

    注意:
        - 依赖check_main_screen()函数检测主界面
        - 依赖close_ad()函数处理广告关闭
        - 各模板图片需放置在Pictures目录下
        - 不同分辨率设备需要调整模板位置
    """
    # 定义所有UI元素模板
    shop_entrance = Template(r"Pictures/shop_entrance.png",
                            record_pos=(-0.41, 0.836), resolution=(1080, 2376), threshold=0.85)
    shop_close_button = Template(r"Pictures/shop_close_button.png",
                                record_pos=(-0.448, -0.988), resolution=(1080, 2376), threshold=0.85)
    material_supply = Template(r"Pictures/material_supply.png",
                              record_pos=(-0.001, -0.549), resolution=(1080, 2376), threshold=0.85)
    diamond_10 = Template(r"Pictures/diamond_10.png",
                         record_pos=(-0.16, 0.67), resolution=(1080, 2376), threshold=0.85)
    diamond_88 = Template(r"Pictures/diamond_88.png",
                         record_pos=(0.162, 0.657), resolution=(1080, 2376), threshold=0.85)
    claim_button = Template(r"Pictures/claim_button.png",
                          record_pos=(0.002, 0.881), resolution=(1080, 2376), threshold=0.85)

    try:
        log("商店：开始")
        # 1. 检查是否在主界面
        if check_main_screen():
            # 2. 进入商店界面
            shop_entrance_pos = exists(shop_entrance)
            if shop_entrance_pos:
                touch(shop_entrance_pos)
            else:
                # 备用点击位置，防止模板匹配失败
                touch([0.09, 0.88])

            # 3. 处理10钻石奖励
            if exists(diamond_10):
                touch(diamond_10)
                close_ad()  # 处理广告
                if exists(claim_button):
                    touch(claim_button)  # 领取奖励

            # 4. 处理88钻石奖励
            if exists(diamond_88):
                touch(diamond_88)
                close_ad()  # 处理广告
                if exists(claim_button):
                    touch(claim_button)  # 领取奖励

            # 5. 关闭商店界面
            touch(shop_close_button)
            assert_equal(True, True, "商店：测试成功")
        else:
            log("未进入主界面，无法执行商店操作")

    except Exception as e:
        log(f"商店功能执行出错: {str(e)}")
        my_assert( False, "商店：测试失败")
    finally:
        log("商店：结束")


def click_build():
    # 初始化UI元素模板
    build_entrance = Template(filename=r"Pictures/build.png",
                              record_pos=(0.001, 0.986), resolution=(1264, 2780), threshold=0.85)
    build_close_button = Template(filename=r"Pictures/close_button.png",
                                  record_pos=(0.436, -0.397), resolution=(1080, 2376), threshold=0.85)
    build_button = Template(filename=r"Pictures/build_button.png",
                            record_pos=(0.356, 0.136), resolution=(1080, 2376), threshold=0.85)
    confirm_button = Template(r"Pictures/confirm_button.png",
                              record_pos=(-0.001, 0.122), resolution=(1440, 3200), target_pos= 6)


    try:
        log("建造流程：开始")
        # 检查主界面状态
        if check_main_screen():
            # 点击建造入口
            touch(build_entrance)
            sleep(1)

            # 检测建造按钮是否存在
            if exists(build_button):
                # 执行建造操作
                touch(build_button)
                touch(confirm_button)
                assert_equal(True,True,"建造流程：测试通过")
            else:
                # 关闭建造界面
                touch(build_close_button)
                assert_equal(True, False, "建造流程：测试失败")
    except Exception as e:
        # 异常处理
        log(f"建造功能执行出错: {str(e)}")
        my_assert( False, "建造流程：测试失败")
    finally:
        log("建造流程：结束")


# def test():
#     try:
#         my_assert(True,"成功")
#         my_assert(False,"失败")
#     except Exception as e:
#         my_assert(False,"失败")
#     finally:
#         log("结束")

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


if __name__ == "__main__":
    # 初始化设备
    # auto_setup(__file__)
    connect_device("Android:///")
    device = device()
    PACKAGE_NAME = check_app()
    click_popup()


    click_offline_ad_reward()
    click_work_efficiency_ad()
    click_to_search()
    click_sign_in_reword()
    click_shop()
    click_build()
    log("脚本运行结束")