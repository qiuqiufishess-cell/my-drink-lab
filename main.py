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

# --- 2. 图片压缩工具 ---
def process_image(image_file):
    if image_file is not None:
        img = Image.open(image_file)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        max_width = 400
        w_percent = (max_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((max_width, h_size), Image.Resampling.LANCZOS)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=75)
        return base64.b64encode(buffered.getvalue()).decode()
    return ""

# --- 3. 自动分行并加点的魔法函数 ---
def display_as_list(text):
    if not text:
        return "暂无内容"
    # 将文本按行拆分，并过滤掉空行
    lines = [line.strip() for line in str(text).split('\n') if line.strip()]
    # 在每行前面加上 · 
    return "\n".join([f"· {line}" for line in lines])

# --- 4. 页面配置 ---
st.set_page_config(page_title="秋秋的饮品实验室", page_icon="🍹", layout="wide")
st.title("🍹 秋秋的云端饮品实验室")

# --- 5. 侧边栏：录入 ---
with st.sidebar:
    st.header("📝 记录新配方")
    new_name = st.text_input("饮品名称")
    new_ingredients = st.text_area("准备材料 (每行一个)", placeholder="例：浓缩咖啡\n冰牛奶")
    new_steps = st.text_area("制作步骤 (每行一个)", placeholder="例：杯中加冰\n倒入牛奶")
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

# --- 6. 搜索框 ---
search_query = st.text_input("🔍 搜索配方库...", placeholder="输入饮品名字")
st.markdown("---")

# --- 7. 展示区：自动分行排版 ---
try:
    data = sheet.get_all_records()
    if data:
        if search_query:
            data = [item for item in data if search_query.lower() in str(item.get('名称','')).lower()]
        
        for item in reversed(data):
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
                    
                    # 关键修改：调用 display_as_list 函数来格式化显示
                    st.subheader("🛒 准备材料")
                    st.markdown(display_as_list(item.get('材料')))
                    
                    st.subheader("👨‍🍳 制作步骤")
                    st.markdown(display_as_list(item.get('做法')))
                
                st.markdown("---")
except Exception:
    st.info("💡 实验室已就绪，快去录入吧！")
