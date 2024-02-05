from flask import Flask, redirect, request, send_from_directory, url_for, jsonify
import requests
from urllib.parse import unquote  # 用来URI解码
from excel_to_json import excel_to_json
from session_handler import init_session, set_session_data, get_session_data, clear_session
import os
import json
import base64

app = Flask(__name__, static_folder='client/build')
# 使用 session_handler.py 中的函数初始化会话
init_session(app)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
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
            #'Accept-Encoding': 'gzip,deflate'
            'Accept': 'application/json'
        }
    try:
        response_EmployeeStandardPay = requests.get(Company_URI, headers=headers_Company)

        set_session_data('EmployeeStandardPay', response_EmployeeStandardPay)
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
        # 保存文件到服务器或处理文件
        # 例如，使用 Pandas 读取 Excel 文件
        # file.save(os.path.join('/path/to/save', file.filename))

        # 或直接读取文件内容
        excel_to_json(file,"E:\\aKaplan\\Academic Intership\\temp\\1.txt")
        # 执行一些操作，例如数据解析
        # ...



        return jsonify({'message': 'File processed successfully'}), 200

    return jsonify({'message': 'An error occurred'}), 500


def fetch_employees(access_token, company_file_guid):
    """
    获取员工信息。

    :param access_token: OAuth 2.0 访问令牌
    :param company_file_guid: 公司文件的 GUID
    :return: 员工信息的响应文本
    """
    # 构建 URL
    # company_file_uri = f"https://api.myob.com/accountright/{company_file_guid}/Payroll/PayrollCategory"
    # company_file_uri = f"https://api.myob.com/accountright/info"
    # company_file_uri = f"https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/"
    company_file_uri = f"https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Payroll/Timesheet"
    # company_file_uri = f"https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Payroll/Timesheet/fd4d9cb3-2290-4351-89a7-2e984ce0590b?StartDate=2024-01-10T00:00:00&EndDate=2024-01-16T00:00:00"

    # 设置请求头
    headers_Company = {
        'Authorization': f'Bearer {access_token}',
        'x-myobapi-cftoken': 'QVBJRGV2ZWxvcGVyOg==',
        'x-myobapi-key': 'dbb1f19c-a0ba-4a7d-84c3-42e9c0df9da7',
        'x-myobapi-version': 'v2',
        'Accept-Encoding': 'gzip,deflate'
        # 'Accept': 'application/json'
    }
    print(headers_Company)
    print(company_file_uri)

    # 发送 GET 请求
    response = requests.get(company_file_uri, headers=headers_Company)
    print(response)
    # return response.json()
    # 返回响应文本

    company_file_uri = f"https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Contact/Employee?$filter=DisplayID eq 'EMP00001'"
    # company_file_uri = "https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Contact/EmployeePayrollDetails"
    # company_file_uri = "https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Payroll/PayrollCategory"
    # 设置请求头
    headers_Company = {
        'Authorization': f'Bearer {access_token}',
        'x-myobapi-cftoken': 'QVBJRGV2ZWxvcGVyOg==',
        'x-myobapi-key': 'dbb1f19c-a0ba-4a7d-84c3-42e9c0df9da7',
        'x-myobapi-version': 'v2',
        'Accept-Encoding': 'gzip,deflate'
        # 'Accept': 'application/json'
    }

    # 发送 GET 请求
    response = requests.get(company_file_uri, headers=headers_Company)
    # return response.json()

    url = "https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Payroll/Timesheet/fd4d9cb3-2290-4351-89a7-2e984ce0590b"
    # url = "https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Contact/EmployeePayrollDetails"

    payload = json.dumps({
        "Employee": {
            "UID": "fd4d9cb3-2290-4351-89a7-2e984ce0590b",
            "Name": "Mary Jones",
            "DisplayID": "EMP00001",
            "URI": "https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Contact/Employee/fd4d9cb3-2290-4351-89a7-2e984ce0590b"
        },
        "StartDate": "2024-01-8T00:00:00Z",
        "EndDate": "2024-01-14T00:00:00Z",
        "Lines": [
            {
                "PayrollCategory": {
                    "UID": "abc070f6-fa2b-4d5d-815e-ca1c96f42f7e"
                },
                "Job": None,
                "Activity": None,
                "Customer": None,
                "Notes": "Annual Leave Request for May",
                "Entries": [
                    {  # "UID": "ba951c0c-dfd8-4a18-bf0c-21ac533129c7",
                        "Date": "2024-01-11T09:00:00",
                        "Hours": 8,
                        "Processed": False
                    },
                    {
                        # "UID": "2968fb34-7ac9-45af-81c9-140468467c0f",
                        "Date": "2024-01-12T09:00:00",
                        "Hours": 8,
                        "Processed": False
                    },
                    {
                        # "UID": "d019be73-9e74-4efb-be00-2286bc639c1d",
                        "Date": "2024-01-13T09:00:00",
                        "Hours": 7.6,
                        "Processed": False
                    }
                ]
            }
        ]
    })
    headers = {
        'Authorization': f'Bearer {access_token}',
        'x-myobapi-cftoken': 'QVBJRGV2ZWxvcGVyOg==',
        'x-myobapi-key': 'dbb1f19c-a0ba-4a7d-84c3-42e9c0df9da7',
        'x-myobapi-version': 'v2',
        'Accept-Encoding': 'gzip,deflate',
        'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    a = response.text
    print(a)
    print("写入成功")

    company_file_uri = f"https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Payroll/Timesheet"
    headers_Company = {
        'Authorization': f'Bearer {access_token}',
        'x-myobapi-cftoken': 'QVBJRGV2ZWxvcGVyOg==',
        'x-myobapi-key': 'dbb1f19c-a0ba-4a7d-84c3-42e9c0df9da7',
        'x-myobapi-version': 'v2',
        'Accept-Encoding': 'gzip,deflate'
        # 'Accept': 'application/json'
    }
    # 发送 GET 请求
    response = requests.get(company_file_uri, headers=headers_Company)
    print(response)
    return response.json()
    # return "写入成功"


# 读取数据
def Enter_Data():
    excel_to_json("E:\\aKaplan\\Academic Intership\\temp\\1.xlsx", "E:\\aKaplan\\Academic Intership\\temp\\1.txt")


if __name__ == '__main__':
    app.run(debug=True)
