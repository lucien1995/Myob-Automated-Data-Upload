from flask import Flask, redirect, request
import requests
from urllib.parse import unquote  #用来URI解码
from excel_to_json import excel_to_json

import json

app = Flask(__name__)

@app.route('/')
def home():
    return 'Home - Click <a href="/get-auth-code">HERE</a> to get access token.'

@app.route('/get-auth-code')
def get_auth_code():
    client_id = "dbb1f19c-a0ba-4a7d-84c3-42e9c0df9da7"
    redirect_uri = "http://127.0.0.1:5000/myob-callback"  # 替换为你的重定向URI
    auth_url = f"https://secure.myob.com/oauth2/account/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=CompanyFile"
    return redirect(auth_url)

@app.route('/myob-callback')
def myob_callback():
    # 从请求参数中获取授权码
    authorization_code = request.args.get('code')
    print("we got code with encoded:\n"+ authorization_code)

    decoded_auth_code = unquote(authorization_code) #解码
    print("\ndecoded as:\n" + authorization_code)
    print("\n\nStart POST request...")

    # 定义访问令牌的 URL 和请求正文
    token_url = "https://secure.myob.com/oauth2/v1/authorize/"
    payload = {
        'client_id': 'dbb1f19c-a0ba-4a7d-84c3-42e9c0df9da7',
        'client_secret': 'KMQ96gq23Qe26balJkkBPVEC',
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
    #return response.json()
    response_data = response.json()
    # 访问不同的字段
    access_token = response_data["access_token"]
    expires_in = response_data["expires_in"]
    refresh_token = response_data["refresh_token"]
    user_uid = response_data["user"]["uid"]
    user_username = response_data["user"]["username"]
    print("response_data===")
    print(response_data)
   # 设置请求的 URL
    url = "https://api.myob.com/accountright"

    # 使用您实际的访问令牌和 MYOB API 密钥
    myob_api_key = "dbb1f19c-a0ba-4a7d-84c3-42e9c0df9da7"

    # 设置请求头
    headers = {
        'Authorization': f'Bearer {access_token}',
        'x-myobapi-key': myob_api_key,
        'x-myobapi-version': 'v2',
        'Accept-Encoding': 'gzip,deflate'
    }
    print("一下是发送公司get请求头")
    print(headers)
    # 发送 GET 请求
    response_COMP = requests.get(url, headers=headers)

    # 打印响应内容-全部公司
    #return response_COMP.json()

    # 要查找的名称
    target_name = "MYOB Shared Sandbox 15"
    company_file_guid = ""
    CompanyFilesList = response_COMP.json()
    # 遍历列表并查找目标名称
    for item in CompanyFilesList:
        if item["Name"] == target_name:
            # 找到匹配项，处理或返回该项
            print("找到匹配项:", item)
            company_file_guid = "aecd5b98-3a05-4e2d-ac54-814d8d698952"  # 替换为您的公司文件GUID
            print("\n\nRequest employees-info...")
            print("\n...")
            print("Employees details\n")
            print(company_file_guid)
            print(access_token)
            break
            #return item
    else:
        print("没有找到匹配的公司项")

    #查找公司下全部员工信息

    return fetch_employees(access_token, company_file_guid)


def fetch_employees(access_token, company_file_guid):
    """
    获取员工信息。

    :param access_token: OAuth 2.0 访问令牌
    :param company_file_guid: 公司文件的 GUID
    :return: 员工信息的响应文本
    """
    # 构建 URL
    #company_file_uri = f"https://api.myob.com/accountright/{company_file_guid}/Payroll/PayrollCategory"
    #company_file_uri = f"https://api.myob.com/accountright/info"
    #company_file_uri = f"https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/"
    company_file_uri = f"https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Payroll/Timesheet"
    #company_file_uri = f"https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Payroll/Timesheet/fd4d9cb3-2290-4351-89a7-2e984ce0590b?StartDate=2024-01-10T00:00:00&EndDate=2024-01-16T00:00:00"

    # 设置请求头
    headers_Company = {
        'Authorization': f'Bearer {access_token}',
        'x-myobapi-cftoken': 'QVBJRGV2ZWxvcGVyOg==',
        'x-myobapi-key': 'dbb1f19c-a0ba-4a7d-84c3-42e9c0df9da7',
        'x-myobapi-version': 'v2',
        'Accept-Encoding': 'gzip,deflate'
        #'Accept': 'application/json'
    }
    print(headers_Company)
    print(company_file_uri)

    # 发送 GET 请求
    response = requests.get(company_file_uri, headers=headers_Company)
    print(response)
    #return response.json()
    # 返回响应文本

    company_file_uri = f"https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Contact/Employee?$filter=DisplayID eq 'EMP00001'"
    #company_file_uri = "https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Contact/EmployeePayrollDetails"
    #company_file_uri = "https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Payroll/PayrollCategory"
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
    #return response.json()

    url = "https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Payroll/Timesheet/fd4d9cb3-2290-4351-89a7-2e984ce0590b"
    #url = "https://arl2.api.myob.com/accountright/c086f5e8-c459-4a49-88b2-bf7a6c82213e/Contact/EmployeePayrollDetails"

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
                    {
                        #"UID": "ba951c0c-dfd8-4a18-bf0c-21ac533129c7",
                        "Date": "2024-01-11T09:00:00",
                        "Hours": 8,
                        "Processed": False
                    },
                    {
                        #"UID": "2968fb34-7ac9-45af-81c9-140468467c0f",
                        "Date": "2024-01-12T09:00:00",
                        "Hours": 8,
                        "Processed": False
                    },
                    {
                        #"UID": "d019be73-9e74-4efb-be00-2286bc639c1d",
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
    a=response.text
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
    #return "写入成功"

#读取数据
def Enter_Data():
    excel_to_json("E:\\aKaplan\\Academic Intership\\temp\\1.xlsx","E:\\aKaplan\\Academic Intership\\temp\\1.txt" )


if __name__ == '__main__':
    app.run(debug=True)