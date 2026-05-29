import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import plotly.express as px
import os
import json

st.set_page_config(page_title="终极学习打卡系统", page_icon="🎯", layout="wide")

# 初始化 Google Sheets 连接
conn = st.connection("gsheets", type=GSheetsConnection)

# ==================== 存储与读取配置 ====================
SUBJECTS_FILE = "subjects.txt"
COUNTDOWN_FILE = "countdown.json"

def load_subjects():
    if os.path.exists(SUBJECTS_FILE):
        with open(SUBJECTS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    else:
        default_subs = ["数学分析","高等代数", "群论","常微分方程", "理论物理"]
        with open(SUBJECTS_FILE, "w", encoding="utf-8") as f:
            for sub in default_subs:
                f.write(sub + "\n")
        return default_subs

def load_countdown():
    if os.path.exists(COUNTDOWN_FILE):
        with open(COUNTDOWN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # 默认设定目标和日期
        default_cd = {"event_name": "清华丘成桐数学领军计划考试", "target_date": "2026-10-18"}
        with open(COUNTDOWN_FILE, "w", encoding="utf-8") as f:
            json.dump(default_cd, f)
        return default_cd

def save_countdown(data):
    with open(COUNTDOWN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

if 'subjects' not in st.session_state:
    st.session_state.subjects = load_subjects()

# ==================== 云端数据加载 ====================
try:
    df = conn.read(ttl=0)
    df = df.dropna(how="all")
except Exception as e:
    df = pd.DataFrame(columns=["日期", "科目", "学习时长(小时)", "学习内容备注"])

# ==================== 区域零：顶部倒计时 ====================
cd_data = load_countdown()
target_date = datetime.datetime.strptime(cd_data["target_date"], "%Y-%m-%d").date()
today = datetime.date.today()
days_left = (target_date - today).days

# 倒计时显示
if days_left > 0:
    st.markdown(f"<h2 style='text-align: center;'>⏳ 距离 <b>{cd_data['event_name']}</b> 还有 <span style='color:#ff4b4b; font-size:1.5em;'>{days_left}</span> 天！</h2>", unsafe_allow_html=True)
elif days_left == 0:
    st.markdown(f"<h2 style='text-align: center; color:#00cc66;'>🚀 就是今天！<b>{cd_data['event_name']}</b>，全力以赴！</h2>", unsafe_allow_html=True)
else:
    st.markdown(f"<h2 style='text-align: center; color:#888888;'>🏁 <b>{cd_data['event_name']}</b> 已过去 {abs(days_left)} 天。</h2>", unsafe_allow_html=True)

# 倒计时设置折叠面板
with st.expander("⚙️ 设置倒计时目标"):
    c1, c2 = st.columns(2)
    with c1:
        new_event = st.text_input("目标名称", value=cd_data["event_name"])
    with c2:
        new_date = st.date_input("目标日期", value=target_date)
    if st.button("更新倒计时"):
        save_countdown({"event_name": new_event, "target_date": str(new_date)})
        st.success("目标已更新！")
        st.rerun()

st.markdown("---")

# ==================== 区域一：打卡与科目管理 ====================
st.subheader("📝 打卡中心与科目管理")
col_left, col_right = st.columns([2, 1])

with col_left:
    with st.form("check_in_form", clear_on_submit=True):
        st.markdown("**新建打卡记录**")
        c1, c2, c3 = st.columns(3)
        with c1:
            date = st.date_input("选择日期", datetime.date.today())
        with c2:
            subject = st.selectbox("学习科目", st.session_state.subjects)
        with c3:
            hours = st.number_input("学习时长 (小时)", min_value=0.5, max_value=16.0, step=0.5, value=1.0)
        
        notes = st.text_area("学习内容备注 (可选)")
        submitted = st.form_submit_button("提交打卡")
        
        if submitted:
            new_record = pd.DataFrame([{"日期": str(date), "科目": subject, "学习时长(小时)": hours, "学习内容备注": notes}])
            updated_df = pd.concat([df, new_record], ignore_index=True)
            conn.update(data=updated_df)
            st.success("✅ 打卡成功！数据已同步至云端。")
            st.rerun()

with col_right:
    st.markdown("**🏫 专属科目管理**")
    # 使用标签页区分新增和删除功能
    tab_add, tab_del = st.tabs(["➕ 新增科目", "🗑️ 删除科目"])
    
    with tab_add:
        new_sub_input = st.text_input("输入新科目名称：", placeholder="例如：政治、考研英语")
        if st.button("确认新增"):
            if new_sub_input.strip() and new_sub_input.strip() not in st.session_state.subjects:
                st.session_state.subjects.append(new_sub_input.strip())
                with open(SUBJECTS_FILE, "w", encoding="utf-8") as f:
                    for s in st.session_state.subjects: f.write(s + "\n")
                st.success(f"已添加：{new_sub_input.strip()}")
                st.rerun()
            elif new_sub_input.strip() in st.session_state.subjects:
                st.warning("该科目已存在！")
                
    with tab_del:
        sub_to_delete = st.selectbox("选择要删除的科目：", st.session_state.subjects)
        if st.button("确认删除", type="primary"):
            if len(st.session_state.subjects) > 1:
                st.session_state.subjects.remove(sub_to_delete)
                with open(SUBJECTS_FILE, "w", encoding="utf-8") as f:
                    for s in st.session_state.subjects: f.write(s + "\n")
                st.success(f"已删除：{sub_to_delete}")
                st.rerun()
            else:
                st.error("请至少保留一个科目，无法删除！")

st.markdown("---")

# ==================== 区域二：锁死的折线图 ====================
st.subheader("📈 学习趋势折线图")

if not df.empty and len(df) > 0:
    df_chart = df.groupby(["日期", "科目"])["学习时长(小时)"].sum().reset_index()
    df_chart = df_chart.sort_values("日期")
    
    fig = px.line(df_chart, x="日期", y="学习时长(小时)", color="科目", markers=True)
    fig.update_layout(
        xaxis=dict(tickangle=0, type='category', fixedrange=True),
        yaxis=dict(rangemode="tozero", fixedrange=True),
        dragmode=False,
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.info("暂无数据，打卡后将生成折线图。")

st.markdown("---")

# ==================== 区域三：数据管理 ====================
st.subheader("⚙️ 数据管理中心")
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if st.button("💾 保存所有修改（同步至云端）"):
    final_df = edited_df.dropna(how="all")
    conn.update(data=final_df)
    st.success("🎉 数据已成功同步更新！")
    st.rerun()
