import json
import threading
import os
import time
from airtest.core.android.adb import ADB
from airtest.core.api import *
from my_lib.file_process import *


def read_apk_info(file_path='apk_info.json'):
    """
    读取apk_info.json文件
    """
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            return json.load(f).get("data", {})
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到")
        return {}
    except json.JSONDecodeError:
        print(f"文件 {file_path} 格式错误")
        return {}


def create_device_log_file(device_id, base_result_path='result'):
    """
    创建设备日志文件路径
    """
    try:
        folder_name = read_txt_file(os.path.join(base_result_path, 'current_log_folder.txt'))
        if folder_name is None:
            print("无法读取current_log_folder.txt的内容")
            return None

        new_dir_path = os.path.join(base_result_path, folder_name, device_id)
        os.makedirs(new_dir_path, exist_ok=True)

        return os.path.join(new_dir_path, f"{device_id}.txt")
    except Exception as e:
        print(f"创建日志文件时发生错误: {e}")
        return None


def install_app(adb, package_name, apk_path, is_first_install):
    """
    安装或卸载并重新安装应用
    """
    try:
        device_list = device().list_app()

        if package_name in device_list and is_first_install:
            uninstall(package_name)
            log(f"卸载已安装的应用: {package_name}")
            is_first_install = False
            install(apk_path)
            log(f"重新安装应用: {apk_path}")
        elif package_name not in device_list and is_first_install:
            is_first_install = False
            install(apk_path)
            log(f"安装应用: {apk_path}")
    except Exception as e:
        log(f"安装应用时发生错误: {e}")


def start_and_monitor_app(adb, package_name, device_log_file_path, max_duration=45):
    """
    启动应用并监控日志，检查初始化是否成功
    """
    try:
        start_app(package_name)
        top_activity = adb.get_top_activity()

        if package_name == top_activity[0]:
            pid = top_activity[2]
            log_generator = adb.logcat(extra_args=f"--pid={pid}", read_timeout=10)

            # 启动独立线程监听模板点击
            stop_thread = threading.Event()
            thread = threading.Thread(target=touch_template, args=(stop_thread,))
            thread.start()

            start_time = time.time()
            is_initialize_success = False

            for line in log_generator:
                if time.time() - start_time > max_duration:
                    log("日志获取时间已到，停止日志读取")
                    stop_app(package_name)
                    stop_thread.set()
                    thread.join()
                    break

                line_str = line.decode('utf-8').strip()
                print(line_str)
                if device_log_file_path:
                    with open(device_log_file_path, 'a', encoding='utf-8') as file:
                        file.write(line_str + "\n")

                if "[Pub_Gravity] initialize success" in line_str:
                    is_initialize_success = True
                    log("引力引擎启动成功")
                    stop_app(package_name)
                    stop_thread.set()
                    thread.join()
                    return True

            if not is_initialize_success:
                log("未找到目标日志，引力引擎启动失败")
                stop_app(package_name)
                stop_thread.set()
                thread.join()
                sleep(5)

        return False
    except Exception as e:
        log(f"启动和监控应用时发生错误: {e}")
        return False


def touch_template(stop_thread):
    """
    独立线程中触发模板点击
    """
    try:
        agree_button = Template(r"tpl1735011586368.png", record_pos=(0.256, 0.684), resolution=(1264, 2780))
        while not stop_thread.is_set():
            if wait(agree_button, timeout=30, interval=2):
                touch(agree_button)
                break
    except Exception as e:
        log(f"模板点击线程中发生错误: {e}")


def process_test_case(test_info, adb, device_id, device_log_file_path):
    """
    处理单个测试用例
    """
    for test_dict in test_info:
        is_first_install = True
        is_initialize_success = False
        apk_path = test_dict.get("apk_path")
        package_name = test_dict.get("package_name")

        # 安装应用
        install_app(adb, package_name, apk_path, is_first_install)

        # 启动和监控应用
        for _ in range(1):  # 重试次数
            if is_initialize_success:
                break

            is_initialize_success = start_and_monitor_app(adb, package_name, device_log_file_path)

        if not is_initialize_success:
            log("引力引擎启动失败，运行失败")
            assert_exists(Template(r"non_existent_image.png"), "This element should not exist, causing the test to fail.")


def main():
    """
    主函数，初始化设备并执行测试用例
    """
    try:
        # 初始化设备和ADB
        auto_setup(__file__)
        wake()
        device_id = device().uuid
        print(f"设备ID: {device_id}")

        # 创建日志文件
        device_log_file_path = create_device_log_file(device_id)
        adb = ADB(device_id)

        # 读取apk_info.json文件
        apk_info = read_apk_info()
        test_package_name = apk_info.get("test_package_name")
        test_info = apk_info.get(test_package_name, {}).get(device_id, [])

        # 处理测试用例
        process_test_case(test_info, adb, device_id, device_log_file_path)
    except Exception as e:
        log(f"主函数执行时发生错误: {e}")


if __name__ == "__main__":
    main()
