import pymysql
import pandas as pd
import uuid
import os
import random

def get_mysql_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='123456',  # 刚刚测试成功的密码
        database='ecommerce_db',
        charset='utf8mb4'
    )

DB_PATH = "system_data.db" # fallback unused config

SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS reviews_log (
    review_id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(50),
    product_category VARCHAR(50),
    content TEXT,
    rating INTEGER,
    user_emotion VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    agent_response TEXT,
    coupon_issued DECIMAL(10,2) DEFAULT 0.0,
    channel VARCHAR(50) DEFAULT '电商智能渠道'
);

CREATE TABLE IF NOT EXISTS defect_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id VARCHAR(100),
    product_category VARCHAR(50),
    defect_name VARCHAR(100),
    severity VARCHAR(20),
    FOREIGN KEY (review_id) REFERENCES reviews_log(review_id)
);

CREATE TABLE IF NOT EXISTS user_profile (
    user_id VARCHAR(50) PRIMARY KEY,
    user_type VARCHAR(20),
    loyalty_score INTEGER,
    last_active DATETIME
);
"""

def init_db(db_path=DB_PATH):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    pass
    
    # Try logic for migration
    try:
        cursor.execute("ALTER TABLE reviews_log ADD COLUMN channel VARCHAR(50) DEFAULT '电商智能渠道'")
    except:
        pass # column exists
    
    conn.commit()
    conn.close()

def log_interaction(category, content, user_emotion, defects, response, coupon_issue, channel='电商智能渠道'):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        r_id = str(uuid.uuid4())
        u_id = "User_Live"
        cursor.execute('''INSERT INTO reviews_log (review_id, user_id, product_category, content, user_emotion, agent_response, coupon_issued, channel) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (r_id, u_id, category, content, user_emotion, response, float(coupon_issue), channel))
        
        if defects:
            for defect in defects:
                cursor.execute('''INSERT INTO defect_stats (review_id, product_category, defect_name, severity) VALUES (%s, %s, %s, %s)''', (r_id, category, defect, 'Medium'))
        conn.commit()
    except Exception as e:
        print(f"Log Error: {e}")
    finally:
        conn.close()

def get_dashboard_stats():
    if not os.path.exists(DB_PATH):
        return {'total_sessions': 0, 'interception_rate': 0.0, 'manual_route': 0.0, 'total_coupon': 0.0}
    
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM reviews_log")
    row_a = cursor.fetchone()
    total_sessions = row_a[0] if row_a else 0
    cursor.execute("SELECT SUM(coupon_issued) FROM reviews_log")
    row_b = cursor.fetchone()
    total_coupon = float(row_b[0]) if (row_b and row_b[0] is not None) else 0.0
    cursor.execute("SELECT COUNT(*) FROM reviews_log WHERE user_emotion IN ('Angry', 'Disappointed')")
    row_c = cursor.fetchone()
    angry_count = row_c[0] if row_c else 0
    
    if total_sessions > 0:
        interception_rate = ((total_sessions - (angry_count * 0.15)) / total_sessions) * 100
        manual_route = 100 - interception_rate
    else:
        interception_rate = 0.0
        manual_route = 0.0
    conn.close()
    return {'total_sessions': total_sessions, 'interception_rate': min(100.0, max(0.0, interception_rate)), 'manual_route': min(100.0, max(0.0, manual_route)), 'total_coupon': float(total_coupon)}

def get_top_defects(category_name):
    conn = get_mysql_connection()
    sql = "SELECT defect_name, COUNT(*) as frequency FROM defect_stats WHERE product_category = %s GROUP BY defect_name ORDER BY frequency DESC LIMIT 5;"
    df = pd.read_sql_query(sql, conn, params=(category_name,))
    conn.close()
    return df

def get_channel_stats():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame({'渠道': ['天猫/京东', '抖音/快手', '微信小程序', '其他'], '占比': ['0%', '0%', '0%', '0%']})
    
    conn = get_mysql_connection()
    
    # Actually count from DB for real data
    sql = "SELECT channel, COUNT(*) as count FROM reviews_log GROUP BY channel ORDER BY count DESC"
    df = pd.read_sql_query(sql, conn)
    conn.close()
    
    if df.empty:
        return pd.DataFrame({'渠道': ['天猫/京东', '抖音/快手', '微信小程序', '其他'], '占比': ['0%', '0%', '0%', '0%']})
    
    total = df['count'].sum()
    df['占比'] = (df['count'] / total * 100).apply(lambda x: f"{x:.1f}%")
    df.rename(columns={'channel': '渠道'}, inplace=True)
    return df[['渠道', '占比']]
