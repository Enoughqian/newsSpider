import streamlit as st
from app.io.session import engine
from app.model.login_info import LoginInfo
from sqlmodel import Session, select, update, func, or_

def get_all_info():
    with Session(engine, autoflush=False) as db:
        smt = select(LoginInfo)
        all_login_info = db.exec(smt).all()
    # 获取所有账号密码
    result = {}
    for temp in all_login_info:
        result[temp.name] = temp.password
    return result


