import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests
import json 

# --- 1. 连接 Google 表格 ---
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_text = st.secrets["gcp_service_account"]
    creds_dict = json.loads(creds_text)
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    SPREADSHEET_ID = "1eZuei2NyFVuKyZkooFPbc6X9J1waGoP4c2rnYcucZ4s"
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1 
except Exception as e:
    st.error(f"❌ 连接失败: {e}")
    st.stop()

# --- 2. ImgBB 高清上传 ---
def upload_to_imgbb(image_file):
    if image_file is None: return ""
    api_key = st.secrets["imgbb_api_key"]
    url = "https://api.imgbb.com/1/upload"
    payload = {"key": api_key}
    files = {"image": image_file.getvalue()}
    res = requests.post(url, payload, files=files)
    if res.status_code == 200:
        return res.json()["data"]["url"]
    return ""

# --- 3. 辅助函数 ---
def display_as_list(text):
    if not text: return "暂无内容"
    lines = [line.strip() for line in str(text).split('\n') if line.strip()]
    return "<br>".join([f"· {line}" for line in lines])

# --- 4. 页面设置 ---
st.set_page_config(page_title="秋秋的实验室 V2.1", layout="wide")
st.title("🍹 秋秋的云端饮品实验室")

# --- 5. 侧边栏：录入 ---
with st.sidebar:
    st.header("📝 记录新灵感")
    new_name = st.text_input("饮品名称")
    new_ing = st.text_area("准备材料")
    new_steps = st.text_area("制作步骤")
    new_pic = st.file_uploader("📸 上传高清照片", type=['png', 'jpg', 'jpeg'])
    
    if st.button("🚀 存入实验室仓库"):
        if new_name and new_ing and new_steps:
            with st.spinner('正在上传高清原图...'):
                img_url = upload_to_imgbb(new_pic)
                sheet.append_row([new_name, new_ing, new_steps, img_url])
                st.success("✅ 已同步到云端！")
                st.rerun()
        else:
            st.error("请填全信息哦！")

# --- 6. 主展示区 ---
search_query = st.text_input("🔍 搜索配方...", placeholder="输入想喝的饮品名字")
st.markdown("---")

try:
    all_data = sheet.get_all_values() 
    if len(all_data) > 1:
        data_rows = all_data[1:] 
        
        for i, row in enumerate(reversed(data_rows)):
            actual_row_num = len(all_data) - i 
            
            if search_query.lower() in row[0].lower():
                with st.container():
                    col1, col2, col3 = st.columns([1, 1.5, 0.6]) # 稍微调宽了操作列
                    
                    with col1:
                        if row[3]: st.image(row[3], use_container_width=True)
                    
                    with col2:
                        st.subheader(f"🍸 {row[0]}")
                        st.markdown(f"**🛒 材料：**<br>{display_as_list(row[1])}", unsafe_allow_html=True)
                        st.markdown(f"**👨‍🍳 步骤：**<br>{display_as_list(row[2])}", unsafe_allow_html=True)
                    
                    with col3:
                        st.write("⚙️ **管理配方**")
                        # --- 核心改进：防误触删除功能 ---
                        with st.popover("🗑️ 删除配方"):
                            st.warning("确定要永久删除吗？")
                            if st.button("🔴 我确定，执行删除", key=f"confirm_del_{actual_row_num}"):
                                with st.spinner('正在清理数据...'):
                                    sheet.delete_rows(actual_row_num)
                                    st.toast(f"已成功删除 {row[0]}")
                                    st.rerun()
                    st.markdown("---")
    else:
        st.info("实验室还没有配方。")
except Exception:
    st.info("💡 实验室已就绪。")
