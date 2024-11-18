import sqlite3
import json
import pandas as pd
from pathlib import Path
import os

class DBManager:
    def __init__(self):
        # 确保db目录存在
        Path("db").mkdir(exist_ok=True)
        self.db_path = "db/qqq.db"
        self.json_path = "db/qqq.json"
        self.init_db()
        self.init_json()

    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nasdaq_data (
                date DATE PRIMARY KEY,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                dividends REAL,
                stock_splits REAL,
                pe_ratio REAL
            )
        ''')
        conn.commit()
        conn.close()

    def init_json(self):
        """初始化JSON文件"""
        if not os.path.exists(self.json_path):
            self.save_metadata({
                "start_date": None,
                "end_date": None,
                "total_records": 0,
                "last_updated": None
            })

    def save_metadata(self, metadata):
        """保存元数据到JSON文件"""
        with open(self.json_path, 'w') as f:
            json.dump(metadata, f, indent=4)

    def get_metadata(self):
        """读取元数据"""
        with open(self.json_path, 'r') as f:
            return json.load(f)

    def save_data(self, df):
        """保存数据到SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        # 重置索引，将日期变成列
        df_to_save = df.reset_index()
        # 重命名 index 列为 date
        df_to_save = df_to_save.rename(columns={'index': 'date'})
        # 转换所有列名为小写
        df_to_save.columns = df_to_save.columns.str.lower()
        # 确保日期列是UTC时间
        df_to_save['date'] = pd.to_datetime(df_to_save['date']).dt.tz_localize(None)
        
        df_to_save.to_sql('nasdaq_data', conn, if_exists='replace', index=False)
        conn.close()

        # 更新元数据
        metadata = {
            "start_date": df_to_save['date'].min().strftime('%Y-%m-%d'),
            "end_date": df_to_save['date'].max().strftime('%Y-%m-%d'),
            "total_records": len(df),
            "last_updated": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_metadata(metadata)

    def load_data(self, start_date=None, end_date=None):
        """从数据库加载数据"""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM nasdaq_data"
        if start_date and end_date:
            query += f" WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        query += " ORDER BY date"  # 确保数据按日期排序
        
        # 读取数据
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # 将日期列转换为UTC时间并设置为索引
        df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_localize(None)
        df.set_index('date', inplace=True)
        
        return df