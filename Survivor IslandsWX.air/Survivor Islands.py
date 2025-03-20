# -*- encoding=utf8 -*-
__author__ = "shihao.li"

from airtest.core.api import *
import time

auto_setup(__file__)

def ShareButton():
    sleep(1)
    touch(Template(r"tpl1742283951350.png", record_pos=(-0.006, 0.229), resolution=(720, 1600)))
    sleep(1)
    touch(Template(r"tpl1742283992155.png", record_pos=(-0.207, -0.203), resolution=(720, 1600)))
    touch(Template(r"tpl1742284020462.png", record_pos=(0.163, 0.886), resolution=(720, 1600)))
    sleep(1)

def code_A():
    touch(Template(r"tpl1742283671257.png", record_pos=(-0.408, 0.708), resolution=(720, 1600)))
    sleep(1)
    if exists(Template(r"tpl1742283757134.png", record_pos=(0.003, 0.164), resolution=(720, 1600))):
        touch(Template(r"tpl1742283772961.png", record_pos=(-0.26, 0.84), resolution=(720, 1600)))
        sleep(1)
        ShareButton()
        touch(Template(r"tpl1742284053071.png", record_pos=(0.0, 0.889), resolution=(720, 1600)))
        sleep(1)
        touch(Template(r"tpl1742284107515.png", record_pos=(0.242, 0.812), resolution=(720, 1600)))
        sleep(1)
        ShareButton()
        sleep(1)
        if exists(Template(r"tpl1742284053071.png", record_pos=(0.0, 0.889), resolution=(720, 1600))):
            touch(Template(r"tpl1742284053071.png", record_pos=(0.0, 0.889), resolution=(720, 1600)))
        else:
            if exists(Template(r"tpl1742293962300.png", record_pos=(0.424, -0.789), resolution=(720, 1600))):
                touch(Template(r"tpl1742291549047.png", record_pos=(0.418, -0.792), resolution=(720, 1600)))

def code_B():
    touch(Template(r"tpl1742286023776.png", record_pos=(0.417, -0.65), resolution=(720, 1600)))
    sleep(1)
    touch(Template(r"tpl1742286042790.png", record_pos=(-0.003, 0.344), resolution=(720, 1600)))
    ShareButton()
    sleep(1)
   
def code_C():
    touch(Template(r"tpl1742283671257.png", record_pos=(-0.408, 0.708), resolution=(720, 1600)))
    sleep(1)
    if exists(Template(r"tpl1742283757134.png", record_pos=(0.003, 0.164), resolution=(720, 1600))):
        touch(Template(r"tpl1742287159759.png", record_pos=(-0.315, -0.406), resolution=(720, 1600)))
        sleep(1)
        if exists(Template(r"tpl1742288268861.png", record_pos=(-0.011, 0.322), resolution=(720, 1600))):
            ShareButton()
            sleep(40)
            touch(Template(r"tpl1742288357121.png", record_pos=(-0.006, 0.714), resolution=(720, 1600)))
            sleep(1)
            touch(Template(r"tpl1742288385557.png", record_pos=(0.367, -0.365), resolution=(720, 1600)))
            sleep(1)
            touch(Template(r"tpl1742287859442.png", record_pos=(0.419, -0.792), resolution=(720, 1600)))
            touch(Template(r"tpl1742288268861.png", record_pos=(-0.011, 0.322), resolution=(720, 1600)))
        elif exists(Template(r"tpl1742292469738.png", record_pos=(-0.019, 0.311), resolution=(720, 1600))):
            touch(Template(r"tpl1742292490806.png", record_pos=(-0.015, 0.318), resolution=(720, 1600)))
            ShareButton()
            sleep(40)
            touch(Template(r"tpl1742288357121.png", record_pos=(-0.006, 0.714), resolution=(720, 1600)))
            sleep(1)
            touch(Template(r"tpl1742292769942.png", record_pos=(-0.003, 0.311), resolution=(720, 1600)))
            ShareButton()
            sleep(40)
            touch(Template(r"tpl1742288357121.png", record_pos=(-0.006, 0.714), resolution=(720, 1600)))
            sleep(1)
            touch(Template(r"tpl1742288385557.png", record_pos=(0.367, -0.365), resolution=(720, 1600)))
            sleep(1)
            touch(Template(r"tpl1742287859442.png", record_pos=(0.419, -0.792), resolution=(720, 1600)))
        
        
start_time = time.time()
while True:
    elapsed_time = time.time() - start_time
    if elapsed_time % 217 < 1:  # 每 217 秒运行一次代码 B
        code_B()
    elif elapsed_time % 7300 < 1:
        code_C()
    elif elapsed_time % 300 < 1:  # 每 300秒 运行一次代码 A
        code_A()

        
    time.sleep(1)