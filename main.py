import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- 1. 连接设置 ---
def get_gspread_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

# 尝试连接
try:
    client = get_gspread_client()
    # 这里的名字确保和你的表格名 My_Drink_Lab_Data 一致
    sheet = client.open("My_Drink_Lab_Data").sheet1 
except Exception as e:
    st.error(f"连接失败: {e}")
    st.stop()

# --- 2. 界面设计 ---
st.set_page_config(page_title="秋秋的饮品实验室", page_icon="🍹")
st.title("🍹 秋秋的饮品实验室")

# 侧边栏：录入数据
with st.sidebar:
    st.header("📝 记录新配方")
    name = st.text_input("饮品名称")
    recipe = st.text_area("调制公式")
    
    if st.button("保存到云端"):
        if name and recipe:
            with st.spinner('正在上传...'):
                sheet.append_row([name, recipe])
                st.success("✅ 存好啦！")
                # 强制刷新以显示新数据
                st.rerun()
        else:
            st.error("请填完名称和配方！")

# --- 3. 数据展示 (增加空表格处理) ---
st.subheader("📖 实验室配方清单")

try:
    # 获取所有数据
    data = sheet.get_all_records()
    
    if not data:
        st.info("💡 表格目前是空的，快在左侧录入你的第一个配方吧！")
    else:
        # 倒序显示
        for item in reversed(data):
            with st.expander(f"🍸 {item.get('名称', '未命名')}"):
                st.write(f"**调制秘籍：**\n{item.get('配方', '暂无内容')}")
except Exception as e:
    # 如果表格完全没有数据行，gspread 有时会抛错，这里做一个友好提示
    st.info("💡 实验室准备就绪！请在左侧侧边栏添加第一个饮品配方。")
