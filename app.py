import streamlit as st
from module.data_downloader import show_downloader
from module.candlestick import show_candlestick
from module.monthly_analysis import show_monthly_analysis
from module.sharpe_ratio import show_sharpe_analysis
from module.november_analysis import show_november_analysis
from module.market_cycle import show_market_cycle

def main():
    st.sidebar.title('导航')
    
    # 自定义CSS样式
    st.markdown("""
        <style>
        .stButton > button {
            width: 100%;
            margin-bottom: 10px;
            border: 2px solid #ffd700;  /* 黄色边框 */
            background-color: transparent;  /* 透明背景 */
            color: white;  /* 白色文字 */
        }
        .stButton > button:hover {
            border: 2px solid #ffd700;
            background-color: transparent;
            color: #ffd700;  /* 悬停时文字变为黄色 */
        }
        div[data-testid="stHorizontalBlock"] button {
            border: 2px solid #ffd700;
            background-color: transparent;
            color: white;  /* 白色文字 */
        }
        div[data-testid="stHorizontalBlock"] button:hover {
            border: 2px solid #ffd700;
            background-color: transparent;
            color: #ffd700;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 使用session_state来记住当前页面
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '下载数据'
    
    # 创建按钮
    if st.sidebar.button('下载数据', key='btn_download'):
        st.session_state.current_page = '下载数据'
    
    if st.sidebar.button('K线图', key='btn_candlestick'):
        st.session_state.current_page = 'K线图'
    
    if st.sidebar.button('月度分析', key='btn_monthly'):
        st.session_state.current_page = '月度分析'
        
    if st.sidebar.button('月夏普比率', key='btn_sharpe'):
        st.session_state.current_page = '月夏普比率'
        
    if st.sidebar.button('11月分析', key='btn_november'):
        st.session_state.current_page = '11月分析'
        
    if st.sidebar.button('牛熊市分析', key='btn_market_cycle'):
        st.session_state.current_page = '牛熊市分析'
    
    # 页面映射
    pages = {
        '下载数据': show_downloader,
        'K线图': show_candlestick,
        '月度分析': show_monthly_analysis,
        '月夏普比率': show_sharpe_analysis,
        '11月分析': show_november_analysis,
        '牛熊市分析': show_market_cycle
    }
    
    # 显示当前选中的页面
    pages[st.session_state.current_page]()

if __name__ == '__main__':
    main() 