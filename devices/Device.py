import math
import subprocess
import time

import pandas as pd


class Device:
    device_info_path = './devices/device_info.xlsx'

    def __init__(self,  adb_path=r'adb'):
        self.device_serial_number = None
        self.device_order = None
        self.device_brand = None
        self.device_name = None
        self.device_model = None
        self.device_android_version = None
        self.device_soc = None
        self.device_ram = None
        self.adb_path = adb_path

        # 在实例初始化时自动更新信息
        self.update_info_from_excel()

    def update_info_from_excel(self):

        df = pd.read_excel(Device.device_info_path)
        device_info = df[df.iloc[:, 1] == self.device_serial_number]  # 假设第二列包含序列号

        if not device_info.empty:
            row = device_info.iloc[0]  # 获取匹配的第一行数据
            self.device_order = row[0]
            self.device_brand = row[2]
            self.device_name = row[3]
            self.device_model = row[4]
            self.device_android_version = row[5]
            self.device_soc = row[6]
            self.device_ram = row[7]
        else:
            print(f"*****{self.device_serial_number}是新设备*****")
            print(f"*****获取设备{self.device_serial_number}信息*****")
            self.get_device_info()
            print(f"*****{self.device_serial_number}信息保存中*****")
            self.save_to_excel()

    def __str__(self):
        print(
            f"Device(serial_number={self.device_serial_number}, order={self.device_order}, brand={self.device_brand}, name={self.device_name}, model={self.device_model}, android_version={self.device_android_version}, soc={self.device_soc}, ram={self.device_ram})")

    def adb_command(self, command):
        """执行ADB命令并返回输出"""
        try:
            completed_process = subprocess.run(f'{self.adb_path} -s {self.device_serial_number} {command}', shell=True, capture_output=True, text=True)
            return completed_process.stdout.strip()
        except Exception as e:
            print(f"Error executing ADB command: {e}")
            return None

    def get_device_info(self):
        """获取设备信息"""
        self.device_brand = self.adb_command('shell getprop ro.product.brand')
        self.device_android_version = self.adb_command('shell getprop ro.build.version.release')
        self.device_soc = self.adb_command('shell cat /proc/cpuinfo').splitlines()[-1].split(":")[-1]
        self.device_ram = self.get_total_memory()
        self.device_name, self.device_model = self.get_device_name_and_model()

    def get_total_memory(self):
        """获取手机RAM大小"""
        meminfo = self.adb_command('shell cat /proc/meminfo').splitlines()
        for line in meminfo:
            if "MemTotal" in line:
                mem_total_kb = int(line.split(':')[1].strip().split(' ')[0])
                return math.ceil(mem_total_kb / (1024 * 1024))
        return 0

    def get_device_name_and_model(self):
        """根据品牌获取设备名称和型号"""
        brand = self.device_brand.lower()
        if brand in ["redmi", "xiaomi"]:
            name = self.adb_command("shell getprop ro.product.model")
            model = self.adb_command('shell getprop ro.product.cert')
        elif brand == "poco":
            name = self.adb_command("shell getprop ro.product.marketname")
            model = self.adb_command('shell getprop ro.product.cert')
        elif brand == "huawei":
            name = self.adb_command("shell getprop ro.config.marketing_name")
            model = self.adb_command('shell getprop ro.product.cert')
        elif brand == "samsung":
            name = None
            model = self.adb_command('shell getprop ro.product.model')
        else:
            name = self.adb_command('shell getprop ro.product.name')
            model = self.adb_command('shell getprop ro.product.model')
        return name, model

    def save_to_excel(self):
        # 读取现有的 Excel 文件
        df = pd.read_excel(Device.device_info_path)

        # 计算新设备的序号
        new_order = df.shape[0] - 1  # 减去标题行
        self.device_order = new_order

        # 创建包含设备信息的新行
        new_device_info = pd.DataFrame([{
            '序号': new_order,
            '序列号': self.device_serial_number,
            '品牌': self.device_brand,
            '名称': self.device_name,
            '型号': self.device_model,
            '安卓版本': self.device_android_version,
            'SoC': self.device_soc,
            'RAM': self.device_ram
        }])

        # 使用 pd.concat 将新行追加到数据帧中
        df = pd.concat([df, new_device_info], ignore_index=True)

        # 将更新后的数据帧写回 Excel 文件
        df.to_excel(Device.device_info_path, sheet_name='base_info', index=False)

    def install_app(self, app_info):

        if app_info.get("install") and app_info.get("app_apk_path"):

            apk_path = app_info["app_apk_path"]

            print(f"Starting installation of {app_info.get('apk_name')} on device {self.device_name}.")

            result = self.adb_command(f'install "{apk_path}"')

            if 'Success' in result:

                print(f"Installed {app_info.get('apk_name')} on device {self.device_name}")
            else:

                print(f"Failed to install {app_info.get('apk_name')} on device {self.device_name}. Error: {result}")

    def uninstall_app(self, app_info):

        if app_info.get("uninstall") and app_info.get("app_package_name"):

            package_name = app_info["app_package_name"]
            # 检查应用是否已安装
            if self.is_app_installed(package_name):

                print(f"Software {app_info.get('apk_name')} installed on device {self.device_name}. Now starting to uninstall.")

                result = self.adb_command(f'uninstall {package_name}')

                if 'Success' in result or 'Failure' not in result:

                    print(f"Uninstalled {package_name} from device {self.device_name}")

                else:

                    print(f"Failed to uninstall {package_name} from device {self.device_name}. Error: {result}")

            else:

                print(f"App {package_name} is not installed on device {self.device_name}")

    def is_app_installed(self, package_name):

        if package_name:
            result = self.adb_command(f'shell pm list packages {package_name}')

            return package_name in result

        return False

    def launch_clashmini(self):

        if self.is_app_installed("com.supercell.clashmini"):
            # 启动 Clash Mini
            self.adb_command('shell am start -n com.supercell.clashmini/.GameApp')
            # 暂停一段时间后检查是否启动成功
            time.sleep(5)

            output = self.adb_command('shell ps')

            if 'com.supercell.clashmini' in output:

                print(f'设备{self.device_name} Clash Mini is running')

            else:

                print(f'设备{self.device_name} Clash Mini is not running')

        else:

            print(f'设备{self.device_name} 未安装 Clash Mini')


if __name__ == '__main__':
    device = Device()
