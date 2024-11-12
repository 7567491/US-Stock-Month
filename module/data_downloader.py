import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from module.db_manager import DBManager

def load_nasdaq_data(start_date, end_date):
    """下载纳斯达克100指数数据"""
    try:
        ndx = yf.Ticker("^NDX")
        df = ndx.history(start=start_date, end=end_date)
        return df
    except Exception as e:
        st.error(f"下载数据时出错: {str(e)}")
        return None

def analyze_yearly_data(df):
    """分析每年的数据完整性"""
    if df is None or df.empty:
        return pd.DataFrame()
    
    yearly_stats = []
    years = df.index.year.unique()
    
    for year in years:
        year_data = df[df.index.year == year]
        
        if year == datetime.now().year:
            total_business_days = pd.date_range(
                start=f"{year}-01-01",
                end=datetime.now().date(),
                freq='B'
            ).size
        else:
            total_business_days = pd.date_range(
                start=f"{year}-01-01",
                end=f"{year}-12-31",
                freq='B'
            ).size
        
        actual_days = len(year_data)
        missing_days = total_business_days - actual_days
        completeness = (actual_days / total_business_days) * 100
        
        yearly_stats.append({
            '年份': year,
            '应有交易日': total_business_days,
            '实际数据天数': actual_days,
            '缺失天数': missing_days,
            '完整性': f"{completeness:.2f}%"
        })
    
    return pd.DataFrame(yearly_stats)

def verify_data(df):
    """验证数据完整性"""
    if df is None or df.empty:
        return False, "没有获取到数据", None
    
    missing_values = df.isnull().sum()
    has_null = missing_values.sum() > 0
    
    yearly_stats = analyze_yearly_data(df)
    
    is_valid = not has_null and yearly_stats['完整性'].str.rstrip('%').astype(float).mean() > 95
    
    message = "数据完整性验证完成"
    
    return is_valid, message, yearly_stats

def show_downloader():
    st.title('数据下载')
    
    db_manager = DBManager()
    metadata = db_manager.get_metadata()
    
    if metadata["total_records"] > 0:
        st.info(f"""现有数据信息:
        - 数据范围: {metadata["start_date"]} 至 {metadata["end_date"]}
        - 总记录数: {metadata["total_records"]}
        - 最后更新: {metadata["last_updated"]}
        """)
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            '开始日期:',
            datetime(2010, 1, 1)
        )
    with col2:
        end_date = st.date_input(
            '结束日期:',
            datetime.now()
        )
    
    if 'downloaded_data' not in st.session_state:
        st.session_state.downloaded_data = None
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button('下载并验证数据'):
            with st.spinner('正在下载数据...'):
                df = load_nasdaq_data(start_date, end_date)
                st.session_state.downloaded_data = df
                
            if df is not None:
                st.success(f'成功下载数据: {len(df)} 条记录')
                
                is_valid, message, yearly_stats = verify_data(df)
                
                st.subheader('年度数据完整性分析')
                if yearly_stats is not None:
                    def highlight_missing(row):
                        return ['background-color: #ffcccc' if row['缺失天数'] > 5 else '' for _ in row]
                    
                    styled_stats = yearly_stats.style.apply(highlight_missing, axis=1)
                    st.dataframe(styled_stats)
                    
                    problem_years = yearly_stats[yearly_stats['缺失天数'] > 5]
                    if not problem_years.empty:
                        st.warning("⚠️ 以下年份的数据缺失较多：\n" + 
                                 "\n".join([f"- {year}: 缺失 {days} 天" 
                                          for year, days in zip(problem_years['年份'], problem_years['缺失天数'])]))
                
                if is_valid:
                    st.success(message)
                else:
                    st.warning(message)
                
                st.subheader('数据预览')
                st.dataframe(df)
                
                csv = df.to_csv()
                st.download_button(
                    label="下载CSV文件",
                    data=csv,
                    file_name=f"nasdaq100_{start_date}_{end_date}.csv",
                    mime='text/csv'
                )
    
    with col2:
        if st.button('存入数据库', disabled=st.session_state.downloaded_data is None):
            if st.session_state.downloaded_data is not None:
                with st.spinner('正在保存到数据库...'):
                    db_manager.save_data(st.session_state.downloaded_data)
                st.success("数据已成功保存到数据库！")
                # 清除已下载的数据
                st.session_state.downloaded_data = None
            else:
                st.warning("请先下载数据")