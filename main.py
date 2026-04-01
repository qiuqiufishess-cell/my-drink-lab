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

# 尝试初始化连接
try:
    client = get_gspread_client()
    # 确保这里的名字和你的表格文件名完全一致
    sheet = client.open("My_Drink_Lab_Data").sheet1 
except Exception as e:
    st.error(f"连接 Google 服务器成功，但无法打开表格。请确认表格名无误。详情: {e}")
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
            with st.spinner('正在同步到云端...'):
                # 往表格追加一行
                sheet.append_row([name, recipe])
                st.success("✅ 存好啦！")
                st.rerun()
        else:
            st.error("名字和配方都要填哦！")

# --- 3. 展示区 (增加空表格容错) ---
st.subheader("📖 实验室配方清单")

try:
    # 获取数据
    data = sheet.get_all_records()
    
    if not data:
        st.info("💡 实验室空荡荡的，快在左侧录入你的第一个配方吧！")
    else:
        for item in reversed(data):
            # 使用 .get() 防止列名对不上的报错
            n = item.get('名称', '未知饮品')
            r = item.get('配方', '暂无配方')
            with st.expander(f"🍸 {n}"):
                st.write(f"**调制秘籍：**\n{r}")
except Exception:
    # 如果表格完全没有数据（gspread 报错），也显示提示
    st.info("💡 实验室已就绪，等待第一个配方入库！")
