import streamlit as st
#マルチページ機能
st.set_page_config(page_title="diary", page_icon="")

import streamlit_calendar as st_calendar
import pandas as pd 
import sqlite3 
import os
from datetime import datetime, timedelta

# データベースパスの設定（スクリプトの上の方に置く）
base_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join("data", "on_data.db")
db_path = os.path.join(base_dir, relative_path)
os.makedirs(os.path.dirname(db_path), exist_ok=True)


# SQLiteに接続する　#ときゅさんの新規追加分は一旦””で囲む
def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ondata(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        "name" 
        "gender"
        "birth_date"
        "lifestyle"
        "person_name"
        "gender
        date TEXT,
        relationship TEXT,
        scene TEXT,
        detail BLOB,
        things TEXT,
        price INTEGER,
        return_value TEXT
              )''')
    
    conn.commit()
    conn.close()

init_db()



#タイトル
st.title('Diary')

#calendar表示
def load_events_from_db():
    events = []

    # SQLite DBに接続
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # テーブルから全データ取得
    c.execute("SELECT id, date, relationship, scene, detail FROM ondata")
    rows = c.fetchall()
    conn.close()

    # データをカレンダー用のevent形式に変換
    for row in rows:
        event = {
            'id': str(row[0]),
            'groupId': '与えた恩' if row[0] % 2 == 0 else '受けた恩',  # 仮のグループ分け（必要に応じて変更）
            'color': "#FFFFCC" if row[0] % 2 == 0 else "#FFCCFF",
            'textColor': "#333333",
            'title':f"{row[2]} - {row[3]}",  # relationship を表示
            'start': row[1],  # 日付
            }
        events.append(event)
    return events


# calendarにはイベント一覧を配列にして渡す
event_list = load_events_from_db()

calendar_options = {
    "initialView": "dayGridMonth",
    "dayMaxEvents": 3,  # ← 1日の最大表示数
}

# イベントを表示するカレンダーを作成
cal = st_calendar.calendar(events = event_list ,options = calendar_options)

#DFを利用して一覧を表示

def load_data():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql('SELECT id, date, relationship,scene,detail,things,price,return_value FROM ondata',conn)
    conn.close()

    # カラム名の変更
    df = df.rename(columns={
        'id': 'No',
        'date': '日付',
        'relationship': '関係',
        'scene': 'シーン',
        'detail': '詳細',
        'things': '物',
        'price': '金額',
        'return_value': 'お返し'
    })

    return df
    
init_db() 
st.subheader("恩の一覧")

df = load_data()
#インデックス番号を削除　→　ID表示に変更。
st.dataframe(df.set_index("No"))


#ここからはテスト用。。実際はときゅさんの入力より反映。#################################################


# データ取得
def fetch_ondata():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    df = pd.read_sql_query(f"SELECT * FROM ondata", conn)
    conn.close()
    return result

def fetch_ondata():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    result = c.execute("SELECT * FROM ondata").fetchall()
    conn.close()
    return result

def insert_ondata(date, relationship, scene, detail, things, price, return_value):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO ondata(date, relationship, scene, detail, things, price, return_value) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (date, relationship, scene, detail, things, price, return_value)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"データ追加中にエラーが発生しました: {e}")


# 入力フォーム
st.subheader("恩入力")
new_date = st.date_input("日付", datetime.now())
new_relationship = st.selectbox("関係", ["家族", "友人", "恋人", "上司"]) 
new_scene = st.text_input("シーン")
new_detail = st.text_area("詳細")
new_things = st.text_input("物品")
new_price = st.number_input("金額", min_value=0, step=100000)
new_return_value = st.text_input("お返し")

# フォームが送信されたらデータベースに新しい恩を挿入
if st.button("追加"):
    insert_ondata(new_date, new_relationship, new_scene, new_detail, new_things, new_price, new_return_value)
    st.success("恩データが追加されました！")

    
