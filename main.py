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
st.set_page_config(page_title="秋秋的实验室 V4.0", layout="wide")
st.title("🍹 秋秋的云端饮品实验室")

# --- 5. 侧边栏：权限控制与录入 ---
with st.sidebar:
    st.header("🔑 实验室门禁")
    # 设置你的暗号
    MY_PASSWORD = "qiuqiu123" 
    input_pwd = st.text_input("输入管理暗号以解锁编辑", type="password")
    # 判断是否为管理员
    is_admin = (input_pwd == MY_PASSWORD)

    if is_admin:
        st.success("👨‍🍳 欢迎回来，秋秋！")
        st.markdown("---")
        st.header("📝 记录新灵感")
        new_name = st.text_input("饮品名称", key="add_name")
        new_ing = st.text_area("准备材料", key="add_ing")
        new_steps = st.text_area("制作步骤", key="add_steps")
        new_pic = st.file_uploader("📸 上传照片", type=['png', 'jpg', 'jpeg'], key="add_pic")
        
        if st.button("🚀 存入实验室仓库"):
            if new_name and new_ing and new_steps:
                with st.spinner('同步中...'):
                    img_url = upload_to_imgbb(new_pic)
                    sheet.append_row([new_name, new_ing, new_steps, img_url])
                    st.success("✅ 已存入！")
                    st.rerun()
            else:
                st.error("请填全信息哦！")
    else:
        st.info("🔓 当前为【访客模式】\n\n输入暗号后可进行上传、修改和删除。")

# --- 6. 主展示区 ---
search_query = st.text_input("🔍 搜索配方...", placeholder="想喝点什么？")
st.markdown("---")

try:
    all_values = sheet.get_all_values()
    if len(all_values) > 1:
        data_rows = all_values[1:]
        
        for i, row in enumerate(reversed(data_rows)):
            actual_row_idx = len(all_values) - i 
            
            if search_query.lower() in row[0].lower():
                with st.container(border=True):
                    edit_key = f"is_editing_{actual_row_idx}"
                    if edit_key not in st.session_state:
                        st.session_state[edit_key] = False

                    # 分列展示：
                    # 如果是管理员，显示：[图] [文字] [操作]
                    # 如果是访客，显示：[图] [文字]
                    if is_admin:
                        col1, col2, col3 = st.columns([1, 1.5, 0.6])
                    else:
                        col1, col2 = st.columns([1, 2.1])
                    
                    with col1:
                        if row[3]: st.image(row[3], use_container_width=True)
                    
                    with col2:
                        if st.session_state[edit_key] and is_admin:
                            # 编辑模式下的输入框
                            e_name = st.text_input("修改名称", value=row[0], key=f"en_{actual_row_idx}")
                            e_ing = st.text_area("修改材料", value=row[1], key=f"ei_{actual_row_idx}")
                            e_steps = st.text_area("修改步骤", value=row[2], key=f"es_{actual_row_idx}")
                        else:
                            # 普通显示模式
                            st.subheader(f"🍸 {row[0]}")
                            st.markdown(f"**🛒 材料：**<br>{display_as_list(row[1])}", unsafe_allow_html=True)
                            st.markdown(f"**👨‍🍳 步骤：**<br>{display_as_list(row[2])}", unsafe_allow_html=True)
                    
                    # 只有管理员（输入了正确暗号）才能看到操作区
                    if is_admin:
                        with col3:
                            if not st.session_state[edit_key]:
                                if st.button("✏️ 修改", key=f"edit_btn_{actual_row_idx}"):
                                    st.session_state[edit_key] = True
                                    st.rerun()
                                
                                with st.popover("🗑️ 删除"):
                                    st.warning("永久删除？")
                                    if st.button("确认删除", key=f"del_btn_{actual_row_idx}"):
                                        sheet.delete_rows(actual_row_idx)
                                        st.rerun()
                            else:
                                if st.button("💾 保存", key=f"save_btn_{actual_row_idx}"):
                                    sheet.update(range_name=f"A{actual_row_idx}:C{actual_row_idx}", 
                                               values=[[e_name, e_ing, e_steps]])
                                    st.session_state[edit_key] = False
                                    st.success("已更新！")
                                    st.rerun()
                                
                                if st.button("❌ 取消", key=f"can_btn_{actual_row_idx}"):
                                    st.session_state[edit_key] = False
                                    st.rerun()
    else:
        st.info("库里还没配方。")
except Exception as e:
    st.error(f"加载出错: {e}")
