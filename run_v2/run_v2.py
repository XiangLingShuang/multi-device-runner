# -*- encoding=utf-8 -*-
# Run Airtest in parallel on multi-device
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

import traceback
import subprocess
import webbrowser
import time
import json


import pandas as pd
from airtest.core.android import Android
from airtest.core.android.adb import ADB
from airtest.core.api import device, connect_device
from jinja2 import Environment, FileSystemLoader
from my_lib.file_process import *


def run(device, air_scripts, script_project_name, run_all=False):
    """
    在单个设备上依次运行多个测试脚本的主函数。

    :param device: 要进行测试的设备序列号。
    :param air_scripts: 测试脚本路径列表。
    :param script_project_name: 脚本项目名称。
    :param run_all: 是否重新开始测试。True 表示从头开始测试,False 表示从data.json保存的进度继续测试。 
    """
    try:
        # 加载测试进度数据
        results = load_json_data(air_scripts[0], run_all)  # 使用第一个脚本初始化
        # 只保存脚本文件名
        results['scripts'] = [os.path.basename(x) for x in air_scripts]  # 保存所有脚本文件名
        results['script_project_name'] = script_project_name  # 保存脚本项目名称

        for air in air_scripts:
            print(f"\n开始执行脚本: {air}")
            # 在设备上启动测试任务
            task = run_on_single_device(device, air, results, run_all)
            
            if task:
                # 等待测试任务完成
                status = task['process'].wait()

                # 生成设备的测试报告，并更新测试状态
                if device not in results['tests']:
                    results['tests'][device] = {}
                # 只用文件名作为key
                air_file = os.path.basename(air)
                results['tests'][device][air_file] = run_one_report(task['air'], task)
                results['tests'][device][air_file]['status'] = status

                # 将当前的测试结果保存到data.json文件
                json.dump(results, open('run_v2/data_v2.json', "w"), indent=4)

        # 生成所有测试的汇总报告
        run_summary(results)

    except Exception as e:
        # 如果出现异常，打印堆栈跟踪信息
        traceback.print_exc()


def load_json_data(air, run_all):
    """
    加载测试进度数据。

    :param air: 测试脚本的路径。
    :param run_all: 是否重新开始测试。True 表示从头开始测试，False 表示从data.json保存的进度继续测试。
    :return: 返回包含测试进度的字典。
    """    # 拼接当前工作目录和data.json文件的完整路径
    json_file = os.path.join(os.getcwd(), 'run_v2', 'data_v2.json')

    # 检查是否需要继续上一次的进度
    if (not run_all) and os.path.isfile(json_file):
        # 使用with语句打开文件，确保文件正确关闭
        with open(json_file, 'r') as file:
            data = json.load(file)

        # 更新开始时间
        data['start'] = time.time()
        return data
    else:
        # 否则，创建一个新的测试进度数据
        data = {
            'start': time.time(),
            'script': air,
            'log_dir_path': '',
            'tests': {},
        }
        # 创建一个时间戳文件夹，用于存放日志
        data['log_dir_path'] = create_time_folder(data['start'])
        return data


def run_on_multi_device(devices, air, results, run_all):
    """
    在多台设备上运行Airtest脚本。

    :param devices: 设备列表。
    :param air: Airtest脚本的路径。
    :param results: 包含之前测试结果的字典。
    :param run_all: 是否重新开始测试。True 表示重新开始，False 表示继续之前的测试。
    :return: 返回一个包含测试任务的列表。
    """
    tasks = []
    for dev in devices:
        # 检查是否需要跳过当前设备的测试
        if not run_all and results['tests'].get(dev) and results['tests'][dev].get('status') == 0:
            print(f"Skip device {dev}")
            continue        # 为每个设备创建一个日志目录
        log_dir = create_device_folder(dev, results['log_dir_path'])

        # 构造Airtest运行命令
        cmd = [
            "airtest",
            "run",
            air,
            "--device",
            f"Android:///{dev}",
            "--log",
            log_dir
        ]
        
        # 获取Android版本号，决定是否添加录制选项
        adb = ADB(serialno=dev)
        android_version = int(adb.cmd(f"-s {dev} shell getprop ro.build.version.release"))
        print(f"设备 {dev} Android版本: {android_version}")
        
        # 如果Android版本小于15，添加录制参数
        if android_version < 15:
            cmd.append('--recording')

        try:
            # 使用subprocess启动测试，并将任务添加到任务列表
            tasks.append({
                'process': subprocess.Popen(cmd, cwd=os.getcwd()),
                'dev': dev,
                'air': air,
                'path': log_dir,
            })
        except Exception as e:
            print(f"Error running on device {dev}: {e}")
            traceback.print_exc()
    return tasks


def run_on_single_device(device, air, results, run_all):
    """
    在单个设备上运行Airtest脚本。

    :param device: 设备序列号。
    :param air: Airtest脚本的路径。
    :param results: 包含之前测试结果的字典。
    :param run_all: 是否重新开始测试。
    :return: 返回测试任务信息。
    """
    # 检查是否需要跳过当前脚本的测试
    air_file = os.path.basename(air)
    if not run_all and device in results['tests'] and air_file in results['tests'][device] and results['tests'][device][air_file].get('status') == 0:
        print(f"跳过设备 {device} 的脚本 {air}")
        return None

    # 为设备和脚本创建日志目录
    log_dir = create_device_folder(device, results['log_dir_path'], air)
      # 构造Airtest运行命令
    cmd = [
        "airtest",
        "run",
        air,
        "--device",
        f"Android:///{device}",
        "--log",
        log_dir
    ]

    # 获取Android版本号，决定是否添加录制选项
    adb = ADB(serialno=device)
    android_version = int(adb.cmd(f"-s {device} shell getprop ro.build.version.release"))
    print(f"设备 {device} Android版本: {android_version}")
    
    # 如果Android版本小于15，添加录制参数
    if android_version < 15:
        cmd.append('--recording')

    try:
        # 使用subprocess启动测试
        return {
            'process': subprocess.Popen(cmd, cwd=os.getcwd()),
            'dev': device,
            'air': air,
            'path': log_dir,
        }
    except Exception as e:
        print(f"在设备 {device} 上运行脚本 {air} 时出错: {e}")
        traceback.print_exc()
        return None


def create_time_folder(timestamp):
    """
    根据给定的时间戳创建一个以时间格式命名的文件夹。

    :param timestamp: 用于生成文件夹名称的时间戳。
    :return: 创建的文件夹的路径。    """
    # 基础目录
    base_dir = os.path.join('.', 'result')

    # 将时间戳转换为时间元组
    time_tuple = time.localtime(timestamp)

    # 根据时间元组生成文件夹名称
    folder_name = time.strftime("%Y_%m_%d_%H_%M_%S", time_tuple)

    # 构造目标文件夹的完整路径
    folder_path = os.path.join(base_dir, folder_name)    # 如果文件夹不存在，则创建它
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        # 将文件夹名保存在 current_log_folder.txt 中
        save_txt_data(folder_name, os.path.join(base_dir, 'current_log_folder.txt'))

    # 返回创建的文件夹路径
    return folder_path


def create_device_folder(device, time_folder_dir, air_path):
    """
    在指定的时间文件夹内为特定设备和脚本创建子文件夹。

    :param device: 设备标识符，用于命名子文件夹。
    :param time_folder_dir: 时间文件夹的路径，用作父目录。
    :param air_path: 脚本路径，用于创建脚本目录。
    :return: 创建的设备文件夹的路径。
    """
    # 使用设备标识符创建文件夹名称，替换掉文件名中不允许的字符
    device_folder_name = device.replace(".", "_").replace(':', '_')

    # 获取脚本名称（去除.air后缀）
    script_name = os.path.splitext(os.path.basename(air_path))[0]

    # 构造完整的路径：时间/序列号/脚本名
    device_folder_dir = os.path.join(time_folder_dir, device_folder_name, script_name)

    # 如果文件夹不存在，则创建它
    if not os.path.exists(device_folder_dir):
        os.makedirs(device_folder_dir, exist_ok=True)

    # 返回创建的设备文件夹路径
    return device_folder_dir


def run_one_report(air, task_temp):
    """
    为单个脚本生成测试报告。

    :param task_temp:
    :param air: Airtest脚本的路径。
    :return: 包含测试报告信息的字典。
    """
    # 获取日志目录
    log_dir = task_temp['path']
    dev = task_temp['dev']
    log_txt = os.path.join(log_dir, 'log.txt')
    log_html = os.path.join(log_dir, 'log.html')
    
    try:
        # 如果日志文件存在，生成测试报告
        if os.path.isfile(log_txt):
            cmd = [
                "airtest",
                "report",
                air,
                "--log_root",
                log_dir,
                "--outfile",
                log_html,
                "--lang",
                "zh"
            ]
            ret = subprocess.call(cmd, shell=True, cwd=os.getcwd())
            device_name = get_devices(dev)
            
            # 计算相对路径：序列号/脚本名/log.html
            script_name = os.path.splitext(os.path.basename(air))[0]
            relative_path = os.path.join(dev.replace(".", "_").replace(':', '_'), script_name)
            
            return {
                'status': ret,
                'device_name': device_name,
                'path': os.path.join(relative_path, 'log.html'),
                'log_path': os.path.join(relative_path, 'log.txt')
            }
        else:
            print(f"Report build Failed. File not found in dir {log_txt}")
    except Exception as e:
        traceback.print_exc()

    return {'status': -1, 'device': dev, 'path': ''}


def run_summary(data):
    """
    生成测试的汇总报告。

    :param data: 包含所有测试数据的字典。
    """
    try:
        total_success = 0
        total_count = 0
        
        # 计算所有脚本的成功和总数
        for device_results in data['tests'].values():
            for script_result in device_results.values():
                if script_result.get('status') == 0:
                    total_success += 1
                total_count += 1

        summary = {
            'time': "%.3f" % (time.time() - data['start']),
            'success': total_success,
            'count': total_count,
            'scripts': data.get('scripts', [])  # 添加脚本列表到汇总信息
        }
        summary.update(data)
        summary['start'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['start']))
        
        env = Environment(loader=FileSystemLoader(os.getcwd()), trim_blocks=True)
        html = env.get_template('run_v2/report_tpl_v2.html').render(data=summary)
        report_path = os.path.join(data['log_dir_path'], 'report.html')
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)
        webbrowser.open(report_path)
    except Exception as e:
        traceback.print_exc()


def get_devices(dev):
    """
    根据设备序列号查询设备型号。

    :param dev: 设备序列号。
    :return: 设备型号名称，如果找不到则返回'NULL'。
    """
    print(f"开始查询{dev}")

    try:
        # 使用pandas读取指定工作表的Excel文件
        df = pd.read_excel(device_info_path)

        # 查找匹配的行
        matched_row = df[df.iloc[:, 1] == dev]

        # 如果找到匹配的行，返回设备型号
        if not matched_row.empty:
            return matched_row.iloc[0, 3]  # 假设设备型号在第4列
        else:
            return 'NULL'
    except FileNotFoundError:
        print("未找到设备信息文件")
        return 'NULL'
    except Exception as e:
        print(f"打开设备信息文件失败：{e}")
        return 'NULL'


def update_device_run_count(results_tests):
    """
    更新或添加设备运行脚本的次数。

    :param results_tests: 包含测试结果的字典，其中key是设备序列号。
    """
    try:        # 读取Excel文件
        file_path = os.path.join('.', 'devices', 'device_count.xlsx')
        df = pd.read_excel(file_path)

        # 遍历results_tests中的每个设备序列号
        for dev_serial, data in results_tests.items():
            if data['status'] == 0:
                # 检查序列号是否在DataFrame中
                if dev_serial in df['序列号'].values:
                    # 如果在，则增加运行次数
                    df.loc[df['序列号'] == dev_serial, '运行次数'] += 1
                else:
                    # 如果不在，则添加新行
                    new_row = {
                        '序列号': dev_serial,
                        '名称': data['device_name'],
                        '运行次数': 1
                    }
                    df = df.append(new_row, ignore_index=True)

        # 将更新后的DataFrame写回Excel文件
        df.to_excel(file_path, index=False)
    except FileNotFoundError:
        print("未找到设备计数文件")
    except Exception as e:
        print(f"处理设备计数文件时出错：{e}")


def save_open_app_time(results, path):
    """
    更新或添加设备运行脚本的次数
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(path)
        base_path = results['log_dir_path']
        # 遍历results_tests中的每个设备序列号
        for dev_serial, scripts_data in results['tests'].items():
            for script_name, script_data in scripts_data.items():
                if script_data.get('status') == 0:
                    # 检查序列号是否在DataFrame中
                    log_path = os.path.join(base_path, dev_serial.replace(".", "_").replace(':', '_'), 
                                          os.path.splitext(os.path.basename(script_name))[0], 'log.txt')
                    print(log_path)
                    lost_time = read_txt(log_path)

                    if dev_serial in df['序列号'].values:
                        # 如果在，则增加运行次数
                        df.loc[df['序列号'] == dev_serial, '对比时间'] = lost_time
                        df.loc[df['序列号'] == dev_serial, '实际时间'] = df.loc[df['序列号'] == dev_serial, '运行时间'] - df.loc[df['序列号'] == dev_serial, '对比时间']
                    else:
                        # 如果不在，则添加新行
                        new_row = {
                            '序列号': dev_serial,
                            '名称': script_data['device_name'],
                            '运行时间': None,
                            '对比时间': lost_time,
                            '实际时间': None
                        }
                        df = df.append(new_row, ignore_index=True)

        # 将更新后的DataFrame写回Excel文件
        df.to_excel(path, index=False)
    except FileNotFoundError:
        print("未找到设备计数文件")
    except Exception as e:
        print(f"处理设备计数文件时出错：{e}")


def read_txt(path):
    with open(path, 'r') as file:
        for line in file:
            try:
                # 尝试将行内容转换为JSON
                json_data = json.loads(line)
                # 检查是否存在"data-ret-time"键
                if "time" in json_data['data']['ret']:
                    return json_data['data']['ret']['time']
            except:
                # 如果行不是有效的JSON，忽略错误并继续
                continue
    return None  # 如果没有找到"data-ret-time"，返回None


device_info_path = os.path.join('.', 'devices', 'device_info.xlsx')

if __name__ == '__main__':
    # 获取已连接的设备列表
    devices_id_list = [tmp[0] for tmp in ADB().devices()]
    print(f"发现设备: {devices_id_list}")
    
    if len(devices_id_list) == 0:
        print("未找到设备")
        exit(0)
          # 要执行的脚本列表
    script_project_name = "test"
    air_scripts = [
        os.path.join(script_project_name, "test.air"),
        os.path.join(script_project_name, "test2.air"),
    ]

      # 使用第一个设备执行所有脚本
    device = devices_id_list[0]
    print(f"使用设备 {device} 执行脚本")
    run(device, air_scripts, script_project_name, run_all=True)
