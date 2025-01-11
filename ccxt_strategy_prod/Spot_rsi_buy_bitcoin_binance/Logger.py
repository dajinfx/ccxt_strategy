import os
from datetime import datetime

class Logger:
    def __init__(self, file_path):
        # 如果 file_path 没有包含目录路径，则默认使用当前目录
        if not os.path.dirname(file_path):
            self.file_path = os.path.join(os.getcwd(), file_path)
        else:
            self.file_path = file_path
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        # 获取文件目录路径
        directory = os.path.dirname(self.file_path)
        # 创建目录（如果目录不存在）
        if directory and not os.path.exists(directory):
            print("create file self.file_path: ",self.file_path)
            os.makedirs(directory)

    def write_log(self, message):
        current_time = datetime.now().strftime("%Y/%m/%d %I:%M:%S %p")
        log_entry = f"------ {current_time} -----{message}\n"
        print("write_log: ",message)
        
        # 写入日志文件前检查文件行数
        self.check_and_trim_log_file()
        
        # 将新日志条目添加到文件顶部
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r+', encoding='utf-8') as file:
                existing_lines = file.readlines()
                file.seek(0)
                file.write(log_entry)
                file.writelines(existing_lines)
        else:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                file.write(log_entry)

    def check_and_trim_log_file(self):
        # 检查文件行数，超过300行则删除前100行
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r+', encoding='utf-8') as file:
                lines = file.readlines()
                if len(lines) > 300:
                    # 保留后面的行
                    lines = lines[100:]
                    # 回写文件内容
                    file.seek(0)
                    file.writelines(lines)
                    file.truncate()

    def getAbPath(self):
        current_script_path = os.path.abspath(__file__)
        return current_script_path