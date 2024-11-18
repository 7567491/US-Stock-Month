import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf
import numpy as np
from module.db_manager import DBManager
from plotly.subplots import make_subplots
import pandas as pd

def plot_candlestick_with_pe(df):
    """绘制K线图和市盈率分析（双Y轴）"""
    # 创建带有双Y轴的图表
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 添加K线图（主Y轴）
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='K线'
        ),
        secondary_y=False
    )
    
    # 添加市盈率曲线（次Y轴）
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['pe_ratio'],
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='QQQ ETF市盈率',
            hovertemplate='PE=%{y:.2f}'
        ),
        secondary_y=True
    )
    
    # 添加市盈率参考线
    pe_references = {
        "极低": 15,
        "偏低": 20,
        "中位": 25,
        "偏高": 30,
        "极高": 35
    }
    
    colors = {
        "极低": "green",
        "偏低": "lightgreen",
        "中位": "yellow",
        "偏高": "orange",
        "极高": "red"
    }
    
    for level, pe in pe_references.items():
        fig.add_trace(
            go.Scatter(
                x=[df.index[0], df.index[-1]],
                y=[pe, pe],
                mode='lines',
                line=dict(color=colors[level], dash='dot', width=1),
                name=f'PE {level}: {pe}',
                hovertemplate=f'PE {level}=%{y:.2f}'
            ),
            secondary_y=True
        )
    
    # 更新布局
    fig.update_layout(
        title='纳斯达克100指数K线图与QQQ ETF市盈率分析',
        height=800,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        xaxis_title='日期'
    )
    
    # 更新Y轴标题
    fig.update_yaxes(title_text="价格", secondary_y=False)
    fig.update_yaxes(
        title_text="市盈率", 
        secondary_y=True,
        range=[10, 40]  # 设置市盈率Y轴范围
    )
    
    return fig

def show_candlestick():
    st.title('K线图分析')
    
    db_manager = DBManager()
    metadata = db_manager.get_metadata()
    
    if metadata["total_records"] == 0:
        st.warning("数据库中没有数据，请先在'下载数据'页面下载数据。")
        return
    
    st.info(f"""当前数据范围: {metadata["start_date"]} 至 {metadata["end_date"]}
    总记录数: {metadata["total_records"]}""")
    
    # 加载并显示K线图
    with st.spinner('正在加载数据...'):
        df = db_manager.load_data()
        
    if not df.empty:
        # 显示当前市盈率信息
        current_pe = df['pe_ratio'].iloc[-1]
        if not pd.isna(current_pe):
            # 计算市盈率百分位
            pe_range = (35 - 15)  # 最高PE - 最低PE
            pe_percentile = ((current_pe - 15) / pe_range) * 100
            pe_percentile = max(0, min(100, pe_percentile))  # 确保在0-100之间
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("当前QQQ ETF市盈率", f"{current_pe:.2f}")
            with col2:
                st.metric("历史百分位", f"{pe_percentile:.1f}%")
        
        # 绘制图表
        fig = plot_candlestick_with_pe(df)
        st.plotly_chart(fig, use_container_width=True)
        
        # 添加市盈率说明
        st.info("""
        📈 QQQ ETF市盈率(PE)解释：
        - PE < 20: 相对便宜
        - 20 ≤ PE ≤ 25: 正常估值
        - 25 < PE ≤ 30: 偏贵
        - PE > 30: 显著高估
        
        当前分析使用前向市盈率(Forward PE)，基于未来12个月预期收益计算。
        """)
    else:
        st.warning("数据库中没有数据")