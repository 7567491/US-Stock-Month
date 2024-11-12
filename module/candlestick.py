import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from module.db_manager import DBManager

def plot_candlestick(df):
    """绘制K线图"""
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])])
    
    fig.update_layout(
        title='纳斯达克100指数K线图',
        yaxis_title='价格',
        xaxis_title='日期',
        height=800  # 增加图表高度以获得更好的显示效果
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
    
    # 直接加载数据并显示K线图
    with st.spinner('正在加载数据...'):
        df = db_manager.load_data()
        
    if not df.empty:
        fig = plot_candlestick(df)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("数据库中没有数据")