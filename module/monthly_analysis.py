import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from module.db_manager import DBManager

def calculate_monthly_returns(df):
    """计算月度收益率"""
    monthly_returns = df['close'].resample('M').last().pct_change() * 100
    return monthly_returns

def analyze_monthly_patterns(monthly_returns):
    """分析每个月的平均涨幅"""
    # 为每个收益率添加月份信息
    monthly_returns.index = pd.to_datetime(monthly_returns.index)
    monthly_data = pd.DataFrame({
        'month': monthly_returns.index.month,
        'returns': monthly_returns.values
    })
    
    # 计算每个月的平均收益率
    monthly_stats = monthly_data.groupby('month')['returns'].agg([
        ('平均收益率', 'mean'),
        ('最大涨幅', 'max'),
        ('最大跌幅', 'min'),
        ('标准差', 'std'),
        ('样本数', 'count')
    ]).round(2)
    
    # 添加月份名称
    month_names = ['一月', '二月', '三月', '四月', '五月', '六月',
                   '七月', '八月', '九月', '十月', '十一月', '十二月']
    monthly_stats.index = month_names
    
    return monthly_stats

def plot_monthly_patterns(monthly_stats):
    """绘制月度模式图表"""
    # 计算年化平均收益率
    annual_return = (1 + monthly_stats['平均收益率'].mean() / 100) ** 12 - 1
    annual_return_percentage = annual_return * 100
    
    # 计算月度平均收益率
    monthly_avg = monthly_stats['平均收益率'].mean()
    
    # 创建柱状图
    fig = go.Figure()
    
    # 添加柱状图
    fig.add_trace(go.Bar(
        x=monthly_stats.index,
        y=monthly_stats['平均收益率'],
        name='月度收益率',
        text=monthly_stats['平均收益率'].apply(lambda x: f'{x:.2f}%'),
        textposition='auto',
    ))
    
    # 添加月度平均线
    fig.add_trace(go.Scatter(
        x=monthly_stats.index,
        y=[monthly_avg] * len(monthly_stats),
        mode='lines',
        line=dict(dash='dash', color='yellow', width=2),
        name=f'月度平均: {monthly_avg:.2f}%'
    ))
    
    # 更新布局
    fig.update_layout(
        title=f'纳斯达克100指数月度平均收益率(%) (年化收益率: {annual_return_percentage:.2f}%)',
        xaxis_title='月份',
        yaxis_title='收益率(%)',
        height=600,
        showlegend=True,
        barmode='relative',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # 设置正负值的颜色
    fig.update_traces(
        marker_color=['red' if x > 0 else 'green' for x in monthly_stats['平均收益率']],
        selector=dict(type='bar')
    )
    
    return fig

def show_monthly_analysis():
    st.title('月度涨幅分析')
    
    db_manager = DBManager()
    metadata = db_manager.get_metadata()
    
    if metadata["total_records"] == 0:
        st.warning("数据库中没有数据，请先在'下载数据'页面下载数据。")
        return
    
    st.info(f"""当前数据范围: {metadata["start_date"]} 至 {metadata["end_date"]}
    总记录数: {metadata["total_records"]}""")
    
    # 直接加载并分析数据
    with st.spinner('正在分析数据...'):
        df = db_manager.load_data()
        
        if not df.empty:
            # 计算月度收益率
            monthly_returns = calculate_monthly_returns(df)
            
            # 分析月度模式
            monthly_stats = analyze_monthly_patterns(monthly_returns)
            
            # 显示月度统计图表
            fig = plot_monthly_patterns(monthly_stats)
            st.plotly_chart(fig, use_container_width=True)
            
            # 显示最佳和最差月份
            best_month = monthly_stats['平均收益率'].idxmax()
            worst_month = monthly_stats['平均收益率'].idxmin()
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"""最佳表现月份: {best_month}
                平均收益率: {monthly_stats.loc[best_month, '平均收益率']:.2f}%""")
            with col2:
                st.info(f"""最差表现月份: {worst_month}
                平均收益率: {monthly_stats.loc[worst_month, '平均收益率']:.2f}%""")
            
            # 显示详细统计数据
            st.subheader('月度详细统计')
            # 格式化百分比显示
            formatted_stats = monthly_stats.copy()
            for col in ['平均收益率', '最大涨幅', '最大跌幅', '标准差']:
                formatted_stats[col] = formatted_stats[col].apply(lambda x: f'{x:.2f}%')
            st.dataframe(formatted_stats)
            
        else:
            st.warning("数据库中没有数据")