import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- 1. 连接 Google Sheets 的魔法 ---
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    # 这里的名字要和你在 Secrets 里写的 [gcp_service_account] 一致
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

# 尝试连接表格
try:
    client = get_gspread_client()
    # 【核心】这里必须是你 Google 表格的准确名字！
    # 把这一段替换掉原来的 scope
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
except Exception as e:
    st.error(f"连接表格失败，请检查表格名字。错误原因: {e}")
    st.stop()

# --- 2. 界面设置 ---
st.set_page_config(page_title="秋秋的饮品实验室", page_icon="🍹")
st.title("🍹 秋秋的饮品实验室")

# 侧边栏：用来输入新配方
with st.sidebar:
    st.header("✨ 记录新配方")
    new_name = st.text_input("饮品名称")
    new_recipe = st.text_area("调制公式")
    
    if st.button("保存到云端"):
        if new_name and new_recipe:
            # 往 Google 表格最后一行追加数据
            sheet.append_row([new_name, new_recipe])
            st.success("✅ 已存入 Google 表格！刷新也不会丢了。")
        else:
            st.error("请填完名称和配方哦！")

# --- 3. 展示区：从云端实时读取 ---
st.subheader("📖 实验室配方集")

# 获取所有数据（代码会自动把表格第一行作为“列名”）
data = sheet.get_all_records()

if not data:
    st.info("目前还没有配方，快去左边加一个吧！")
else:
    # 倒序显示，让最新的配方排在最上面
    for item in reversed(data):
        with st.expander(f"🍸 {item['名称']}"):
            st.write(f"**调制秘籍：**\n{item['配方']}")
