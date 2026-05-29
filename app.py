import streamlit as st
import pandas as pd
import datetime
import os

# 设置页面配置（宽屏模式更适合看图表和表格）
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
        # 默认提供一些初始数据，防止第一次打开太空荡
        return pd.DataFrame([
            {"日期": str(datetime.date.today() - datetime.timedelta(days=2)), "科目": "高等代数", "学习时长(小时)": 2.0, "学习内容备注": "完成第一章线性空间习题"},
            {"日期": str(datetime.date.today() - datetime.timedelta(days=2)), "科目": "英语", "学习时长(小时)": 1.0, "学习内容备注": "背单词"},
            {"日期": str(datetime.date.today() - datetime.timedelta(days=1)), "科目": "多元微积分", "学习时长(小时)": 3.0, "学习内容备注": "看偏导数网课"},
            {"日期": str(datetime.date.today() - datetime.timedelta(days=1)), "科目": "理论物理", "学习时长(小时)": 2.5, "学习内容备注": "推导拉格朗日方程"},
            {"日期": str(datetime.date.today()), "科目": "高等代数", "学习时长(小时)": 1.5, "学习内容备注": "矩阵特征值复习"}
        ], columns=["日期", "科目", "学习时长(小时)", "学习内容备注"])

# 确保数据加载到会话状态中
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# 界面上半部分：打卡与图表
st.subheader("📝 每日打卡与趋势分析")
with st.form("check_in_form", clear_on_submit=True):
    date = st.date_input("选择日期", datetime.date.today())
    subject = st.selectbox("学习科目", ["高等代数", "多元微积分", "理论物理", "英语", "其他"])
    hours = st.number_input("学习时长 (小时)", min_value=0.5, max_value=16.0, step=0.5, value=1.0)
    notes = st.text_area("学习内容备注 (可选)")
    submitted = st.form_submit_button("提交打卡")
    
    if submitted:
        new_record = pd.DataFrame([{"日期": str(date), "科目": subject, "学习时长(小时)": hours, "学习内容备注": notes}])
        st.session_state.df = pd.concat([st.session_state.df, new_record], ignore_index=True)
        st.session_state.df.to_csv(DATA_FILE, index=False)
        st.success("✅ 打卡成功！图表和下方管理中心已同步更新。")

# 优化的按日期堆叠图表展示
if not st.session_state.df.empty:
    # 按日期排序，确保图表时间轴顺序正确
    df_sorted = st.session_state.df.sort_values("日期")
    # 高级堆叠柱状图：横轴为日期，纵轴为时长，用科目颜色堆叠区分
    st.bar_chart(df_sorted, x="日期", y="学习时长(小时)", color="科目", use_container_width=True)
else:
    st.info("暂无数据，图表将在打卡后生成。")

st.markdown("---")

# 界面下半部分：强大的数据管理（删除与修改）
st.subheader("⚙️ 数据管理中心（支持直接修改和删除）")
st.caption("💡 提示：你可以直接双击表格格子修改内容。若要删除，请勾选行左侧的复选框并按键盘的 Delete 键，或直接在表格内操作。修改后切记点击下方按钮保存！")

# 使用新型 data_editor 组件，开启动态行列操作
edited_df = st.data_editor(
    st.session_state.df, 
    num_rows="dynamic", 
    use_container_width=True
)

# 保存修改的触发按钮
if st.button("💾 保存所有修改（含删除）"):
    st.session_state.df = edited_df
    st.session_state.df.to_csv(DATA_FILE, index=False)
    st.success("🎉 数据已成功同步并永久保存！")
    st.rerun()
