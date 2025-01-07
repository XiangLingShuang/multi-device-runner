import json
import threading
from airtest.core.android.adb import ADB
from airtest.core.api import *
from my_lib.file_process import *


def create_device_log_file(device_id, base_result_path='result'):
    folder_name = read_txt_file(os.path.join(base_result_path, 'current_log_folder.txt'))
    if folder_name is None:
        print("无法读取current_log_folder.txt的内容")
        return None

    new_dir_path = os.path.join(base_result_path, folder_name, device_id)
    os.makedirs(new_dir_path, exist_ok=True)

    return os.path.join(new_dir_path, f"{device_id}.txt")


# def touch_template():
#     agree_button = Template(r"agree_button.png", record_pos=(0.256, 0.684), resolution=(1264, 2780))
#     while not stop_thread.is_set():
#         if wait(agree_button,timeout=30, interval=2):
#             touch(agree_button)
#             break

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


# 初始化设备和ADB
auto_setup(__file__)
wake()
device_id = device().uuid
print(device_id)
device_log_file_path = create_device_log_file(device_id)
adb = ADB(device_id)

# 读取apk_info.json文件
with open('apk_info.json', 'r', encoding="utf-8") as f:
    apk_info = json.load(f).get("data")

test_package_name = apk_info.get("test_package_name")
test_info = apk_info.get(test_package_name, {}).get(device_id, [])

for test_dict in test_info:
    is_first_install = True
    is_initialize_success = False
    apk_path = test_dict.get("apk_path")
    package_name = test_dict.get("package_name")

    device_list = device().list_app()

    if package_name in device_list and is_first_install:
        uninstall(package_name)
        is_first_install = False

        xiaomi_install_agree_button = Template(r"tpl1735889056299.png", record_pos=(-0.21, 0.885), resolution=(1080, 2340))
        xiaomi_install_agree_button_stop_thread = threading.Event()
        xiaomi_install_agree_button_thread = threading.Thread(target=touch_template,
                                               args=(xiaomi_install_agree_button, 30, 2, xiaomi_install_agree_button_stop_thread))
        xiaomi_install_agree_button_thread.start()
        install(apk_path)

        xiaomi_install_agree_button_stop_thread.set()
        xiaomi_install_agree_button_thread.join()


    elif package_name not in device_list and is_first_install:
        is_first_install = False
        install(apk_path)

    for _ in range(1):
        if is_initialize_success:
            break

        start_app(package_name)
        top_activity = adb.get_top_activity()

        if package_name == top_activity[0]:

            agree_button = Template(r"agree_button.png", record_pos=(0.256, 0.684), resolution=(1264, 2780))
            agree_button_stop_thread = threading.Event()
            agree_button_thread = threading.Thread(target=touch_template, args=(agree_button, 30, 2, agree_button_stop_thread))
            agree_button_thread.start()


            pid = top_activity[2]
            log_generator = adb.logcat(extra_args=f"--pid={pid}", read_timeout=10)

            start_time = time.time()
            max_duration = 45



            for line in log_generator:
                if time.time() - start_time > max_duration:
                    log("日志获取时间已到，停止日志读取")
                    stop_app(package_name)
                    agree_button_stop_thread.set()
                    agree_button_thread.join()
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
                    agree_button_stop_thread.set()
                    agree_button_thread.join()
                    break

            if not is_initialize_success:
                log("未找到目标日志，引力引擎启动失败")
                stop_app(package_name)
                agree_button_stop_thread.set()
                agree_button_thread.join()
                sleep(5)

    if not is_initialize_success:
        log("引力引擎启动失败，运行失败")
        assert_exists(Template(r"non_existent_image.png"), "This element should not exist, causing the test to fail.")


