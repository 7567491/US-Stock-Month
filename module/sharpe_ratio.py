import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from module.db_manager import DBManager

def calculate_monthly_sharpe(df):
    """计算月度夏普比率"""
    # 计算月度收益率
    monthly_returns = df['close'].resample('M').last().pct_change() * 100
    
    # 计算年化收益率和标准差
    annual_return = monthly_returns.mean() * 12
    annual_std = monthly_returns.std() * (12 ** 0.5)
    
    # 假设无风险利率为2%
    risk_free_rate = 2.0
    
    # 计算夏普比率
    sharpe_ratio = (annual_return - risk_free_rate) / annual_std
    
    return monthly_returns, sharpe_ratio, annual_return, annual_std

def plot_rolling_sharpe(monthly_returns, window=12):
    """绘制滚动夏普比率"""
    # 计算滚动夏普比率
    rolling_return = monthly_returns.rolling(window).mean() * 12
    rolling_std = monthly_returns.rolling(window).std() * (12 ** 0.5)
    risk_free_rate = 2.0
    rolling_sharpe = (rolling_return - risk_free_rate) / rolling_std
    
    # 创建图表
    fig = go.Figure()
    
    # 添加滚动夏普比率线
    fig.add_trace(go.Scatter(
        x=rolling_sharpe.index,
        y=rolling_sharpe.values,
        mode='lines',
        name='滚动夏普比率'
    ))
    
    # 添加零线
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    
    # 更新布局
    fig.update_layout(
        title=f'{window}个月滚动夏普比率',
        xaxis_title='日期',
        yaxis_title='夏普比率',
        height=500,
        showlegend=True
    )
    
    return fig

def show_sharpe_analysis():
    st.title('月夏普比率分析')
    
    db_manager = DBManager()
    metadata = db_manager.get_metadata()
    
    if metadata["total_records"] == 0:
        st.warning("数据库中没有数据，请先在'下载数据'页面下载数据。")
        return
    
    st.info(f"""当前数据范围: {metadata["start_date"]} 至 {metadata["end_date"]}
    总记录数: {metadata["total_records"]}""")
    
    # 加载数据
    df = db_manager.load_data()
    
    if not df.empty:
        # 计算夏普比率
        monthly_returns, sharpe_ratio, annual_return, annual_std = calculate_monthly_sharpe(df)
        
        # 显示总体统计
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总体夏普比率", f"{sharpe_ratio:.2f}")
        with col2:
            st.metric("年化收益率", f"{annual_return:.2f}%")
        with col3:
            st.metric("年化波动率", f"{annual_std:.2f}%")
        
        # 绘制滚动夏普比率图
        st.subheader("滚动夏普比率分析")
        window = st.slider("选择滚动窗口(月)", min_value=6, max_value=36, value=12, step=6)
        fig = plot_rolling_sharpe(monthly_returns, window)
        st.plotly_chart(fig, use_container_width=True)
        
        # 解释说明
        st.info("""
        📊 夏普比率解释：
        - 夏普比率 > 1: 优秀的风险调整后收益
        - 夏普比率 0-1: 可接受的风险调整后收益
        - 夏普比率 < 0: 风险调整后收益不及无风险利率
        
        当前分析使用2%作为无风险利率基准。
        """) 