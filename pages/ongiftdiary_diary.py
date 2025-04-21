import streamlit as st
#マルチページ機能
st.set_page_config(page_title="diary", page_icon="")
import json
import streamlit_calendar as st_calendar
import streamlit.components.v1 as components
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
                gift_name TEXT,
                gift_feature TEXT,
                gift_price TEXT,
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

# --- データ読み込み ---
def load_events_from_db():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM ondata", conn)
    conn.close()
    return df

df = load_events_from_db()

# --- URLから選択されたイベントのIDを取得 ---
query_params = st.query_params
selected_id = int(query_params.get("selected_id", [0])[0])

#タイトル
st.title('Diary')

#with st.sidebar:
#    st.header("表示設定")
#    selectable_columns = df.columns.drop(["id", "date"])  # IDや日付そのものは除く
#    display_column = st.selectbox("カレンダーに表示したいカラム", selectable_columns)

# --- FullCalendar 用データを生成 ---

def generate_color(mode, output1):
    base_colors = {
        "受けた恩": (0, 123, 255),   # 青ベース
        "与えた恩": (40, 167, 69),  # 緑ベース
        "送った恩": (255, 193, 7)   # オレンジベース
    }

    r, g, b = base_colors.get(mode, (108, 117, 125))  # fallback: グレー

    try:
        level = int(output1)
    except:
        level = 1  # 安全値

    alpha = 0.2 + (min(max(level, 1), 10) / 10) * 0.6  # alphaは0.2〜0.8
    return f"rgba({r},{g},{b},{alpha:.2f})"

events = []
for _, row in df.iterrows():
    if row["date"]:  # dateが空じゃないときのみ
        color = generate_color(row["mode"], row["output1"])
        
        # タイトル構築
        title_parts = [
            str(row["person_name"]) if row["person_name"] else "",
            str(row["scene"]) if row["scene"] else "",
            str(row["emotion"]) if row["emotion"] else ""
        ]
        title = "｜".join(filter(None, title_parts))  # 空文字は省く
        
        
        event = {
            "title": title,
            "start": row["date"],
            "color": color,
            "extendedProps":  {
                "id": int(row["id"]),
                "mode": row["mode"],
                "output1": row["output1"],
                "relationship": row["relationship"],
                "scene": row["scene"],
                "detail": row["detail"]
            }
        }
        events.append(event)

# --- FullCalendar HTML ---
events_json = json.dumps(events, ensure_ascii=False).replace("</", "<\\/")

calendar_html = f"""
<style>
  .highlight-event {{
    box-shadow: 0 0 0 3px red !important;
    border: 2px solid red !important;
    background-color: #fff !important;
  }}
</style>
<div id='calendar'></div>
<link href='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.css' rel='stylesheet' />
<script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js'></script>
<script>
  document.addEventListener('DOMContentLoaded', function () {{
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {{
      initialView: 'dayGridMonth',
      locale: 'ja',
      dayMaxEventRows: 4,
      events: {events_json},
      eventClick: function(info) {{
        const id = info.event.extendedProps.id;
        const url = new URL(window.location.href);
        url.searchParams.set('selected_id', id);
        window.location.href = url.toString();
      }},
      eventDidMount: function(info) {{
        let tooltip = "";
        for (const [key, value] of Object.entries(info.event.extendedProps)) {{
          tooltip += key + ": " + value + "\\n";
        }}
        info.el.title = tooltip;

        const selectedId = {selected_id};
        if (info.event.extendedProps.id === selectedId) {{
          info.el.classList.add("highlight-event");
        }}
      }}  // ← ← ← ここで正しく閉じてる！
    }});
    calendar.render();
  }});
</script>
"""

components.html(calendar_html, height=600)

# --- ハイライトされた恩を表示 ---
if selected_id:
    st.markdown("### 🧡 この恩の詳細")
    highlight_df = df[df["id"] == selected_id]
    st.dataframe(highlight_df.style.applymap(lambda x: "background-color: yellow", subset=pd.IndexSlice[:, :]))


#DFを利用して一覧を表示
def load_data():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql('SELECT id, name, gender, birth_date, lifestyle,date, mode, person_name, relationship, person_gender, person_age,kinds, scene, detail, emotion,level, ureP_level, distance,return_date, return_idea,gift_name,gift_feature,gift_price,output1, output2, output3, output4, output5,output6, output7 FROM ondata',conn)
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
        'gift_name': '贈り物名',
        'gift_feature': '贈り物特徴',
        'gift_price': '贈り物価格',
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

# --- 一覧表示（該当行を緑でハイライト） ---
def highlight_row(row):
    if row.name == selected_id:
        return ["background-color: lightgreen"] * len(row)
    else:
        return [""] * len(row)
st.dataframe(df.set_index("No").style.apply(highlight_row, axis=1))


#ここからはテスト用。。実際はときゅさんの入力より反映。#################################################


# データ取得
def fetch_ondata():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM ondata", conn)
    conn.close()
    return df  # ← これでOK

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


