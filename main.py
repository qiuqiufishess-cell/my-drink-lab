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

# --- 2. 图片压缩与转换魔法 ---
def process_image(image_file):
    if image_file is not None:
        # 打开图片
        img = Image.open(image_file)
        # 如果是 RGBA (带透明度)，转为 RGB 防止保存报错
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # 自动缩小图片尺寸（宽度设为 300 像素，等比例缩放）
        # 这样既能看清，又不会撑爆表格单元格
        max_width = 300
        w_percent = (max_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((max_width, h_size), Image.Resampling.LANCZOS)
        
        # 将压缩后的图片转为 Base64 字符串
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=70) # 压缩质量设为 70%
        return base64.b64encode(buffered.getvalue()).decode()
    return ""

# --- 3. 页面配置 ---
st.set_page_config(page_title="秋秋的饮品实验室", page_icon="🍹", layout="wide")
st.title("🍹 秋秋的云端饮品实验室")

# --- 4. 侧边栏：全功能录入 ---
with st.sidebar:
    st.header("📝 记录新配方")
    new_name = st.text_input("饮品名称", placeholder="例：生椰拿铁")
    new_ingredients = st.text_area("准备材料", placeholder="例：厚椰乳 200ml...")
    new_steps = st.text_area("制作步骤", placeholder="例：1. 满杯冰块...")
    uploaded_file = st.file_uploader("📸 上传照片 (会自动压缩)", type=['png', 'jpg', 'jpeg'])
    
    if st.button("🚀 存入实验室仓库"):
        if new_name and new_ingredients and new_steps:
            with st.spinner('正在处理并同步...'):
                try:
                    img_str = process_image(uploaded_file)
                    # 写入表格：名称、材料、做法、图片数据
                    sheet.append_row([new_name, new_ingredients, new_steps, img_str])
                    st.success(f"✅ {new_name} 已存入！")
                    st.rerun()
                except Exception as e:
                    st.error(f"保存失败，可能是图片太大了，请尝试换张小图。报错详情: {e}")
        else:
            st.error("请填全名称、材料和步骤！")

# --- 5. 搜索与展示 ---
search_query = st.text_input("🔍 搜索配方...", placeholder="输入关键词...")
st.markdown("---")

try:
    data = sheet.get_all_records()
    if data:
        if search_query:
            data = [item for item in data if search_query.lower() in str(item.get('名称','')).lower()]
        
        for item in reversed(data):
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    img_data = item.get('图片数据')
                    if img_data:
                        st.image(f"data:image/jpeg;base64,{img_data}", use_container_width=True)
                    else:
                        st.caption("📷 暂无照片")
                with col2:
                    st.header(f"🍸 {item.get('名称')}")
                    t1, t2 = st.tabs(["🛒 材料", "👨‍🍳 步骤"])
                    with t1: st.info(item.get('材料'))
                    with t2: st.success(item.get('做法'))
                st.markdown("---")
except Exception:
    st.info("💡 实验室就绪，快去录入吧！")
