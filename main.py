import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import base64

# --- 1. 核心连接设置 ---
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    # 使用你已经测试成功的表格 ID
    SPREADSHEET_ID = "1eZuei2NyFVuKyZkooFPbc6X9J1waGoP4c2rnYcucZ4s"
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1 
except Exception as e:
    st.error(f"连接失败: {e}")
    st.stop()

# --- 2. 图片处理工具 ---
def img_to_base64(image_file):
    if image_file is not None:
        # 将本地上传的图片转为字符串存入表格
        return base64.b64encode(image_file.getvalue()).decode()
    return ""

# --- 3. 页面配置 ---
st.set_page_config(page_title="秋秋的饮品实验室", page_icon="🍹", layout="wide")
st.title("🍹 秋秋的云端饮品实验室")
st.markdown("欢迎来到你的私人配方库！在这里记录每一份灵感。")

# --- 4. 侧边栏：全功能录入 ---
with st.sidebar:
    st.header("📝 记录新配方")
    new_name = st.text_input("饮品名称", placeholder="例：厚乳拿铁")
    new_ingredients = st.text_area("准备材料", placeholder="例：咖啡粉 18g\n冰牛奶 200ml")
    new_steps = st.text_area("制作步骤", placeholder="例：1. 萃取咖啡\n2. 将牛奶打出奶泡...")
    
    # 本地图片上传
    uploaded_file = st.file_uploader("📸 上传饮品成品图", type=['png', 'jpg', 'jpeg'])
    
    if st.button("🚀 存入实验室仓库"):
        if new_name and new_ingredients and new_steps:
            with st.spinner('正在同步到云端...'):
                img_str = img_to_base64(uploaded_file)
                # 对应表格列：名称(A), 材料(B), 做法(C), 图片数据(D)
                sheet.append_row([new_name, new_ingredients, new_steps, img_str])
                st.success(f"✅ {new_name} 已保存！")
                st.rerun()
        else:
            st.error("名称、材料和步骤都要填哦！")

# --- 5. 主界面：搜索功能 ---
search_query = st.text_input("🔍 搜索我的配方库", placeholder="输入名字关键词搜搜看...")

# --- 6. 数据展示区 ---
st.markdown("---")
try:
    data = sheet.get_all_records()
    
    if not data:
        st.info("💡 实验室目前没有数据。快在左侧录入你的第一个配方吧！")
    else:
        # 搜索过滤
        if search_query:
            display_data = [item for item in data if search_query.lower() in str(item.get('名称', '')).lower()]
        else:
            display_data = data

        # 倒序显示，让最新的配方在最上面
        for item in reversed(display_data):
            with st.container():
                col1, col2 = st.columns([1, 2])
                
                # 左侧显示图片
                with col1:
                    img_base64 = item.get('图片数据')
                    if img_base64:
                        st.image(f"data:image/png;base64,{img_base64}", use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/300x300?text=No+Image", use_container_width=True)
                
                # 右侧显示文字详情
                with col2:
                    st.header(f"🍸 {item.get('名称', '未命名')}")
                    
                    tab1, tab2 = st.tabs(["🛒 准备材料", "👨‍🍳 制作步骤"])
                    with tab1:
                        st.info(item.get('材料', '暂无材料信息'))
                    with tab2:
                        st.success(item.get('做法', '暂无步骤信息'))
                
                st.markdown("---")

except Exception as e:
    st.warning("数据加载中...请先录入一个完整配方。")
