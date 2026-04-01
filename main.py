import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- 1. 连接设置 ---
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

# 尝试连接
try:
    client = get_gspread_client()
    # 【核心修改点】使用 ID 打开表格，百分之百精准
    # 请将下面括号里的内容替换为你刚刚复制的那一长串 ID
    sheet = client.open_by_key("1eZuei2NyFVuKyZkooFPbc6X9J1waGoP4c2rnYcucZ4s").sheet1 
except Exception as e:
    st.error(f"连接失败！请确认 ID 是否正确。详情: {e}")
    st.stop()

# --- 2. 界面设计 ---
st.set_page_config(page_title="秋秋的饮品实验室", page_icon="🍹")
st.title("🍹 秋秋的饮品实验室")

with st.sidebar:
    st.header("📝 记录新配方")
    name = st.text_input("饮品名称")
    recipe = st.text_area("调制公式")
    
    if st.button("保存到云端"):
        if name and recipe:
            with st.spinner('同步中...'):
                sheet.append_row([name, recipe])
                st.success("✅ 存好啦！")
                st.rerun()
        else:
            st.error("名字和配方都要填哦！")

# --- 3. 展示区 ---
st.subheader("📖 实验室配方清单")
try:
    data = sheet.get_all_records()
    if not data:
        st.info("💡 实验室准备就绪！请在左侧添加第一个配方。")
    else:
        for item in reversed(data):
            n = item.get('名称', '未知饮品')
            r = item.get('配方', '暂无内容')
            with st.expander(f"🍸 {n}"):
                st.write(f"**调制秘籍：**\n{r}")
except Exception:
    st.info("💡 实验室连接成功！快去录入第一个配方吧。")
