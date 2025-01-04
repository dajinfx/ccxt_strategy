import csv
import chardet

class OperationCSV:
    def __init__(self, root_path, filename):
        self.root_path = root_path
        self.filename = filename
        self.full_path = f"{self.root_path}/{self.filename}"

    def detect_encoding(self):
        with open(self.full_path, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding']

    def remove_null_bytes(self):
        with open(self.full_path, 'rb') as file:
            content = file.read()
        content = content.replace(b'\x00', b'')  # 去除 NUL 字符
        with open(self.full_path, 'wb') as file:
            file.write(content)

    def add_row_if_empty(self,new_row_value):
        rows = []
        inserted = False

        # 检测文件编码
        encoding = self.detect_encoding()
        if encoding is None:
            encoding = 'utf-8'  # 如果检测失败，使用默认编码

        # 读取现有的 CSV 文件内容
        with open(self.full_path, mode='r', newline='', encoding=encoding, errors='ignore') as file:
            reader = csv.reader(file)
            try:
                header = next(reader)  # 获取表头
                rows.append(header)    # 保存表头到rows中
            except StopIteration:
                print("File is empty or only contains null bytes.")
                
            for row in reader:
                if not inserted and all(cell.strip() for cell in row):
                    rows.append(row)
                    #print("rows.append(row)  ",row)
                else:
                    #print("Insert row: ",row)
                    rows.append(row)

        # 如果没有插入新行，则在文件末尾添加新行
        if not inserted:
            rows.append(new_row_value)

        # 写回 CSV 文件
        with open(self.full_path, mode='w', newline='', encoding=encoding, errors='ignore') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    def update_csv_rows(self, order_text, new_values):
        rows = []

        # 检测文件编码
        encoding = self.detect_encoding()
        if encoding is None:
            encoding = 'utf-8'  # 如果检测失败，使用默认编码
        print(f"Detected encoding: {encoding}")

        # 移除文件中的 NUL 字符
        self.remove_null_bytes()

        # 读取现有的 CSV 文件内容
        with open(self.full_path, mode='r', newline='', encoding=encoding, errors='ignore') as file:
            reader = csv.reader(file)
            header = next(reader)  # 获取表头
            rows.append(header)    # 保存表头到rows中
            checked = 0;
            for row in reader:
                if row[0] == order_text:  # 在 A 列中匹配 match_value
                    if row[8] == 'open' and checked == 0:
                        while len(row) < 15:  # 确保行有足够的列
                            row.append('')
                        row[8:15] = new_values  # 更新 E, F, G, H, I, J, K 列的值
                        checked = 1
                    elif row[8] == 'open' and checked == 1:
                        row[8] = 'closed';
                rows.append(row)    

        # 写回 CSV 文件
        with open(self.full_path, mode='w', newline='', encoding=encoding, errors='ignore') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        
        

    def check_open_order(self, order_text):
        rows = []
        # 检测文件编码
        encoding = self.detect_encoding()
        if encoding is None:
            encoding = 'utf-8'  # 如果检测失败，使用默认编码
        print(f"Detected encoding: {encoding}")
        # 读取现有的 CSV 文件内容
        with open(self.full_path, mode='r', newline='', encoding=encoding, errors='ignore') as file:
            reader = csv.reader(file)
            header = next(reader)  # 获取表头
            #rows.append(header)    # 保存表头到rows中
            checked = 0;
            for row in reader:
                if row[0] == order_text:  # 在 A 列中匹配 match_value
                    if row[8] == 'open':
                        rows.append(row) 
        return rows;





