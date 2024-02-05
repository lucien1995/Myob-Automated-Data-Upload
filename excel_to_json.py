# This is a sample Python script.
import pandas as pd
from session_handler import init_session, set_session_data, get_session_data, clear_session

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def excel_to_json(file, output_file):
    pay_categories = set()
    customers = set()
    activities = set()
    job_nos = set()
    # 使用pandas读取Excel文件
    try:
        df = pd.read_excel(file, header=3, parse_dates=['Date'])
    except Exception as e:
        print(f"读取Excel文件时出错：{e}")
        return

    # 格式化日期列为指定的格式
    df['Date'] = df['Date'].dt.strftime('%d-%b-%Y').str.upper()
    # 处理“name”列中的姓名，将姓和名的位置互换
    df['Name'] = df['Name'].apply(swap_names)

    # 将DataFrame转换为JSON格式
    try:
        json_data = df.to_json(orient='records', force_ascii=False, lines=True)
        summarize_data(json_data)
    except Exception as e:
        print(f"转换为JSON时出错：{e}")
        return

    # 将JSON数据写入文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_data)
    except Exception as e:
        print(f"写入文件时出错：{e}")
        return

    print(f"数据已转换为JSON并保存在 {output_file}")


# 处理“Notes”列中的姓名，将姓和名的位置互换
def swap_names(name):
    parts = name.split()
    p_l = len(parts)
    # 当存在两个或更多的名字部分时进行互换
    if p_l == 2:
        return ' '.join(parts[-1:] + parts[:-1])
    if p_l > 2:
        return ' '.join(parts[-2:] + parts[:-2])
    return name  # 如果只有一个名字部分则不变

def summarize_data(raw_data):
    # 初始化集合用于存储唯一值
    pay_categories = set()
    customers = set()
    activities = set()
    job_nos = set()

    # 遍历数据，提取信息
    for entry in raw_data:
        pay_categories.add(entry["Pay- Category"])
        customers.add(entry["Customer"])
        activities.add(entry["Activity"])
        job_nos.add(entry["Job No"])

    # 将集合转换为列表并保存在 Flask 会话中
    set_session_data('PayCategorySummary',  list(pay_categories))
    set_session_data('CustomerSummary',  list(customers))
    set_session_data('ActivitySummary',  list(activities))
    set_session_data('JobNoSummary',  list(job_nos))


# 使用示例
# file_path = 'path_to_your_excel_file.xlsx'  # 替换为你的Excel文件路径
# output_file = 'output.json'  # 输出JSON文件的名称
# excel_to_json(file_path, output_file)


# if __name__ == '__main__':
#    print_hi('PyCharm')
#    excel_to_json("E:\\aKaplan\\Academic Intership\\temp\\1.xlsx","E:\\aKaplan\\Academic Intership\\temp\\1.txt" )
