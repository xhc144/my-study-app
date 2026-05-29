import streamlit as st
import pandas as pd
import datetime
import os
import plotly.express as px

# 设置网页布局
st.set_page_config(page_title="硬核去Bug版学习打卡系统", page_icon="🎯", layout="wide")
st.title("🎯 专属学习打卡系统（硬核去Bug终极版）")

DATA_FILE = "study_records.csv"
SUBJECTS_FILE = "subjects.txt"

# 1. 初始化或读取科目列表
def load_subjects():
    if os.path.exists(SUBJECTS_FILE):
        with open(SUBJECTS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    else:
        # 默认初始科目
        default_subs = ["高等代数", "多元微积分", "理论物理", "英语", "其他"]
        with open(SUBJECTS_FILE, "w", encoding="utf-8") as f:
            for sub in default_subs:
                f.write(sub + "\n")
        return default_subs

# 2. 初始化或读取打卡数据
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame(columns=["日期", "科目", "学习时长(小时)", "学习内容备注"])
    else:
        return pd.DataFrame([
            {"日期": str(datetime.date.today() - datetime.timedelta(days=2)), "科目": "高等代数", "学习时长(小时)": 2.0, "学习内容备注": "初始数据"},
            {"日期": str(datetime.date.today() - datetime.timedelta(days=1)), "科目": "多元微积分", "学习时长(小时)": 3.0, "学习内容备注": "初始数据"},
            {"日期": str(datetime.date.today()), "科目": "理论物理", "学习时长(小时)": 1.5, "学习内容备注": "初始数据"}
        ], columns=["日期", "科目", "学习时长(小时)", "学习内容备注"])

# 加载数据到状态机
if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'subjects' not in st.session_state:
    st.session_state.subjects = load_subjects()

# ==================== 区域一：打卡与科目管理 ====================
st.subheader("📝 打卡中心与科目管理")
col_left, col_right = st.columns([2, 1])

with col_left:
    # 打卡表单
    with st.form("check_in_form", clear_on_submit=True):
        st.markdown("**新建打卡记录**")
        c1, c2, c3 = st.columns(3)
        with c1:
            date = st.date_input("选择日期", datetime.date.today())
        with c2:
            # 这里的选项是动态加载的
            subject = st.selectbox("学习科目", st.session_state.subjects)
        with c3:
            hours = st.number_input("学习时长 (小时)", min_value=0.5, max_value=16.0, step=0.5, value=1.0)
        
        notes = st.text_area("学习内容备注 (可选)")
        submitted = st.form_submit_button("提交打卡")
        
        if submitted:
            new_record = pd.DataFrame([{"日期": str(date), "科目": subject, "学习时长(小时)": hours, "学习内容备注": notes}])
            st.session_state.df = pd.concat([st.session_state.df, new_record], ignore_index=True)
            st.session_state.df.to_csv(DATA_FILE, index=False)
            st.success("✅ 打卡成功！")
            st.rerun()

with col_right:
    # 增加新建打卡项目（科目）的区域
    st.markdown("**🏫 科目管理**")
    new_sub_input = st.text_input("输入你想新建的打卡科目：", placeholder="例如：考研政治、日语")
    if st.button("➕ 确认新增该科目"):
        if new_sub_input.strip():
            if new_sub_input.strip() not in st.session_state.subjects:
                st.session_state.subjects.append(new_sub_input.strip())
                # 写入文件永久保存
                with open(SUBJECTS_FILE, "a", encoding="utf-8") as f:
                    f.write(new_sub_input.strip() + "\n")
                st.success(f"成功添加科目：{new_sub_input.strip()}！")
                st.rerun()
            else:
                st.warning("该科目已存在，换个名字吧。")
        else:
            st.error("请输入有效的科目名称。")

st.markdown("---")

# ==================== 区域二：强制锁死的线性折线图 ====================
st.subheader("📈 学习趋势折线图（已完全锁死坐标轴与字体）")

if not st.session_state.df.empty:
    # 按照日期和科目合并计算当天的总时长，防止同一个科目一天打卡多次在图表上画出乱线
    df_chart = st.session_state.df.groupby(["日期", "科目"])["学习时长(小时)"].sum().reset_index()
    df_chart = df_chart.sort_values("日期")
    
    # 使用 Plotly 创建精细控制的折线图
    fig = px.line(
        df_chart, 
        x="日期", 
        y="学习时长(小时)", 
        color="科目", 
        markers=True, # 强行在折线转折处点上小圆点，方便看数据
        title="每日各科目学习时间走势"
    )
    
    # 【核心去Bug命令】：强行修改图表底层属性
    fig.update_layout(
        xaxis=dict(
            tickangle=0,            # 🔍 绝招1：强制日期角度为0度（死都要横着放！）
            type='category',        # 🔍 绝招2：把日期当成分类标签，防止系统乱算时间轴间隔
            fixedrange=True         # 🔍 绝招3：彻底锁死X轴，禁止鼠标缩放、滚动、拖拽！
        ),
        yaxis=dict(
            rangemode="tozero",     # 🔍 绝招4：Y轴必须从0开始，绝对不允许变成负数！
            fixedrange=True         # 🔍 绝招5：彻底锁死Y轴，禁止鼠标缩放、滚动、拖拽！
        ),
        dragmode=False,             # 🔍 绝招6：关闭整张图表的拖拽模式
        hovermode="x unified"       # 鼠标放上去时，一条垂直线把当天所有科目的时间一起显示出来，最适合人类阅读
    )
    
    # 渲染图表，并且关掉右上角所有自带的烦人小工具栏（config里设置）
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.info("暂无数据，打卡后将生成折线图。")

st.markdown("---")

# ==================== 区域三：数据管理 ====================
st.subheader("⚙️ 数据管理中心")
st.caption("💡 提示：双击格子可改。勾选左侧行按 Delete 键可删。改后必须点下方按钮保存！")

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
