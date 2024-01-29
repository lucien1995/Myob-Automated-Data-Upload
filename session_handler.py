from flask import session
from flask_session import Session
import os
def init_session(app):
    # 设置 Flask 的 SECRET_KEY
    app.secret_key = os.urandom(24)
    app.config['SECRET_KEY'] = app.secret_key
    # 配置会话存储在服务器端的文件系统
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_FILE_THRESHOLD'] = 100  # 最多存储的文件个数
    # 初始化 Session 对象
    Session(app)

def set_session_data(key, value):
    session[key] = value

def get_session_data(key):
    return session.get(key)

def clear_session():
    session.clear()