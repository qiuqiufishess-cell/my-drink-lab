import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests
import json  # 必须有这一行，用来读 Secrets 里的那块大文字

# --- 1. 连接 Google 表格 (适配三引号写法) ---
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # 从 Secrets 获取那一整块文字
    creds_text = st.secrets["gcp_service_account"]
    # 将文字解析为钥匙字典
    creds_dict = json.loads(creds_text)
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    # 你的表格 ID
    SPREADSHEET_ID = "1eZuei2NyFVuKyZkooFPbc6X9J1waGoP4c2rnYcucZ4s"
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1 
except Exception as e:
    st.error(f"❌ 连接失败，请检查 Secrets 里的 JSON 格式: {e}")
    st.stop()

# --- 2. ImgBB 高清上传魔法 ---
def upload_to_imgbb(image_file):
    if image_file is None: return ""
    api_key = st.secrets["imgbb_api_key"]
    url = "https://api.imgbb.com/1/upload"
    payload = {"key": api_key}
    files = {"image": image_file.getvalue()}
    res = requests.post(url, payload, files=files)
    if res.status_code == 200:
        return res.json()["data"]["url"] # 拿到高清图网址
    return ""

# --- 3. 辅助函数：排版小圆点 ---
def display_as_list(text):
    if not text: return "暂无内容"
    lines = [line.strip() for line in str(text).split('\n') if line.strip()]
    return "<br>".join([f"· {line}" for line in lines])

# --- 4. 页面显示设置 ---
st.set_page_config(page_title="秋秋的实验室 V2.0", layout="wide")
st.title("🍹 秋秋的云端饮品实验室")

# --- 5. 侧边栏：录入配方 ---
with st.sidebar:
    st.header("📝 记录新灵感")
    new_name = st.text_input("饮品名称")
    new_ing = st.text_area("准备材料")
    new_steps = st.text_area("制作步骤")
    new_pic = st.file_uploader("📸 上传高清照片", type=['png', 'jpg', 'jpeg'])
    
    if st.button("🚀 存入实验室仓库"):
        if new_name and new_ing and new_steps:
            with st.spinner('图片正在高清同步...'):
                img_url = upload_to_imgbb(new_pic)
                # 写入表格：名称、材料、步骤、图片网址
                sheet.append_row([new_name, new_ing, new_steps, img_url])
                st.success("✅ 存好啦！")
                st.rerun()
        else:
            st.error("请填全信息哦！")

# --- 6. 主展示区：搜索、展示与删除 ---
search_query = st.text_input("🔍 搜索配方...", placeholder="输入名字搜搜看")
st.markdown("---")

try:
    all_data = sheet.get_all_values() 
    if len(all_data) > 1:
        data_rows = all_data[1:] # 只要数据，不要表头
        
        # 倒序显示，让最新的在最上面
        for i, row in enumerate(reversed(data_rows)):
            # 计算这一行在 Google 表格里的真实行号（从 2 开始算）
            actual_row_num = len(all_data) - i 
            
            if search_query.lower() in row[0].lower():
                with st.container():
                    col1, col2, col3 = st.columns([1, 1.5, 0.5])
                    with col1:
                        if row[3]: st.image(row[3], use_container_width=True)
                    with col2:
                        st.subheader(f"🍸 {row[0]}")
                        st.markdown(f"**🛒 材料：**<br>{display_as_list(row[1])}", unsafe_allow_html=True)
                        st.markdown(f"**👨‍🍳 步骤：**<br>{display_as_list(row[2])}", unsafe_allow_html=True)
                    with col3:
                        st.write("⚙️ 管理")
                        if st.button("🗑️ 删除", key=f"del_{actual_row_num}"):
                            sheet.delete_rows(actual_row_num)
                            st.toast("已删除！")
                            st.rerun()
                    st.markdown("---")
    else:
        st.info("实验室还没有配方，快去左边增加一个吧！")
except Exception:
    st.info("💡 实验室已就绪，由于格式升级，请录入新配方吧！")
