import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests # 新朋友：专门负责把图片“寄”给图床

# --- 1. 连接 Google 表格 (你的档案柜) ---
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    # 你的表格 ID 保持不变
    SPREADSHEET_ID = "1eZuei2NyFVuKyZkooFPbc6X9J1waGoP4c2rnYcucZ4s"
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1 
except Exception as e:
    st.error(f"连接失败: {e}")
    st.stop()

# --- 2. ImgBB 高清图床魔法 (最关键的改动) ---
def upload_to_imgbb(image_file):
    if image_file is None: return ""
    # 读取你刚才在 Secrets 里藏好的钥匙
    api_key = st.secrets["imgbb_api_key"]
    url = "https://api.imgbb.com/1/upload"
    # 把图片打包，准备寄送给 ImgBB 服务器
    payload = {"key": api_key}
    files = {"image": image_file.getvalue()}
    # 发出寄送请求
    res = requests.post(url, payload, files=files)
    if res.status_code == 200:
        # 寄送成功，拿到照片在云端的“门牌号”(网址)
        return res.json()["data"]["url"]
    return ""

# --- 3. 辅助功能：自动排版 ---
def display_as_list(text):
    if not text: return "暂无内容"
    # 把回车换成小圆点和强制换行
    lines = [line.strip() for line in str(text).split('\n') if line.strip()]
    return "<br>".join([f"· {line}" for line in lines])

# --- 4. 页面设置 ---
st.set_page_config(page_title="秋秋的实验室 V2.0", layout="wide")
st.title("🍹 秋秋的云端饮品实验室")

# --- 5. 侧边栏：记录新配方 ---
with st.sidebar:
    st.header("📝 记录新灵感")
    new_name = st.text_input("饮品名称", placeholder="例如：西西里咖啡")
    new_ing = st.text_area("准备材料", placeholder="每行一个材料")
    new_steps = st.text_area("制作步骤", placeholder="第一步、第二步...")
    new_pic = st.file_uploader("📸 上传高清原图", type=['png', 'jpg', 'jpeg'])
    
    if st.button("🚀 存入实验室仓库"):
        if new_name and new_ing and new_steps:
            with st.spinner('图片正在寄往云端仓库...'):
                # 步骤 A：把图传给 ImgBB
                img_url = upload_to_imgbb(new_pic)
                # 步骤 B：把名字、材料、步骤和【图片网址】存入表格
                sheet.append_row([new_name, new_ing, new_steps, img_url])
                st.success("✅ 存好啦！")
                st.rerun()
        else:
            st.warning("请填全名称、材料和步骤哦！")

# --- 6. 展示与管理区 ---
search_query = st.text_input("🔍 搜索配方...", placeholder="输入名称搜搜看")
st.markdown("---")

try:
    # 获取表格里所有内容
    all_data = sheet.get_all_values()
    if len(all_data) > 1:
        headers = all_data[0] # 第一行是表头
        rows = all_data[1:]    # 剩下的是配方
        
        # 倒序显示，让最新的在最上面
        for i, row in enumerate(reversed(rows)):
            # 算出它在原始表格里的“行号”，删除时要用
            actual_row_num = len(all_data) - i
            
            # 搜索过滤：只显示包含搜索词的
            if search_query.lower() in row[0].lower():
                with st.container():
                    # 分成三列：[图] | [文字详情] | [管理按钮]
                    col1, col2, col3 = st.columns([1, 1.8, 0.5])
                    
                    with col1:
                        # 如果有网址，直接显示，这次图片会非常高清！
                        if row[3]: st.image(row[3], use_container_width=True)
                    
                    with col2:
                        st.subheader(f"🍸 {row[0]}")
                        st.markdown(f"**🛒 材料：**<br>{display_as_list(row[1])}", unsafe_allow_html=True)
                        st.markdown(f"**👨‍🍳 步骤：**<br>{display_as_list(row[2])}", unsafe_allow_html=True)
                    
                    with col3:
                        st.write("⚙️ 操作")
                        # 删除按钮：点击后指令 Google 表格删掉对应行
                        if st.button("🗑️ 删除", key=f"del_{actual_row_num}"):
                            sheet.delete_rows(actual_row_num)
                            st.toast("已成功删除！")
                            st.rerun()
                    st.markdown("---")
    else:
        st.info("实验室还是空的呢，快在左边增加第一个配方吧！")
except Exception:
    st.info("💡 实验室已就绪，请录入高清配方。")
