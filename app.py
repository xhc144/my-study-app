import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="高级学习打卡系统", page_icon="🚀", layout="wide")
st.title("🚀 专属学习打卡与数据管理系统")

DATA_FILE = "study_records.csv"

# 初始化或读取数据
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame(columns=["日期", "科目", "学习时长(小时)", "学习内容备注"])
    else:
        return pd.DataFrame([
            {"日期": str(datetime.date.today() - datetime.timedelta(days=2)), "科目": "高等代数", "学习时长(小时)": 2.0, "学习内容备注": "第一章习题"},
            {"日期": str(datetime.date.today() - datetime.timedelta(days=1)), "科目": "多元微积分", "学习时长(小时)": 3.0, "学习内容备注": "看网课"},
            {"日期": str(datetime.date.today()), "科目": "理论物理", "学习时长(小时)": 1.5, "学习内容备注": "推导方程"}
        ], columns=["日期", "科目", "学习时长(小时)", "学习内容备注"])

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# 顶部打卡表单
st.subheader("📝 每日打卡")
with st.form("check_in_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("选择日期", datetime.date.today())
    with col2:
        subject = st.selectbox("学习科目", ["高等代数", "多元微积分", "理论物理", "英语", "其他"])
    with col3:
        hours = st.number_input("学习时长 (小时)", min_value=0.5, max_value=16.0, step=0.5, value=1.0)
    
    notes = st.text_area("学习内容备注 (可选)")
    submitted = st.form_submit_button("提交打卡")
    
    if submitted:
        new_record = pd.DataFrame([{"日期": str(date), "科目": subject, "学习时长(小时)": hours, "学习内容备注": notes}])
        st.session_state.df = pd.concat([st.session_state.df, new_record], ignore_index=True)
        st.session_state.df.to_csv(DATA_FILE, index=False)
        st.success("✅ 打卡成功！")

st.markdown("---")

# 中部：顺滑的折线图
st.subheader("📈 学习趋势折线图")
if not st.session_state.df.empty:
    # 按照日期排序
    df_sorted = st.session_state.df.sort_values("日期")
    
    # 渲染折线图 (如果被你鼠标滑乱了，双击图表即可恢复默认)
    st.line_chart(df_sorted, x="日期", y="学习时长(小时)", color="科目", use_container_width=True)
else:
    st.info("暂无数据，打卡后将生成折线图。")

st.markdown("---")

# 底部：数据管理
st.subheader("⚙️ 数据管理中心")
st.caption("💡 提示：双击单元格可修改。若要删除，勾选左侧复选框按 Delete 键。修改后务必点击下方保存按钮！")

edited_df = st.data_editor(
    st.session_state.df, 
    num_rows="dynamic", 
    use_container_width=True
)

if st.button("💾 保存所有修改（含删除）"):
    st.session_state.df = edited_df
    st.session_state.df.to_csv(DATA_FILE, index=False)
    st.success("🎉 数据已永久保存！")
    st.rerun()
