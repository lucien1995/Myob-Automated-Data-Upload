# This is a sample Python script.
import pandas as pd
from session_handler import init_session, set_session_data, get_session_data, clear_session
from collections import defaultdict
import json
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def excel_to_json(file):
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
###########################################################################
    # 初始化一个字典来存储整理后的数据
    grouped_data = defaultdict(lambda: defaultdict(list))

    # 遍历DataFrame中的每一行
    for index, row in df.iterrows():
        name = row['Name']
        category = row['Pay- Category']
        job_no = row['Job No']
        activity = row['Activity']
        customer = row['Customer']


        # 构建二级分类的唯一标识符，确保相同的组合被归到一起
        category_key = (category, job_no, activity, customer)

        # 构建这个组合的数据记录
        record = {
            "Date": row["Date"],
            "Start": row["Start"],
            "End": row["End"],
            "Total Hours Worked": row["Total Hours Worked"],
            "Total Hours After MOT and LD": row["Total Hours After MOT and LD"],
            "Base Rate": row["Base Rate"],
            "Rate As per Day": row["Rate As per Day"],
            "Consultant": row["Consultant"],
            "OT Rate": row["OT Rate"],
            "OT >2": row["OT >2"],
            "Day": row["Day"],
            "Activity WITHOUT TRIM": row["Activity WITHOUT TRIM"],
            "Decuction - Lunch Break": row["Decuction - Lunch Break"],
            "Morining OT Hours": row["Morining OT Hours"],
            "Evening OT Hours": row["Evening OT Hours"],
            "Total OT Test": row["Total OT Test"],
            "Total OT": row["Total OT"],
            "Base Hours No need": row["Base Hours No need"],
            "Emp Base Hours": row["Emp Base Hours"],
            " Emp OT Rate $": row[" Emp OT Rate $"],
            "Base Rate $": row["Base Rate $"],
            "Total Earnings": row["Total Earnings"],
            # 可以继续添加其他需要的字段
        }

        # 将记录添加到正确的分类中
        grouped_data[name][category_key].append(record)

    # 转换为最终需要的格式
    final_data = {
        name: [{"Pay- Category": key[0], "Job No": key[1], "Activity": key[2], "Customer": key[3], "Records": records}
               for key, records in categories.items()]
        for name, categories in grouped_data.items()}

    Sessiondata_needEntry = json.dumps(final_data)
    set_session_data("Sessiondata_needEntry", Sessiondata_needEntry)
    #####################################################################

    # 将DataFrame转换为JSON格式
    try:
        json_data = df.to_json(orient='records', force_ascii=False, lines=True)
        summarize_data(json_data)
        set_session_data("Excel_data", json_data)
    except Exception as e:
        print(f"转换为JSON时出错：{e}")
        return

    # 将JSON数据写入文件


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
