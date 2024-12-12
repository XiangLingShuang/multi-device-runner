import json
from airtest.core.android.adb import ADB
from airtest.core.api import *
from pandas.io.formats.printing import pprint_thing
from my_lib.file_process import *


def create_device_log_file(device_id, base_result_path='result'):
    # 读取current_log_folder.txt内容
    folder_name = read_txt_file(os.path.join(base_result_path, 'current_log_folder.txt'))
    if folder_name is None:
        print("无法读取current_log_folder.txt的内容")
        return None
    
    # 创建新的目录路径
    new_dir_path = os.path.join(base_result_path, folder_name, device_id)
    
    # 如果目录不存在，则创建
    os.makedirs(new_dir_path, exist_ok=True)
    
    # 返回设备日志文件路径
    return os.path.join(new_dir_path, f"{device_id}.txt")

# 设备初始化，ADB初始化
auto_setup(__file__)
wake()
device_id = device().uuid
print(device_id)
device_log_file_path = create_device_log_file(device_id)

adb = ADB(device_id)


# 配置信息
# 读取apk_info.json文件
with open('apk_info.json', 'r', encoding="utf-8") as f:
    apk_info = json.load(f)

test_package_name = apk_info.get("test_package_name")
test_info = apk_info.get(test_package_name, {}).get(device_id, [])

for test_dict in test_info:
    is_first_install = True
    is_initialize_success = False
    apk_path = test_dict.get("apk_path")
    package_name = test_dict.get("package_name")

    device_list = device().list_app()

    # 检查并卸载已安装的应用
    if package_name in device_list and is_first_install:
        uninstall(package_name)
        is_first_install = False
        # 安装APK
        install(apk_path)
    elif package_name not in device_list and is_first_install:
        is_first_install = False
        # 安装APK
        install(apk_path)

    for _ in range(5):  # 改为循环5次
        if is_initialize_success:
            break

        start_app(package_name)
        top_activity = adb.get_top_activity()

        if package_name == top_activity[0]:
            pid = top_activity[2]

            log_generator = adb.logcat(extra_args=f"--pid={pid}", read_timeout=10)

            start_time = time.time()  # 记录起始时间
            max_duration = 30  # 设置最大持续时间为30秒

            for line in log_generator:
                # 检查当前时间与起始时间的差
                if time.time() - start_time > max_duration:
                    log("日志获取时间已到，停止日志读取")
                    stop_app(package_name)
                    break

                line_str = line.decode('utf-8').strip()
                # 更新日志文件
                print(line_str)
                if device_log_file_path:
                    with open(device_log_file_path, 'a', encoding='utf-8') as file:  # 指定编码为utf-8
                        file.write(line_str + "\n")
                # 在此处添加日志验证逻辑
                if "[Pub_Gravity] initialize success" in line_str:
                    is_initialize_success = True
                    log("引力引擎启动成功")
                    stop_app(package_name)
                    break

            if not is_initialize_success:
                log("未找到目标日志，引力引擎启动失败")
                stop_app(package_name)
                sleep(5)  # 添加5秒的等待时间


    # 在循环结束后检查是否成功
    if not is_initialize_success:
        log("引力引擎启动失败，运行失败")
        assert_exists(Template(r"non_existent_image.png"), "This element should not exist, causing the test to fail.")