import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from module.db_manager import DBManager

def identify_market_cycles(df, threshold=20):
    """识别牛熊市周期
    threshold: 从高点下跌或从低点上涨超过该百分比则认为是新的周期
    """
    cycles = []
    current_cycle = {'type': None, 'start_date': None, 'end_date': None, 'start_price': None, 'end_price': None}
    high_price = low_price = df['close'].iloc[0]
    high_date = low_date = df.index[0]
    
    for date, row in df.iterrows():
        price = row['close']
        
        if current_cycle['type'] is None:
            # 初始化第一个周期
            current_cycle = {
                'type': 'bull' if price > df['close'].iloc[0] else 'bear',
                'start_date': df.index[0],
                'start_price': df['close'].iloc[0]
            }
        
        if current_cycle['type'] == 'bull':
            if price > high_price:
                high_price = price
                high_date = date
            elif price < high_price * (1 - threshold/100):
                # 确认熊市开始
                current_cycle['end_date'] = high_date
                current_cycle['end_price'] = high_price
                cycles.append(current_cycle)
                current_cycle = {
                    'type': 'bear',
                    'start_date': high_date,
                    'start_price': high_price
                }
                low_price = price
                low_date = date
        else:  # bear market
            if price < low_price:
                low_price = price
                low_date = date
            elif price > low_price * (1 + threshold/100):
                # 确认牛市开始
                current_cycle['end_date'] = low_date
                current_cycle['end_price'] = low_price
                cycles.append(current_cycle)
                current_cycle = {
                    'type': 'bull',
                    'start_date': low_date,
                    'start_price': low_price
                }
                high_price = price
                high_date = date
    
    # 添加最后一个未完成的周期
    if current_cycle['type'] == 'bull':
        current_cycle['end_date'] = high_date
        current_cycle['end_price'] = high_price
    else:
        current_cycle['end_date'] = low_date
        current_cycle['end_price'] = low_price
    cycles.append(current_cycle)
    
    return cycles

def plot_market_cycles(df, cycles):
    """绘制带有牛熊市标记的价格图"""
    fig = go.Figure()
    
    # 添加价格线
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['close'],
        mode='lines',
        name='价格',
        line=dict(color='white')
    ))
    
    # 添加牛熊市区域
    for cycle in cycles:
        color = 'rgba(255,0,0,0.2)' if cycle['type'] == 'bull' else 'rgba(0,255,0,0.2)'
        fig.add_vrect(
            x0=cycle['start_date'],
            x1=cycle['end_date'],
            fillcolor=color,
            opacity=0.5,
            layer="below",
            line_width=0,
        )
    
    # 更新布局
    fig.update_layout(
        title='纳斯达克100指数牛熊市周期',
        xaxis_title='日期',
        yaxis_title='价格',
        height=600,
        showlegend=True
    )
    
    return fig

def show_market_cycle():
    st.title('牛熊市周期分析')
    
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
        # 设置牛熊市判断阈值
        threshold = st.slider(
            "设置牛熊市判断阈值(%)",
            min_value=10,
            max_value=30,
            value=20,
            help="从高点下跌或从低点上涨超过该百分比则认为是新的周期"
        )
        
        # 识别牛熊市周期
        cycles = identify_market_cycles(df, threshold)
        
        # 绘制周期图
        fig = plot_market_cycles(df, cycles)
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示周期统计
        st.subheader("牛熊市周期统计")
        
        cycles_df = pd.DataFrame(cycles)
        cycles_df['持续天数'] = (cycles_df['end_date'] - cycles_df['start_date']).dt.days
        cycles_df['涨跌幅(%)'] = ((cycles_df['end_price'] - cycles_df['start_price']) / cycles_df['start_price'] * 100).round(2)
        
        # 分别统计牛熊市
        bull_cycles = cycles_df[cycles_df['type'] == 'bull']
        bear_cycles = cycles_df[cycles_df['type'] == 'bear']
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"""
            🐂 牛市统计：
            - 次数: {len(bull_cycles)}
            - 平均持续天数: {bull_cycles['持续天数'].mean():.0f}
            - 平均涨幅: {bull_cycles['涨跌幅(%)'].mean():.2f}%
            """)
        
        with col2:
            st.info(f"""
            🐻 熊市统计：
            - 次数: {len(bear_cycles)}
            - 平均持续天数: {bear_cycles['持续天数'].mean():.0f}
            - 平均跌幅: {bear_cycles['涨跌幅(%)'].mean():.2f}%
            """)
        
        # 显示详细周期数据
        st.subheader("周期详细数据")
        display_df = cycles_df.copy()
        display_df['start_date'] = display_df['start_date'].dt.strftime('%Y-%m-%d')
        display_df['end_date'] = display_df['end_date'].dt.strftime('%Y-%m-%d')
        display_df['type'] = display_df['type'].map({'bull': '牛市', 'bear': '熊市'})
        st.dataframe(display_df) 