import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- 1. 连接 Google Sheets 的“魔法” ---
def get_gspread_client():
    # 这里就是增加后的双重权限 scope
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

# 尝试连接表格 (完整的 try-except 结构，防止语法错误)
try:
    client = get_gspread_client()
    # 【注意】确保这里的名字和你 Google 表格文件名完全一样
    sheet = client.open("My_Drink_Lab_Data").sheet1 
except Exception as e:
    st.error(f"连接失败！请检查：1.表格名 2.共享邮箱。 报错详情: {e}")
    st.stop()

# --- 2. 界面设计 ---
st.set_page_config(page_title="秋秋的饮品实验室", page_icon="🍹")
st.title("🍹 秋秋的饮品实验室")

# 侧边栏输入
with st.sidebar:
    st.header("📝 记录新配方")
    name = st.text_input("饮品名称")
    recipe = st.text_area("调制公式")
    
    if st.button("保存到云端"):
        if name and recipe:
            sheet.append_row([name, recipe])
            st.success("✨ 存好啦！数据已飞进表格。")
        else:
            st.error("名字和配方都得填哦！")

# --- 3. 实时展示 ---
st.subheader("📖 藏书阁（实时更新）")
data = sheet.get_all_records()

if not data:
    st.info("目前还没有配方，快去左边加一个吧！")
else:
    for item in reversed(data):
        with st.expander(f"🍸 {item['名称']}"):
            st.write(item['配方'])
