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


connect_device("Android:///")
device = device()

start_app("com.ss.android.ugc.aweme")