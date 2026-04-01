import streamlit as st
import pandas as pd

# --- 1. 设置页面与安全口令 ---
st.set_page_config(page_title="秋秋的饮品实验室", page_icon="🧪")

def check_password():
    """验证身份，防止路人误入"""
    if "auth" not in st.session_state:
        st.session_state.auth = False
    
    if not st.session_state.auth:
        col1, col2 = st.columns([2,1])
        with col1:
            pwd = st.text_input("🔑 输入实验室进入口令：", type="password")
        if pwd == "666888":  # 这里设置你的专属暗号
            st.session_state.auth = True
            st.rerun()
        elif pwd:
            st.error("口令不对哦，再想想？")
        st.stop()

check_password()

# --- 2. 初始化云端数据 (暂用 Session，下一步教你连数据库) ---
# 注意：在没有连真正的外部数据库前，云端重启仍会重置。
# 但你可以先通过这个版本完成“跨网络访问”的测试。
if "my_recipes" not in st.session_state:
    st.session_state.my_recipes = {
        "生椰拿铁": {
            "image": "https://images.unsplash.com/photo-1559496417-e7f25cb247f3",
            "ingredients": ["冰块满杯", "厚椰乳 180ml", "牛奶 120ml","咖啡液 30ml"],
            "steps": "先加冰，再倒椰乳，最后淋咖啡。"
        }
    }

# --- 3. 界面逻辑 ---
st.title("🍹 秋秋的饮品实验室")

with st.sidebar:
    st.header("➕ 录入新配方")
    with st.form("add_form", clear_on_submit=True):
        n = st.text_input("名称")
        img = st.file_uploader("上传照片", type=['jpg','png'])
        ing = st.text_area("材料")
        step = st.text_area("步骤")
        if st.form_submit_button("同步到云端"):
            if n:
                st.session_state.my_recipes[n] = {
                    "image": img if img else "https://via.placeholder.com/400",
                    "ingredients": ing.split("\n"),
                    "steps": step
                }
                st.success("同步成功！")

# 选择显示
choice = st.selectbox("查看配方：", list(st.session_state.my_recipes.keys()))
data = st.session_state.my_recipes[choice]

col1, col2 = st.columns(2)
with col1:
    st.image(data["image"])
with col2:
    st.subheader("材料")
    for i in data["ingredients"]: st.write(f"- {i}")
st.info(data["steps"])
