import streamlit as st
import pandas as pd
import datetime
import os

# 设置页面标题
st.set_page_config(page_title="专属学习打卡系统", page_icon="📚")
st.title("📚 每日学习打卡")

# 数据存储文件
DATA_FILE = "study_records.csv"

# 初始化或读取数据
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["日期", "科目", "学习时长(小时)", "学习内容备注"])

df = load_data()

# 侧边栏：打卡表单
st.sidebar.header("新增打卡记录")
with st.sidebar.form("check_in_form"):
    date = st.date_input("日期", datetime.date.today())
    
    # 预设了一些硬核学科作为选项
    subject = st.selectbox("学习科目", [
        "高等代数", 
        "多元微积分", 
        "理论物理", 
        "英语", 
        "其他"
    ])
    
    hours = st.number_input("学习时长 (小时)", min_value=0.5, max_value=16.0, step=0.5)
    notes = st.text_area("学习内容备注 (如：完成XX定理证明)")
    
    submitted = st.form_submit_button("提交打卡")
    
    if submitted:
        new_record = pd.DataFrame([{
            "日期": str(date), 
            "科目": subject, 
            "学习时长(小时)": hours, 
            "学习内容备注": notes
        }])
        df = pd.concat([df, new_record], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("✅ 打卡成功！")

# 主页面：数据展示与统计
st.subheader("历史打卡记录")
if not df.empty:
    st.dataframe(df, use_container_width=True)
    
    st.subheader("学习时长统计")
    # 按科目汇总学习时长
    summary = df.groupby("科目")["学习时长(小时)"].sum().reset_index()
    st.bar_chart(summary.set_index("科目"))
else:
    st.info("目前还没有打卡记录，去左侧边栏开始你的第一次打卡吧！")