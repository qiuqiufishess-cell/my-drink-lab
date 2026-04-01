import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- 1. 核心连接设置 ---
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    # 使用你确认成功的那个 ID
    SPREADSHEET_ID = "1eZuei2NyFVuKyZkooFPbc6X9J1waGoP4c2rnYcucZ4s"
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1 
except Exception as e:
    st.error(f"连接失败: {e}")
    st.stop()

# --- 2. 页面配置 ---
st.set_page_config(page_title="秋秋的饮品实验室", page_icon="🍹", layout="centered")
st.title("🍹 秋秋的云端饮品实验室")
st.markdown("---")

# --- 3. 侧边栏：录入功能 (增加图片链接输入) ---
with st.sidebar:
    st.header("📝 记录新配方")
    new_name = st.text_input("饮品名称", placeholder="例如：拿铁咖啡")
    new_recipe = st.text_area("调制公式", placeholder="例如：浓缩咖啡 + 牛奶")
    new_image = st.text_input("图片网址 (可选)", placeholder="https://...")
    
    if st.button("🚀 存入实验室"):
        if new_name and new_recipe:
            with st.spinner('正在同步到云端...'):
                # 按照表格顺序追加：名称、配方、图片链接
                sheet.append_row([new_name, new_recipe, new_image])
                st.success(f"✅ {new_name} 记录成功！")
                st.rerun()
        else:
            st.error("名称和配方是必填的哦！")

# --- 4. 主界面：搜索功能 ---
search_query = st.text_input("🔍 搜索我的配方库", placeholder="输入名字搜搜看...")

# --- 5. 展示区 ---
try:
    # 获取所有数据
    data = sheet.get_all_records()
    
    if not data:
        st.info("💡 实验室目前是空的。由于更换了数据库，请重新录入你的‘拿铁咖啡’吧！")
    else:
        # 如果有搜索词，就过滤数据
        if search_query:
            display_data = [item for item in data if search_query.lower() in item.get('名称', '').lower()]
        else:
            display_data = data

        # 倒序显示，最新的在最上面
        for item in reversed(display_data):
            with st.expander(f"🍸 {item.get('名称', '未命名')}", expanded=True):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # 显示图片，如果没有图片就显示占位图
                    img_url = item.get('图片链接') or item.get('图片')
                    if img_url and img_url.startswith("http"):
                        st.image(img_url, use_container_width=True)
                    else:
                        st.caption("📷 暂无预览图")
                
                with col2:
                    st.write("**调制配方：**")
                    st.info(item.get('配方', '暂无内容'))
                
except Exception as e:
    st.warning("正在等待数据同步...录入一个新配方即可激活界面！")
