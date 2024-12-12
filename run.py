# -*- encoding=utf-8 -*-
# Run Airtest in parallel on multi-device
import os
import traceback
import subprocess
import webbrowser
import time
import json

import pandas as pd
from airtest.core.android.adb import ADB
from jinja2 import Environment, FileSystemLoader
from my_lib.file_process import *


def run(devices, air, run_all=False):
    """
    运行测试脚本的主函数。

    :param devices: 要进行测试的设备列表。
    :param air: 测试脚本的路径。
    :param run_all: 是否重新开始测试。True 表示从头开始测试,False 表示从data.json保存的进度继续测试。 
    """
    try:
        # 加载测试进度数据
        results = load_json_data(air, run_all)

        # 在多个设备上启动测试任务
        tasks = run_on_multi_device(devices, air, results, run_all)

        for task in tasks:
            # 等待每个测试任务完成
            status = task['process'].wait()

            # 生成单个设备的测试报告，并更新测试状态
            results['tests'][task['dev']] = run_one_report(task['air'], task)
            results['tests'][task['dev']]['status'] = status

            # 将当前的测试结果保存到data.json文件
            json.dump(results, open('data.json', "w"), indent=4)

        # 生成所有测试的汇总报告
        run_summary(results)
        # update_device_run_count(results['tests'])


    except Exception as e:
        # 如果出现异常，打印堆栈跟踪信息
        traceback.print_exc()


def load_json_data(air, run_all):
    """
    加载测试进度数据。

    :param air: 测试脚本的路径。
    :param run_all: 是否重新开始测试。True 表示从头开始测试，False 表示从data.json保存的进度继续测试。
    :return: 返回包含测试进度的字典。
    """
    # 拼接当前工作目录和data.json文件的完整路径
    json_file = os.path.join(os.getcwd(), 'data.json')

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
            continue

        # 为每个设备创建一个日志目录
        log_dir = create_device_folder(dev, results['log_dir_path'])

        # 构造Airtest运行命令
        cmd = [
            "airtest",
            "run",
            air,
            "--device",
            f"Android:///{dev}",
            "--log",
            log_dir,
            "--recording"
        ]

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


def create_time_folder(timestamp):
    """
    根据给定的时间戳创建一个以时间格式命名的文件夹。

    :param timestamp: 用于生成文件夹名称的时间戳。
    :return: 创建的文件夹的路径。
    """
    # 基础目录
    base_dir = '.\\result'

    # 将时间戳转换为时间元组
    time_tuple = time.localtime(timestamp)

    # 根据时间元组生成文件夹名称
    folder_name = time.strftime("%Y_%m_%d_%H_%M_%S", time_tuple)

    # 构造目标文件夹的完整路径
    folder_path = os.path.join(base_dir, folder_name)

    # 如果文件夹不存在，则创建它
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
            # 将文件夹名保存在 current_log_folder.txt 中
        save_txt_data(folder_name,os.path.join(base_dir, 'current_log_folder.txt'))

    # 返回创建的文件夹路径
    return folder_path


def create_device_folder(device, time_folder_dir):
    """
    在指定的时间文件夹内为特定设备创建一个子文件夹。

    :param device: 设备标识符，用于命名子文件夹。
    :param time_folder_dir: 时间文件夹的路径，用作父目录。
    :return: 创建的设备文件夹的路径。
    """
    # 使用设备标识符创建文件夹名称，替换掉文件名中不允许的字符
    device_folder_name = device.replace(".", "_").replace(':', '_')

    # 构造设备文件夹的完整路径
    device_folder_dir = os.path.join(time_folder_dir, device_folder_name)

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
    # 为设备创建日志目录
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
            path = f".\\{dev}"
            return {
                'status': ret,
                'device_name': device_name,
                'path': os.path.join(path, 'log.html'),
                'log_path': os.path.join(path, 'log.txt')
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
        summary = {
            'time': "%.3f" % (time.time() - data['start']),
            'success': [item['status'] for item in data['tests'].values()].count(0),
            'count': len(data['tests'])
        }
        summary.update(data)
        summary['start'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['start']))
        env = Environment(loader=FileSystemLoader(os.getcwd()), trim_blocks=True)
        html = env.get_template('report_tpl.html').render(data=summary)
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
    try:
        # 读取Excel文件
        file_path = './devices/device_count.xlsx'
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
        for dev_serial, data in results['tests'].items():
            if data['status'] == 0:
                # 检查序列号是否在DataFrame中
                log_path = f"{base_path}\\{dev_serial}\\log.txt"
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
                        '名称': data['device_name'],
                        '运行时间': None,
                        '对比时间': None,
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


device_info_path = r'.\devices\device_info.xlsx'

if __name__ == '__main__':
    devices_id_list = [tmp[0] for tmp in ADB().devices()]
    # air_folder = "tutorial.air"
    # run(devices_id_list, air_folder, run_all=True)
    air_folder = "test.air"
    run(devices_id_list, air_folder, run_all=True)
