import json
import tkinter as tk
from tkinter import ttk, filedialog

# 从 JSON 文件中加载数据
json_file_path = 'apk_info.json'


def load_data():
    with open(json_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


data = load_data()


# def save_selection(value):
#     # 更新 test_package_name 的值，并保存到 JSON 文件中
#     data["data"]["test_package_name"] = value
#     print(f"选择的包名: {value}")
#
#     # 如果包名不在现有列表中，添加到package_name_list
#     if value not in data["config"]["package_name_list"]:
#         data["config"]["package_name_list"].append(value)
#
#     with open(json_file_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)
#     print("数据已保存")

def save_selection(value):
    # 更新 test_package_name 的值，并保存到 JSON 文件中
    data["data"]["test_package_name"] = value
    print(f"选择的包名: {value}")

    # 如果包名不在现有列表中，添加到 package_name_list
    if value not in data["config"]["package_name_list"]:
        data["config"]["package_name_list"].append(value)

    # 读取当前表单的内容
    current_forms_data = {}
    for serial_number_var, device_var, apk_channel_var, path_var in forms:
        device = device_var.get()
        apk_channel = apk_channel_var.get()
        path = path_var.get()

        # 如果序列号已经存在，追加到列表中，否则创建新列表
        if device in current_forms_data:
            current_forms_data[device].append({
                "apk_channel": apk_channel,
                "apk_path": path,
                "package_name": value
            })
        else:
            current_forms_data[device] = [{
                "apk_channel": apk_channel,
                "apk_path": path,
                "package_name": value
            }]

    # 更新或新增包名对应的数据
    if value in data["data"]:
        data["data"][value].update(current_forms_data)
    else:
        data["data"][value] = current_forms_data

    # 保存到 JSON 文件
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("数据已保存")


def load_forms_for_package(package_name):
    # 清除现有表单
    for widgets in root.grid_slaves():
        if int(widgets.grid_info()["row"]) > 1:
            widgets.destroy()
    forms.clear()

    # 获取对应包名的数据
    package_data = data["data"].get(package_name, {})

    # 遍历序列号和对应列表，生成表单
    row = 2
    for serial_number, details_list in package_data.items():
        for details in details_list:
            add_form(serial_number, serial_number, details["apk_channel"], details["apk_path"], row)
            row += 2


def add_form(serial_number="", device="", apk_channel="", path="", row=None):
    # 添加一个新的表单
    if row is None:
        row = (len(forms) + 1) * 2

    serial_number_var = tk.StringVar(value=serial_number)
    device_var = tk.StringVar(value=device)
    apk_channel_var = tk.StringVar(value=apk_channel)
    path_var = tk.StringVar(value=path)

    # 第一行
    serial_number_label = tk.Label(root, text="serial_number", width=20)
    serial_number_label.grid(row=row, column=0, padx=5, pady=5)

    device_combobox = ttk.Combobox(root, textvariable=device_var, values=data["config"]["devices_list"], width=20)
    device_combobox.grid(row=row, column=1, padx=5, pady=5)

    apk_channel_label = tk.Label(root, text="apk_channel", width=20)
    apk_channel_label.grid(row=row, column=2, padx=5, pady=5)

    apk_channel_combobox = ttk.Combobox(root, textvariable=apk_channel_var, values=data["config"]["apk_channel_list"],
                                        width=20)
    apk_channel_combobox.grid(row=row, column=3, padx=5, pady=5)

    # 第二行
    path_entry = tk.Entry(root, textvariable=path_var, width=150)
    path_entry.grid(row=row + 1, column=0, columnspan=3, padx=5, pady=5)

    path_button = tk.Button(root, text="选择文件", command=lambda: select_file(path_var))
    path_button.grid(row=row + 1, column=3, padx=5, pady=5)

    forms.append((serial_number_var, device_var, apk_channel_var, path_var))


def select_file(path_var):
    file_path = filedialog.askopenfilename()
    if file_path:
        path_var.set(file_path)


def on_package_name_change(*args):
    # 当包名变化时调用的函数
    current_package = combo_value.get()
    load_forms_for_package(current_package)


# 创建主窗口
root = tk.Tk()
root.title("APK 信息管理")

# 上部：包名选择区域
param_label = tk.Label(root, text="test_package_name")
param_label.grid(row=0, column=0, padx=10, pady=10)

combo_value = tk.StringVar()
combo_value.trace('w', on_package_name_change)

package_name_combobox = ttk.Combobox(root, textvariable=combo_value, width=40)
package_name_combobox['values'] = data["config"]["package_name_list"]
# package_name_combobox.set(data["data"]["test_package_name"])
package_name_combobox.grid(row=0, column=1, padx=10, pady=10)

save_button = tk.Button(root, text="保存", command=lambda: save_selection(combo_value.get()))
save_button.grid(row=0, column=2, padx=10, pady=10)

# 下部：包数据显示区域
forms = []
add_form_button = tk.Button(root, text="+", command=add_form)
add_form_button.grid(row=0, column=3, columnspan=10, pady=10)

# 初始化表单
# load_forms_for_package(data["data"]["test_package_name"])

# 运行主循环
root.mainloop()
