def read_txt_file(file_path, create_if_not_found=False):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        if create_if_not_found:
            # 创建文件如果它不存在
            with open(file_path, 'w') as file:
                pass
            print(f"创建文件")
        read_txt_file(file_path, True)
        return None
    except Exception as e:
        print(f"读取文件时出错：{e}")
        return None


def save_txt_data(new_txt_data, name_txt_path):
    saved_name = read_txt_file(name_txt_path, create_if_not_found=True)
    if saved_name == new_txt_data:
        print("The txt data has been saved successfully.")
        return True
    else:
        try:
            with open(name_txt_path, 'w') as f:
                f.write(new_txt_data)
            return False
        except Exception as e:
            print(f"保存文件名时出错：{e}")
            return False
