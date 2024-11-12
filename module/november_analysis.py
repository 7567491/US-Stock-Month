import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from module.db_manager import DBManager

def analyze_november(df):
    """分析历年11月表现"""
    # 获取所有11月的数据
    november_data = df[df.index.month == 11]
    
    # 按年份计算11月收益率
    yearly_nov_returns = []
    years = november_data.index.year.unique()
    
    for year in years:
        nov_data = november_data[november_data.index.year == year]
        if not nov_data.empty:
            start_price = nov_data['close'].iloc[0]
            end_price = nov_data['close'].iloc[-1]
            return_pct = (end_price - start_price) / start_price * 100
            yearly_nov_returns.append({
                '年份': year,
                '收益率': return_pct,
                '开盘价': nov_data['open'].iloc[0],
                '收盘价': nov_data['close'].iloc[-1],
                '最高价': nov_data['high'].max(),
                '最低价': nov_data['low'].min(),
            })
    
    return pd.DataFrame(yearly_nov_returns)

def plot_november_returns(nov_returns):
    """绘制11月收益率柱状图"""
    fig = go.Figure()
    
    # 添加柱状图
    fig.add_trace(go.Bar(
        x=nov_returns['年份'],
        y=nov_returns['收益率'],
        text=nov_returns['收益率'].apply(lambda x: f'{x:.2f}%'),
        textposition='auto',
    ))
    
    # 添加平均线
    avg_return = nov_returns['收益率'].mean()
    fig.add_hline(
        y=avg_return,
        line_dash="dash",
        line_color="yellow",
        annotation_text=f"平均收益率: {avg_return:.2f}%"
    )
    
    # 更新布局
    fig.update_layout(
        title='历年11月收益率分析',
        xaxis_title='年份',
        yaxis_title='收益率(%)',
        height=500,
        showlegend=False
    )
    
    # 设置正负值的颜色
    fig.update_traces(
        marker_color=['red' if x > 0 else 'green' for x in nov_returns['收益率']]
    )
    
    return fig

def show_november_analysis():
    st.title('11月行情分析')
    
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
        # 分析11月数据
        nov_returns = analyze_november(df)
        
        # 显示统计信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("平均收益率", f"{nov_returns['收益率'].mean():.2f}%")
        with col2:
            st.metric("最佳表现", f"{nov_returns['收益率'].max():.2f}%")
        with col3:
            st.metric("最差表现", f"{nov_returns['收益率'].min():.2f}%")
        
        # 显示历年11月收益率图表
        fig = plot_november_returns(nov_returns)
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示详细数据表格
        st.subheader("历年11月详细数据")
        formatted_data = nov_returns.copy()
        formatted_data['收益率'] = formatted_data['收益率'].apply(lambda x: f'{x:.2f}%')
        st.dataframe(formatted_data)
        
        # 胜率统计
        win_rate = (nov_returns['收益率'] > 0).mean() * 100
        st.info(f"""
        📊 11月行情统计：
        - 上涨概率: {win_rate:.1f}%
        - 分析年数: {len(nov_returns)} 年
        """) 