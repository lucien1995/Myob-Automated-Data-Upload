from flask import Flask, redirect, request, send_from_directory, url_for, jsonify
import requests
from urllib.parse import unquote  # 用来URI解码
from excel_to_json import excel_to_json
from session_handler import init_session, set_session_data, get_session_data, clear_session
import os
import sys
import json
import base64
import uuid
from datetime import datetime, timedelta

## when form EXE, using this commend, D: path is your packages path
# pyinstaller --onefile --paths "D:\\Python\\lib\\site-packages" --add-data "E:\\aKaplan\\Academic Intership\\flaskProject\\client\\build;client\build" app.py

app = Flask(__name__)

if getattr(sys, 'frozen', False):
    # 应用被打包
    app_root = sys._MEIPASS  # PyInstaller 创建的临时目录
else:
    # 应用未被打包
    app_root = os.path.dirname(os.path.abspath(__file__))

app.static_folder = os.path.join(app_root, 'client', 'build')

# 使用 session_handler.py 中的函数初始化会话
init_session(app)


# 特定的路由来提供 `client/build/static` 中的静态资源
@app.route('/static/js/<path:filename>')
def js_static(filename):
    # 将路径从 `static` 映射到 `client/build/static`
    js_dir = os.path.join(app.static_folder, 'static', 'js')
    return send_from_directory(js_dir, filename)


@app.route('/static/css/<path:filename>')
def css_static(filename):
    # 将路径从 `static` 映射到 `client/build/static`
    css_dir = os.path.join(app.static_folder, 'static', 'css')
    return send_from_directory(css_dir, filename)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@app.route('/')
def home():
    return 'Home - Click <a href="/get-auth-code">HERE</a> to get access token.'


@app.route('/get-auth-code')
def get_auth_code():
    set_session_data('MYOB_Key', 'dbb1f19c-a0ba-4a7d-84c3-42e9c0df9da7')
    set_session_data('MYOB_Secret', 'KMQ96gq23Qe26balJkkBPVEC')
    client_id = get_session_data('MYOB_Key')
    redirect_uri = "http://127.0.0.1:5000/myob-callback"  # 替换为你的重定向URI
    auth_url = f"https://secure.myob.com/oauth2/account/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=CompanyFile"
    return redirect(auth_url)


@app.route('/myob-callback')
def myob_callback():
    # 从请求参数中获取授权码
    authorization_code = request.args.get('code')
    print("we got code with encoded:\n" + authorization_code)

    decoded_auth_code = unquote(authorization_code)  # 解码
    print("\ndecoded as:\n" + authorization_code)
    print("\n\nStart POST request...")

    # 定义访问令牌的 URL 和请求正文
    MYOB_Key = get_session_data('MYOB_Key')
    MYOB_Secret = get_session_data('Secret')
    token_url = "https://secure.myob.com/oauth2/v1/authorize/"
    payload = {
        'client_id': MYOB_Key,
        'client_secret': MYOB_Secret,
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': 'http://127.0.0.1:5000/myob-callback'  # 确保这与您在MYOB注册应用时使用的redirect_uri相匹配
    }

    # 设置请求头
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # 发送 POST 请求获取访问令牌
    response = requests.post(token_url, headers=headers, data=payload)

    # 打印并返回响应的 JSON 数据
    # return response.json()
    response_data = response.json()
    # 访问不同的字段
    access_token = response_data["access_token"]
    expires_in = response_data["expires_in"]
    refresh_token = response_data["refresh_token"]
    user_uid = response_data["user"]["uid"]
    user_username = response_data["user"]["username"]
    print("response_data Got")
    set_session_data('User_Access',
                     {'access_token': access_token, 'expires_in': expires_in, 'refresh_token': refresh_token,
                      'user_uid': user_uid, 'user_username': user_username})
    # 设置请求的 URL
    url = "https://api.myob.com/accountright"

    # 设置请求头
    access_token = get_session_data('user_data', {}).get('access_token')
    headers = {
        'Authorization': f'Bearer {access_token}',
        'x-myobapi-key': MYOB_Key,
        'x-myobapi-version': 'v2',
        'Accept-Encoding': 'gzip,deflate'
    }
    print("一下是发送公司get请求头")
    print(headers)
    # 发送 GET 请求
    response_COMP = requests.get(url, headers=headers)

    # names_list = [{"Name": item["Name"]} for item in response_COMP]
    set_session_data('Company_List', response_COMP)

    # print COMP-Info
    redirect(url_for('company_select'))


@app.route('/api/get-companies')
def get_companies_from_session():
    # 从会话中获取公司列表
    companies = get_session_data('Company_List')
    # 检查公司列表是否存在
    if companies is None:
        return jsonify({'error': 'No company data available'}), 404

    data = json.loads(companies)
    extracted_data = [
        {"Name": item["Name"], "SerialNumber": item["SerialNumber"]}
        for item in data
    ]
    return jsonify(extracted_data)


@app.route('/CompanyDetail', methods=['POST'])
def company_detail():
    data = request.json
    selected_company = data['selectedCompany']
    username = data['username']
    password = data['password']
    # Coding cftoken
    credentials = f"{username}:{password}"
    credentials_bytes = credentials.encode('ascii')  # 转换为字节
    base64_credentials = base64.b64encode(credentials_bytes).decode('ascii')  # 进行 Base64 编码

    # 要查找的名称
    target_name = selected_company
    company_file_guid = ""
    # 遍历列表并查找目标名称
    company_list = get_session_data('Company_List')
    access_token = get_session_data('user_data', {}).get('access_token')
    MYOB_Key = get_session_data('MYOB_Key')

    try:
        # 检查是否存在公司列表
        if company_list:
            # 确保公司列表是 Python 对象
            if isinstance(company_list, str):
                company_list = json.loads(company_list)

            # 查找特定名称的公司
            for company in company_list:
                if company['name'] == target_name:
                    # 找到公司，存储其 UID
                    company_file_guid = company['uid']
                    print(f"找到的公司 UID 是: {company_file_guid}")
                    break
            # cmp file address
            company_file_uri = f"https://api.myob.com/accountright/{company_file_guid}"

            set_session_data('comp_uri', company_file_uri)
            set_session_data('cf_token', base64_credentials)

            return jsonify({"status": "success", "message": "Company details processed"}), 200
    except Exception as e:
        # 处理发生错误的情况
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/get-payroll-data')
def get_payroll_data():
    access_token = get_session_data('user_data', {}).get('access_token')
    MYOB_Key = get_session_data('MYOB_Key')
    Company_URI = get_session_data('comp_uri') + '/Contact/EmployeeStandardPay'
    CF_Token = get_session_data('cf_token')
    headers_Company = {
        'Authorization': f'Bearer {access_token}',
        'x-myobapi-cftoken': 'QVBJRGV2ZWxvcGVyOg==',
        'x-myobapi-key': MYOB_Key,
        'x-myobapi-version': 'v2',
        # 'Accept-Encoding': 'gzip,deflate'
        'Accept': 'application/json'
    }
    try:
        response_EmployeeStandardPay = requests.get(Company_URI, headers=headers_Company)
        set_session_data('EmployeeStandardPay', response_EmployeeStandardPay)

        Company_URI = get_session_data('comp_uri') + '/Contact/Customer'
        response_Customer = requests.get(Company_URI, headers=headers_Company)
        set_session_data('Customer', response_Customer)

        Company_URI = get_session_data('comp_uri') + '/GeneralLedger/Job'
        response_Job = requests.get(Company_URI, headers=headers_Company)
        set_session_data('Job', response_Job)

        Company_URI = get_session_data('comp_uri') + '/TimeBilling/Activity'
        response_Activity = requests.get(Company_URI, headers=headers_Company)
        set_session_data('Activity', response_Activity)

        return jsonify({"status": "success", "message": "Payroll Timesheet data fetched"}), 200
    except Exception as e:
        # 处理错误情况
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/timesheet-upload', methods=['POST'])
def timesheet_upload():
    # 检查是否有文件在请求中
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']

    # 如果用户没有选择文件，浏览器也会提交一个空的文件部分
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file:
        try:
            # 保存文件到服务器或处理文件
            # 例如，使用 Pandas 读取 Excel 文件
            # file.save(os.path.join('/path/to/save', file.filename))

            # 或直接读取文件内容
            excel_to_json(file)
            # 执行一些操作，例如数据解析
            # ...
            ##这里创建数据字典，减少session遍历次数，
            ##构建后，开始生成上传数据用的json
            final_data = get_session_data('Sessiondata_needEntry')
            employee_standard_pay = get_session_data('EmployeeStandardPay')
            job_data = get_session_data('Job')
            activity_data = get_session_data('Activity')
            customer_data = get_session_data('Customer')

            # 转换为字典，便于快速查找
            employee_dict = {emp['Name']: emp for emp in json.loads(employee_standard_pay)}
            job_dict = {job['JobName']: job['UID'] for job in json.loads(job_data)}
            activity_dict = {act['ActivityName']: act['UID'] for act in json.loads(activity_data)}
            customer_dict = {cust['CustomerName']: cust['UID'] for cust in json.loads(customer_data)}

            preview_upload = build_upload_payload(final_data, employee_dict, job_dict, activity_dict, customer_dict)
            # 转换 upload_payloads 列表为JSON字符串
            json_payload = json.dumps(preview_upload, indent=4)  # 使用indent参数美化输出，方便调试
            set_session_data("data_waiting_upload", json_payload)

            return jsonify(preview_upload), 200
        except Exception as e:
            return jsonify({'message': 'Error processing file', 'error': str(e)}), 500
    else:
        return jsonify({'message': 'An error occurred'}), 500


# 现在已经可以正确获取文件数据，payroll categories 只需要继续完成jobactivity和customer，note的编写，就可以开始录入了，(如果要把产品升级至真实的日常工作水平。需要确定payroll categories，OT，OT>2 以及对应的activity，需要的不仅仅是UID还有工作时间的计算。)
# 目前需要从文件中选出所有员工，然后搜索job，act之类的uid信息，
# 然后就可以整型json开始录入。
# 最后把内容显示在前端。
# 打包成exe
def build_upload_payload(final_data, employee_dict, job_dict, activity_dict, customer_dict):
    # 假设 final_data 是一个字典，包含所有员工的记录
    upload_payloads = []
    # 获取第一个员工的名字和记录
    first_employee_name, first_employee_categories = next(iter(final_data.items()))

    # 获取第一个记录的第一个类别的第一条记录
    first_category_key, first_records = next(iter(first_employee_categories.items()))
    first_record = first_records[0]
    start_date_iso, end_date_iso = get_week_range(first_record["Date"])
    # 获取起始日期和结束日期

    for name, categories in final_data.items():

        # 构建每条记录的上传格式
        new_record = {
            "Employee": {
                "UID": employee_dict[name]['UID'],  # 从employee_dict获取
                "Name": name,
                "DisplayID": employee_dict[name]['DisplayID'],
                "URI": employee_dict[name]['URI']
            },
            "StartDate": start_date_iso,
            "EndDate": end_date_iso,
            "Lines": []
        }

        # 遍历该员工的所有工作记录
        for category_key, records in categories.items():
            for record in records:
                # 在这里处理每一条工作记录
                # 假设 find_payroll_category_uid 等函数已经定义
                payroll_category_uid = find_payroll_category_uid(name, record["Pay- Category"], employee_dict)
                job_uid = job_dict.get(record["Job No"], {}).get('UID', None)
                activity_uid = activity_dict.get(record["Activity"], {}).get('UID', None)
                customer_uid = customer_dict.get(record["Customer"], {}).get('UID', None)

                # 构建 Lines 部分
                new_line = {
                    "PayrollCategory": {"UID": payroll_category_uid},
                    "Job": {"UID": job_uid},
                    "Activity": {"UID": activity_uid},
                    "Customer": {"UID": customer_uid},
                    "Notes": None,  # 假设 Notes 不从 record 中获取
                    "Entries": [{
                        "UID": generate_uid(),  # 假设有 generate_uid 函数生成唯一标识符
                        "Date": record["Date"],
                        "Hours": record["Total Hours Worked"],
                        "Processed": False
                    }]
                }
                new_record["Lines"].append(new_line)

        upload_payloads.append((employee_dict[name]['UID'], new_record))
        set_session_data('upload_payloads', upload_payloads)

    return upload_payloads


def generate_uid():
    return str(uuid.uuid4())


def find_payroll_category_uid(employee_name, category_name, employee_dict):
    """
    根据员工名和工资类别名称，找到对应的工资类别UID
    """
    emp_info = employee_dict.get(employee_name)
    if not emp_info:
        return None  # 员工信息不存在

    # 遍历员工的PayrollCategories查找匹配的类别
    for category in emp_info.get("PayrollCategories", []):
        if category["Name"] == category_name:
            return category["UID"]
    return None  # 未找到匹配的类别


def get_week_range(date_str):
    # 将日期字符串解析为 datetime 对象
    date = datetime.strptime(date_str, '%d-%b-%Y')

    # 找到当前日期所在周的周一
    start_of_week = date - timedelta(days=date.weekday())

    # 找到当前日期所在周的周日
    end_of_week = start_of_week + timedelta(days=6)

    # 将日期格式化为 ISO 8601 格式
    start_of_week_iso = start_of_week.strftime('%Y-%m-%dT00:00:00Z')
    end_of_week_iso = end_of_week.strftime('%Y-%m-%dT23:59:59Z')

    return start_of_week_iso, end_of_week_iso


@app.route('/api/confirm-upload', methods=['POST'])
def confirm_upload():
    # TODO:现在遇到的问题是，MYOB上传timesheet只能一个人一个人的上传，因此需要在build_upload_payload这里将每个人的记录拆分开，并且建立一个字典，对应着员工UID和上传信息 然后在这里遍历信息，生成URI进行批量循环上传。
    access_token = get_session_data('user_data', {}).get('access_token')
    MYOB_Key = get_session_data('MYOB_Key')
    Company_URI = get_session_data('comp_uri')
    CF_Token = get_session_data('cf_token')
    headers_Company = {
        'Authorization': f'Bearer {access_token}',
        'x-myobapi-cftoken': 'QVBJRGV2ZWxvcGVyOg==',
        'x-myobapi-key': MYOB_Key,
        'x-myobapi-version': 'v2',
        'Accept-Encoding': 'gzip,deflate',
        'Content-Type': 'application/json'
    }
    # 获取上传数据
    upload_payloads = get_session_data('upload_payloads')

    # 遍历上传数据
    for employee_uid, payload in upload_payloads:
        # 构建员工对应的 URI
        uri = f"{Company_URI}/Payroll/Timesheet/{employee_uid}"

        # 将 payload 转换为 JSON 格式
        json_payload = json.dumps(payload)

        # 发送请求上传数据
        response = requests.put(uri, headers=headers_Company, data=json_payload)

        # 检查响应状态码
        if response.ok:
            print(f"Data for employee with UID {employee_uid} uploaded successfully.")
        else:
            print(f"Failed to upload data for employee with UID {employee_uid}. Status code: {response.status_code}")

    # 根据需要返回响应
    clear_session()
    return jsonify({'message': 'Upload completed successfully'}), 200


#
# def fetch_employees(access_token, company_file_guid):
#     """
#     获取员工信息。
#
#     :param access_token: OAuth 2.0 访问令牌
#     :param company_file_guid: 公司文件的 GUID
#     :return: 员工信息的响应文本
#     """
#     # 构建 URL
#     # company_file_uri = f"https://api.myob.com/accountright/{company_file_guid}/Payroll/PayrollCategory"
#     # company_file_uri = f"https://api.myob.com/accountright/info"
#     # company_file_uri = f"https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/"
#     company_file_uri = f"https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Payroll/Timesheet"
#     # company_file_uri = f"https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Payroll/Timesheet/fd4d9cb3-2290-4351-89a7-2e984ce0590b?StartDate=2024-01-10T00:00:00&EndDate=2024-01-16T00:00:00"
#
#     # 设置请求头
#     headers_Company = {
#         'Authorization': f'Bearer {access_token}',
#         'x-myobapi-cftoken': 'QVBJRGV2ZWxvcGVyOg==',
#         'x-myobapi-key': 'dbb1f19c-a0ba-4a7d-84c3-42e9c0df9da7',
#         'x-myobapi-version': 'v2',
#         'Accept-Encoding': 'gzip,deflate'
#         # 'Accept': 'application/json'
#     }
#     print(headers_Company)
#     print(company_file_uri)
#
#     # 发送 GET 请求
#     response = requests.get(company_file_uri, headers=headers_Company)
#     print(response)
#     # return response.json()
#     # 返回响应文本
#
#     company_file_uri = f"https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Contact/Employee?$filter=DisplayID eq 'EMP00001'"
#     # company_file_uri = "https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Contact/EmployeePayrollDetails"
#     # company_file_uri = "https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Payroll/PayrollCategory"
#     # 设置请求头
#     headers_Company = {
#         'Authorization': f'Bearer {access_token}',
#         'x-myobapi-cftoken': 'QVBJRGV2ZWxvcGVyOg==',
#         'x-myobapi-key': 'dbb1f19c-a0ba-4a7d-84c3-42e9c0df9da7',
#         'x-myobapi-version': 'v2',
#         'Accept-Encoding': 'gzip,deflate'
#         # 'Accept': 'application/json'
#     }
#
#     # 发送 GET 请求
#     response = requests.get(company_file_uri, headers=headers_Company)
#     # return response.json()
#
#     url = "https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Payroll/Timesheet/fd4d9cb3-2290-4351-89a7-2e984ce0590b"
#     # url = "https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Contact/EmployeePayrollDetails"
#
#     payload = json.dumps({
#         "Employee": {
#             "UID": "fd4d9cb3-2290-4351-89a7-2e984ce0590b",
#             "Name": "Mary Jones",
#             "DisplayID": "EMP00001",
#             "URI": "https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Contact/Employee/fd4d9cb3-2290-4351-89a7-2e984ce0590b"
#         },
#         "StartDate": "2024-01-8T00:00:00Z",
#         "EndDate": "2024-01-14T00:00:00Z",
#         "Lines": [
#             {
#                 "PayrollCategory": {
#                     "UID": "abc070f6-fa2b-4d5d-815e-ca1c96f42f7e"
#                 },
#                 "Job": None,
#                 "Activity": None,
#                 "Customer": None,
#                 "Notes": "Annual Leave Request for May",
#                 "Entries": [
#                     {  # "UID": "ba951c0c-dfd8-4a18-bf0c-21ac533129c7",
#                         "Date": "2024-01-11T09:00:00",
#                         "Hours": 8,
#                         "Processed": False
#                     },
#                     {
#                         # "UID": "2968fb34-7ac9-45af-81c9-140468467c0f",
#                         "Date": "2024-01-12T09:00:00",
#                         "Hours": 8,
#                         "Processed": False
#                     },
#                     {
#                         # "UID": "d019be73-9e74-4efb-be00-2286bc639c1d",
#                         "Date": "2024-01-13T09:00:00",
#                         "Hours": 7.6,
#                         "Processed": False
#                     }
#                 ]
#             }
#         ]
#     })
#     headers = {
#         'Authorization': f'Bearer {access_token}',
#         'x-myobapi-cftoken': 'QVBJRGV2ZWxvcGVyOg==',
#         'x-myobapi-key': 'dbb1f19c-a0ba-4a7d-84c3-42e9c0df9da7',
#         'x-myobapi-version': 'v2',
#         'Accept-Encoding': 'gzip,deflate',
#         'Content-Type': 'application/json'
#     }
#
#     response = requests.request("PUT", url, headers=headers, data=payload)
#     a = response.text
#     print(a)
#     print("写入成功")
#
#     company_file_uri = f"https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Payroll/Timesheet"
#     headers_Company = {
#         'Authorization': f'Bearer {access_token}',
#         'x-myobapi-cftoken': 'QVBJRGV2ZWxvcGVyOg==',
#         'x-myobapi-key': 'dbb1f19c-a0ba-4a7d-84c3-42e9c0df9da7',
#         'x-myobapi-version': 'v2',
#         'Accept-Encoding': 'gzip,deflate'
#         # 'Accept': 'application/json'
#     }
#     # 发送 GET 请求
#     response = requests.get(company_file_uri, headers=headers_Company)
#     print(response)
#     return response.json()
#     # return "写入成功"


# 读取数据
def Enter_Data():
    excel_to_json("E:\\aKaplan\\Academic Intership\\temp\\1.xlsx", "E:\\aKaplan\\Academic Intership\\temp\\1.txt")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
