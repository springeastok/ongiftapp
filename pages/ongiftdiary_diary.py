import streamlit as st
#マルチページ機能
st.set_page_config(page_title="diary", page_icon="")

import streamlit_calendar as st_calendar
import pandas as pd 
import sqlite3 
import os
from datetime import datetime, timedelta

# データベースパスの設定（スクリプトの上の方に置く）
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(base_dir, "data", "on_data.db") 
#os.makedirs(os.path.dirname(db_path), exist_ok=True)


# SQLiteに接続する　#ときゅさんの新規追加分は一旦””で囲む
def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ondata(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                gender TEXT,
                birth_date TEXT,
                lifestyle TEXT,
                date TEXT,
                mode TEXT,
                person_name TEXT,
                relationship TEXT,
                person_gender TEXT,
                person_age TEXT,
                kinds TEXT,
                scene TEXT,
                detail TEXT,
                emotion TEXT,
                level INTEGER,
                ureP_level INTEGER,
                distance INTEGER,
                return_date TEXT,
                return_idea TEXT,
                output1 INTEGER,
                output2 INTEGER,
                output3 INTEGER,
                output4 INTEGER,
                output5 INTEGER,
                output6 TEXT,
                output7 TEXT
        )
    ''')
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
    c.execute("SELECT id, name, gender, birth_date, lifestyle,date, mode, person_name, relationship, person_gender, person_age,kinds, scene, detail, emotion,level, ureP_level, distance,return_date, return_idea,output1, output2, output3, output4, output5,output6, output7 FROM ondata")
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
    df = pd.read_sql('SELECT id, name, gender, birth_date, lifestyle,date, mode, person_name, relationship, person_gender, person_age,kinds, scene, detail, emotion,level, ureP_level, distance,return_date, return_idea,output1, output2, output3, output4, output5,output6, output7 FROM ondata',conn)
    conn.close()

    # カラム名の変更
    df = df.rename(columns={
        'id': 'No',
        'name': '名前',
        'gender': '性別',
        'birth_date': '誕生日',
        'lifestyle': 'ライフスタイル',
        'date': '日付',
        'mode': 'モード',
        'person_name': '相手の名前',
        'relationship': '関係',
        'person gender': '相手の性別',
        'person_age': '相手の年齢',
        'kinds': '種類',
        'scene': 'シーン',
        'detail': '詳細',
        'emotion': '感情',
        'level': 'レベル',
        'ureP_level': 'うれPレベル',
        'distance': '距離',
        'return_date': 'お返し日',
        'return_idea': 'お返しアイデア',
        'output1': '出力1',
        'output2': '出力2',
        'output3': '出力3',
        'output4': '出力4',
        'output5': '出力5',
        'output6': '出力6',
        'output7': '出力7'
        })

    return df
    
init_db() 
st.subheader("恩一覧")

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

def insert_ondata(date, relationship, scene, detail):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO ondata(date, relationship, scene, detail,) VALUES (?, ?, ?, ?)",
            (date, relationship, scene, detail)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"データ追加中にエラーが発生しました: {e}")


