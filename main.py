import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import base64
from PIL import Image
import io

# --- 1. 连接设置 ---
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    SPREADSHEET_ID = "1eZuei2NyFVuKyZkooFPbc6X9J1waGoP4c2rnYcucZ4s"
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1 
except Exception as e:
    st.error(f"连接失败: {e}")
    st.stop()

# --- 2. 图片压缩工具 (核心：防止报错) ---
def process_image(image_file):
    if image_file is not None:
        img = Image.open(image_file)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        # 缩小尺寸
        max_width = 400 
        w_percent = (max_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((max_width, h_size), Image.Resampling.LANCZOS)
        # 压缩质量
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=75)
        return base64.b64encode(buffered.getvalue()).decode()
    return ""

# --- 3. 页面配置 ---
st.set_page_config(page_title="秋秋的饮品实验室", page_icon="🍹", layout="wide")
st.title("🍹 秋秋的云端饮品实验室")

# --- 4. 侧边栏：录入 ---
with st.sidebar:
    st.header("📝 记录新配方")
    new_name = st.text_input("饮品名称")
    new_ingredients = st.text_area("准备材料 (每行一个)")
    new_steps = st.text_area("制作步骤")
    uploaded_file = st.file_uploader("📸 上传饮品照片", type=['png', 'jpg', 'jpeg'])
    
    if st.button("🚀 存入实验室"):
        if new_name and new_ingredients and new_steps:
            with st.spinner('同步中...'):
                img_str = process_image(uploaded_file)
                sheet.append_row([new_name, new_ingredients, new_steps, img_str])
                st.success(f"✅ {new_name} 已存好！")
                st.rerun()
        else:
            st.error("信息填全才能保存哦！")

# --- 5. 搜索框 ---
search_query = st.text_input("🔍 搜索配方库...", placeholder="输入饮品名字")
st.markdown("---")

# --- 6. 展示区：回归直观排版 ---
try:
    data = sheet.get_all_records()
    if data:
        if search_query:
            data = [item for item in data if search_query.lower() in str(item.get('名称','')).lower()]
        
        for item in reversed(data):
            # 使用容器包装每一条数据
            with st.container():
                col1, col2 = st.columns([1, 1.5])
                
                with col1:
                    img_data = item.get('图片数据')
                    if img_data:
                        st.image(f"data:image/jpeg;base64,{img_data}", use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/400x300?text=No+Photo", use_container_width=True)
                
                with col2:
                    st.header(f"🍸 {item.get('名称')}")
                    # 直接显示材料
                    st.subheader("🛒 准备材料")
                    st.write(item.get('材料'))
                    # 直接显示步骤
                    st.subheader("👨‍🍳 制作步骤")
                    st.write(item.get('做法'))
                
                st.markdown("---") # 分割线
except Exception:
    st.info("💡 实验室已就绪，快去录入吧！")
