# -*- coding: utf-8 -*-
import streamlit as st

# ↓↓↓↓↓ ここにマルチページ機能を追加 ↓↓↓↓↓
st.set_page_config(page_title="diary", page_icon="")

import openai
import sqlite3
import datetime
import matplotlib.pyplot as plt
import japanize_matplotlib # 日本語化のためのライブラリをインポート
import numpy as np

# 画像記録アプリ有効化のためのライブラリをインポート
import pandas as pd
from io import BytesIO
import requests
import base64

import os # OSが持つ環境変数OPENAI_API_KEYにAPIを入力するためにosにアクセスするためのライブラリをインポート
# ↓↓↓↓↓ ここにテーブル作成機能を追加 ↓↓↓↓↓
base_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join("data", "on_data.db")
db_path = os.path.join(base_dir, relative_path)
os.makedirs(os.path.dirname(db_path), exist_ok=True)


def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS ondata (
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

# 起動時に実行
init_db()

import dotenv # .envファイルを読み込むためのライブラリをインポート
from dotenv import load_dotenv

load_dotenv() # .envファイルを読み込むためのライブラリをインポート
# アクセスの為のキーをopenai.api_keyに代入し、設定
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

api_key = os.getenv("OPENAI_API_KEY")

from openai import OpenAI
# openAIの機能をclientに代入
client = OpenAI()
api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key # 環境変数OPENAI_API_KEYにAPIを代入 


# アプリのタイトルを設定
st.title("恩 Gift Diary")
st.subheader("✨恩ギフトダイアリー & 感動チャート✨")
st.write("サイドバーにて簡単な項目を入力すると、あなたの「恩」にまつわる日記と感動チャートを生成します")

# ユーザー属性情報の入力と保持
st.sidebar.header("ユーザー情報")
if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "name": "",
        "gender": "",
        "birth_date": None,  # 生年月日を保持
        "lifestyle": ""
    }

# ユーザー情報の入力欄
st.session_state.user_info["name"] = st.sidebar.text_input("名前", value=st.session_state.user_info["name"])
st.session_state.user_info["gender"] = st.sidebar.selectbox("性別", ["選択してください", "男性", "女性", "その他"], index=["選択してください", "男性", "女性", "その他"].index(st.session_state.user_info["gender"]) if st.session_state.user_info["gender"] else 0)
st.session_state.user_info["birth_date"] = st.sidebar.date_input(
    "生年月日",
    value=st.session_state.user_info["birth_date"] if st.session_state.user_info["birth_date"] else datetime.date(2000, 1, 1),
    min_value=datetime.date.today() - datetime.timedelta(days=365 * 100),  # 100年前
    max_value=datetime.date.today()  # 今日まで
)
st.session_state.user_info["lifestyle"] = st.sidebar.text_input("ライフスタイル", value=st.session_state.user_info["lifestyle"])

# ユーザー情報を表示
st.sidebar.write("現在のユーザー情報:")
st.sidebar.write(f"名前: {st.session_state.user_info['name']}")
st.sidebar.write(f"性別: {st.session_state.user_info['gender']}")
st.sidebar.write(f"生年月日: {st.session_state.user_info['birth_date']}")
st.sidebar.write(f"ライフスタイル: {st.session_state.user_info['lifestyle']}")

# chatGPTにリクエストするためのメソッドを設定
def run_gpt(content_text_to_gpt, content_kind_of_to_gpt, content_maxStr_to_gpt,person_name_val, relationship_val, person_gender_val, person_age_val,emotion_level, ureP_level, distance_level):
    # content_date_to_gptを文字列に変換
    content_date_to_gpt_str = content_date_to_gpt.strftime("%Y-%m-%d")

    # ユーザー情報をリクエスト文に追加
    user_info = (
        f"ユーザー情報:\n"
        f"名前: {st.session_state.user_info['name']}\n"
        f"性別: {st.session_state.user_info['gender']}\n"
        f"生年月日: {st.session_state.user_info['birth_date']}\n"
        f"ライフスタイル: {st.session_state.user_info['lifestyle']}\n"
    )

    # スコア情報を追加
    score_info = (
        f"感情レベル: {emotion_level}\n"
        f"嬉P度: {ureP_level}\n"
        f"キョリ影響度: {distance_level}\n"
    )

    # リクエスト文を作成
    request_to_gpt = (
        "以下の内容を基にダイアリーを作成してください。\n"
        + user_info
        + "日付: " + content_date_to_gpt_str + "\n"
        + "タイトルをつけてください。\n"
        + "内容: " + content_text_to_gpt + "\n"
        + "文体: " + content_kind_of_to_gpt + "\n"
        + "文字数: " + content_maxStr_to_gpt + "文字以内\n"
        + score_info
    )

    # OpenAI APIへのリクエスト
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": request_to_gpt},
        ],
    )

    # 出力結果を取得
    output_content = response.choices[0].message.content.strip()
    return output_content    
    content_text_to_gpt_list.append(st.sidebar.date_input('恩の日付', datetime.date.today()))

print("恩ダイアリー")
output_content = st.empty() # chatGPTから出力された文字を代入するための箱を用意

content_date_to_gpt = st.sidebar.date_input('恩の日付', datetime.date.today())

def selectbox_with_others(label, options, placeholder="選択してください"):
    selected = st.sidebar.selectbox(label, options + ["その他"])
    if selected == "その他":
        return st.sidebar.text_input(f"{label}「その他」の内容", placeholder="「その他」の内容（自由記述）")
    return selected

# 入力欄の構築関数
def build_content_inputs(mode):
    content_text_to_gpt = ""
    content_text_to_gpt_array = []
    content_text_to_gpt_list = []

# 恩の相手の名前と関係性を入力
    person_name = st.sidebar.text_input("恩の相手の名前", placeholder="相手の名前")
    relationship = selectbox_with_others("恩の相手との関係(選択式)", ["友人", "家族", "恋人", "同僚", "上司", "先輩", "後輩", "部下", "恩師"])
    person_gender = selectbox_with_others("恩の相手の性別(選択式)", ["男性", "女性"])
    person_age = selectbox_with_others("恩の相手の年齢(選択式)", ["10代", "20代", "30代", "40代", "50代", "60代", "70代以上"])

    # 名前と関係性を統合
    if person_name and relationship:
        combined_person_info = f"『{relationship}』である『{person_name}』"
    elif person_name:  # 名前のみ
        combined_person_info = f"『{person_name}』"
    elif relationship:  # 関係性のみ
        combined_person_info = f"『{relationship}』"
    else:
        combined_person_info = ""  # 両方空欄の場合は空文字列

    if combined_person_info:
        content_text_to_gpt_list.append(combined_person_info)
    
    if mode == "受けた恩":
        content_text_to_gpt_list.append(selectbox_with_others("恩の種類(選択式)", ["物や食べ物をもらった", "言葉をかけてくれた", "時間や労力をかけてくれた", "経済的に助けてくれた"]))
        content_text_to_gpt_list.append(selectbox_with_others("恩のシチュエーション(選択式)", ["誕生日", "イベント", "職場", "卒業", "入学", "結婚", "出産"]))
        content_text_to_gpt_list.append(st.sidebar.text_input("具体的な内容について書いてください", placeholder="具体的な内容(フリー記述)"))
        content_text_to_gpt_list.append(selectbox_with_others("恩に対する感情/特に強く感じた気持ちを選んでください", ["感謝", "驚き", "喜び", "感動", "興奮", "親しみ","期待", "戸惑い", "安心", "恥ずかしさ", "申し訳なさ"]))
        # 恩の感情レベルをスライドバーで表示する
        emotion_level = st.sidebar.slider('恩の感情レベル：その気持ちの感じかたの主観的強さを記録', 1,10,5)
        ureP_level = st.sidebar.slider('嬉P度：その気持ちに加えて自分が感じた主観的な「嬉しさ」の度合いを記録', 1,10,5)
        distance_level = st.sidebar.slider('心のキョリ好影響度：相手との関係への主観的な好影響度合いを記録', 1,10,5)
        st.sidebar.date_input('恩返し予定日', datetime.date.today())
        content_text_to_gpt_list.append(selectbox_with_others("恩返し案(選択式)", ["物や食べ物をプレゼント", "言葉をかける", "時間や労力をかける", "経済的なお返しをする"]))


    elif mode == "返した恩":
        content_text_to_gpt_list.append(selectbox_with_others("恩の種類(選択式)", ["物や食べ物をプレゼント", "言葉をかける", "時間や労力をかける", "経済的なお返しをする"]))
        content_text_to_gpt_list.append(st.sidebar.text_input("具体的な内容について書いてください", placeholder="具体的な内容(フリー記述)"))
        content_text_to_gpt_list.append(st.sidebar.text_input("恩のシチュエーション／恩返しの機会", placeholder="恩返しの機会(フリー記述)"))
        content_text_to_gpt_list.append(selectbox_with_others("恩の感情/特に強く感じた気持ちを選んでください", ["感謝", "喜び", "感動", "興奮", "親しみ", "安心", "期待", "戸惑い", "安心", "恥ずかしさ", "申し訳なさ"]))
        emotion_level = st.sidebar.slider('恩の感情レベル：その気持ちの感じかたの主観的強さを記録', 1,10,5)
        ureP_level = st.sidebar.slider('嬉P度：その気持ちに加えて自分が感じた主観的な「嬉しさ」の度合いを記録', 1,10,5)
        distance_level = st.sidebar.slider('心のキョリ好影響度：相手との関係への主観的な好影響度合いを記録', 1,10,5)
    
    else:  # mode == "送った恩"
        content_text_to_gpt_list.append(selectbox_with_others("恩の種類(選択式)", ["物や食べ物をプレゼント", "言葉をかける", "時間や労力をかける", "経済的に負担をする"]))
        content_text_to_gpt_list.append(st.sidebar.text_input("具体的な内容について書いてください", placeholder="具体的な内容(フリー記述)"))
        content_text_to_gpt_list.append(st.sidebar.text_input("恩のシチュエーション／機会", placeholder="恩を送る機会(フリー記述)"))
        content_text_to_gpt_list.append(selectbox_with_others("恩の感情/特に強く感じた気持ちを選んでください", ["感謝", "喜び", "感動", "興奮", "親しみ", "安心", "期待", "戸惑い", "安心", "恥ずかしさ", "申し訳なさ"]))
        emotion_level = st.sidebar.slider('恩の感情レベル：その気持ちの感じかたの主観的強さを記録', 1,10,5)
        ureP_level = st.sidebar.slider('嬉P度：その気持ちに加えて自分が感じた主観的な「嬉しさ」の度合いを記録', 1,10,5)
        distance_level = st.sidebar.slider('心のキョリ好影響度：相手との関係への主観的な好影響度合いを記録', 1,10,5)
    
    return (
        content_text_to_gpt,
        content_text_to_gpt_array,
        content_text_to_gpt_list,
        person_name,
        relationship,
        person_gender,
        person_age,
        emotion_level,
        ureP_level,
        distance_level
    )

# ラジオボタンでモード選択
select_box = ["受けた恩", "返した恩", "送った恩"]
radio_select = st.sidebar.radio("恩の方向", select_box)

# 入力UIの表示
(
    content_text_to_gpt,
    content_text_to_gpt_array,
    content_text_to_gpt_list,
    person_name_val,
    relationship_val,
    person_gender_val,
    person_age_val,
    level_val,
    ureP_level_val,
    distance_level_val
) = build_content_inputs(radio_select)

# 入力された配列から空欄を排除し、content_text_to_gpt_arrayに代入
content_text_to_gpt_array = []  # 初期化を確認

# content_text_to_gpt_listが初期化されているか確認
if 'content_text_to_gpt_list' in locals() and content_text_to_gpt_list:
    for c in content_text_to_gpt_list:
        if c != "":
            # datetime.date型の場合は文字列に変換
            if isinstance(c, datetime.date):
                content_text_to_gpt_array.append(c.strftime("%Y-%m-%d"))
            else:
                content_text_to_gpt_array.append(c)
else:
    warning_text.write("入力項目がありません。リストが初期化されていない可能性があります。")

# 整理した結果、１つでも内容がある場合、書かせたい内容に変換する
if content_text_to_gpt_array:
    content_text_to_gpt = "入力した項目は" + "、".join(content_text_to_gpt_array) + " です。"
else:
    content_text_to_gpt = "入力項目がありません。"

# 日記の文体
content_kind_of = [
    "シンプルな記録調",
    "ビジネスライク報告調",
    "ハイテンション",
    "物語調",
    "詩的・文学的",
    "SNS風",
    "知的読み物調",
    "エッセイ風",
    "実況中継風",
    "こども日記風",
    "手紙スタイル",
    "ツンデレ",
    "J-POP歌詞風",
    "HIP-HOP",
    "少年マンガ風",
    "ひろゆき風",
    "連歌スタイル",
    "おまかせ",
    "フリー記述でスタイルを指定"
]
            
# 書かせたい内容のテイストを選択肢として表示する
content_kind_of_to_gpt = selected_style = st.sidebar.selectbox("ダイアリーの文体・雰囲気",options=content_kind_of)

# 「フリー記述」が選ばれた場合は入力欄を表示
if selected_style == "フリー記述でスタイルを指定":
    custom_style = st.sidebar.text_input("自由に文体を記述してください（例：昭和の文豪風）")
else:
    custom_style = selected_style

st.sidebar.write("文章のスタイル：", custom_style)

# chatGPTに出力させる文字数をスライドバーで表示する
content_maxStr_to_gpt = str(st.sidebar.slider('ダイアリーの最大文字数', 100,1000,500))

# エラーが起きたときに表示するための箱をサイドバーに用意する
warning_text = st.sidebar.empty()


# レーダーチャートを描画する関数
def plot_radar_chart(scores, labels, title="スコア分析"):
    # スコアの数に応じて角度を計算
    num_vars = len(scores)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    scores += scores[:1]  # 最後の点を最初に戻す
    angles += angles[:1]

    # プロットの設定
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, scores, color='orange', alpha=0.25)
    ax.plot(angles, scores, color='orange', linewidth=2)
    ax.set_yticks([2, 4, 6, 8, 10])  # スコアの目盛り
    ax.set_yticklabels(["2", "4", "6", "8", "10"], color="gray", size=8)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_title(title, size=16, color="black", pad=20)

    return fig

# ダイアリーの生成とスコアの可視化を同時に行う
if st.sidebar.button("ダイアリーとスコアを表示"):
    # ダイアリーの内容（例として固定のテキストを使用）
    diary_content = "恩を感じた出来事を自動で文章化します。"

    # 無駄にリクエストしないように書かせたい内容に中身があるか確認し、あれば実行
    if content_text_to_gpt != "":
        output_content.write("ダイアリー生成中")  # 状況案内を表示
        warning_text.write("")  # 正常に実行されているので、エラーを書き込む箱を空欄書き込みでリセット処理

        # chatGPTにリクエストするためのメソッドを設定
        output_content_text = run_gpt(
            content_text_to_gpt,
            content_kind_of_to_gpt,
            content_maxStr_to_gpt,
            person_name_val,
            relationship_val,
            person_gender_val,
            person_age_val,
            level_val,
            ureP_level_val,
            distance_level_val
        )


        # ダイアリーのタイトルを抽出（例: 最初の行をタイトルとする）
        diary_title = output_content_text.split("\n")[0] if "\n" in output_content_text else "生成されたタイトル"
        
        # 恩の日付をタイトルに追加
        diary_title_with_date = f"{content_date_to_gpt.strftime('%Y-%m-%d')} - {diary_title}"

        # スコアの初期化と保存
        st.session_state.generated_diary = output_content_text
        st.session_state.generated_title = diary_title_with_date

        # スコアの初期値（保存）
        st.session_state.output_scores = {
            "感動度": 7,
            "影響度": 5,
            "距離感の変化": 4,
            "お返ししたい気持ち": 6,
            "心情的つながり": 9
        }
                # 【ここから保存用変数の定義】
        name_val = st.session_state.user_info.get("name", "")
        gender_val = st.session_state.user_info.get("gender", "")
        birth_date_val = st.session_state.user_info.get("birth_date", datetime.date(2000,1,1)).strftime('%Y-%m-%d')
        lifestyle_val = st.session_state.user_info.get("lifestyle", "")
        date_val = content_date_to_gpt.strftime('%Y-%m-%d')
        mode_val = radio_select

        # content_text_to_gpt_list から取得（modeごとに処理）
        offset = 1 if person_name_val or relationship_val else 0
        kinds_val = content_text_to_gpt_list[offset]
        scene_val = content_text_to_gpt_list[offset + 1]
        detail_val = content_text_to_gpt_list[offset + 2]
        emotion_val = content_text_to_gpt_list[offset + 3]
        return_date_val = ""
        return_idea_val = ""
        gift_name_val = ""
        gift_feature_val = ""   
        gift_price_val = ""

        if mode_val == "受けた恩":
            return_idea_val = content_text_to_gpt_list[offset + 4]
            return_date_obj = st.session_state.get("恩返し予定日", datetime.date.today())
            return_date_val = return_date_obj.strftime('%Y-%m-%d')

        #level_val = st.sidebar.slider("感情レベル", 1, 5, 3)
        #ureP_level_val = st.sidebar.slider("嬉P度", 1, 5, 3)
        #distance_val = st.sidebar.slider("心のキョリ好影響度", 1, 5, 3)
        level_val = level_val
        ureP_level_val = ureP_level_val
        distance_val = distance_level_val

        output1_val = st.session_state.output_scores["感動度"] #st.sidebar.slider("保存用 感動度", 1, 10, 5)
        output2_val = st.session_state.output_scores["影響度"] #st.sidebar.slider("保存用 影響度", 1, 10, 5)
        output3_val = st.session_state.output_scores["心情的つながり"] #st.sidebar.slider("保存用 心情的つながり", 1, 10, 5)
        output4_val = st.session_state.output_scores["お返ししたい気持ち"] #st.sidebar.slider("保存用 お返ししたい気持ち", 1, 10, 5)
        output5_val = st.session_state.output_scores["距離感の変化"] #st.sidebar.slider("保存用 距離感の変化", 1, 10, 5)

        output6_val = output_content_text
        output7_val = ""  # 画像未対応のため空欄

        # ↓↓↓↓↓ ここに保存処理を追加 ↓↓↓↓↓
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('''
                INSERT INTO ondata (
                    name, gender, birth_date, lifestyle,
                    date, mode, person_name, relationship, person_gender, person_age,
                    kinds, scene, detail, emotion,
                    level, ureP_level, distance,
                    return_date, return_idea,gift_name, gift_feature, gift_price,
                    output1, output2, output3, output4, output5,
                    output6, output7
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name_val, gender_val, birth_date_val, lifestyle_val,
                content_date_to_gpt.strftime("%Y-%m-%d"),
                mode_val, person_name_val, relationship_val, person_gender_val, person_age_val,
                kinds_val, scene_val, detail_val, emotion_val,
                level_val, ureP_level_val, distance_val,
                return_date_val, return_idea_val,gift_name_val, gift_feature_val, gift_price_val,
                output1_val, output2_val, output3_val, output4_val, output5_val,
                output6_val, output7_val
            ))
            # 🔽 lastrowid を session_state に保存
            st.session_state.generated_id = c.lastrowid

            conn.commit()
            conn.close()
            st.success("データベースに保存されました！")
            
        except Exception as e:
            st.error(f"保存時にエラーが発生しました: {e}")
        # ↑↑↑↑↑ ここまでが保存処理 ↑↑↑↑↑
else:
    warning_text.write("入力内容をチェックして、ボタンを押してください。")  



# 生成済みの場合の表示（リロード防止 & スライダー編集可能）
if "generated_diary" in st.session_state:
    st.subheader("生成ダイアリー")
    st.write(st.session_state.generated_title)
    st.write(st.session_state.generated_diary)

    st.subheader("保存用スコアの調整")
    for key in st.session_state.output_scores:
        st.session_state.output_scores[key] = st.sidebar.slider(f"{key}", 1, 10, st.session_state.output_scores[key])
    
    
    # チャート描画
    scores = list(st.session_state.output_scores.values())
    labels = list(st.session_state.output_scores.keys())
    radar_chart = plot_radar_chart(scores, labels, title=st.session_state.generated_title)

    # スコア分析を縦に表示
    st.subheader("感動チャート")
    st.pyplot(radar_chart)

    # 編集可能なテキストエリアを表示
    st.write("生成されたダイアリーを編集してください:")
    editable_content = st.text_area("編集可能なダイアリー", st.session_state.generated_diary, height=300)

    # 編集後の内容をダウンロードするボタンを設置
    if st.download_button(
        label='更新してダウンロード',
        data=editable_content,
        file_name='edited_output.txt',
        mime='text/plain',
        ):

        if "generated_id" in st.session_state:
            try:    
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute('''
                    UPDATE ondata SET
                        output1 = ?, output2 = ?, output3 = ?, output4 = ?, output5 = ?, output6 = ?
                    WHERE id = ?
                ''', (
                    st.session_state.output_scores["感動度"],
                    st.session_state.output_scores["影響度"],
                    st.session_state.output_scores["心情的つながり"],
                    st.session_state.output_scores["お返ししたい気持ち"],
                    st.session_state.output_scores["距離感の変化"],
                    editable_content,
                    st.session_state.generated_id
                ))
                conn.commit()
                conn.close()
                st.success("スコアと内容をデータベースに上書き保存しました！")
            except Exception as e:
                st.error(f"更新エラー: {e}")
        else:
            st.warning("データベースに保存されたIDが見つかりません。再度「ダイアリーとスコアを表示」から始めてください。")
    # 画像記録アプリの機能を追加
    # Cloudinaryの設定
cloud_name = os.getenv("CLOUDINARY_NAME")
upload_preset = os.getenv("CLOUDINARY_PRESET")

st.subheader("🎁頂きもの画像解析")
st.write("下の枠から画像をアップロードするとその商品が何かを推測して5つの候補を表示します")

# 画像アップロード
uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "jpeg", "png"])

# セッション状態の初期化
if "candidates" not in st.session_state:
    st.session_state["candidates"] = []
if "image_bytes" not in st.session_state:
    st.session_state["image_bytes"] = None

# 画像解析ボタン
if uploaded_file:
    st.session_state["image_bytes"] = uploaded_file.read()
    if st.button("画像を解析する"):
        try:
            # OpenAI APIで商品を推定
            encoded_image = base64.b64encode(st.session_state["image_bytes"]).decode()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたはあらゆる商品に精通した、プロダクトウオッチャー兼アナリストです。"},
                    {"role": "user", "content": [
                        {"type": "text", "text": "この画像の商品について、推定される商品を5パターン挙げて以下の項目を書いてください。この内容以外の記載は不要です。\n- 商品名\n- 特徴\n- おおよその小売価格（日本円）"},
                        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + encoded_image }}
                    ]},
                ],
                max_tokens=500
            )

            # GPTからの応答（候補リスト）をセッション状態に保存
            result_text = response.choices[0].message.content
            st.session_state["candidates"] = result_text.strip().split("\n\n")
            st.success("解析が完了しました！")

        except Exception as e:
            st.error("解析中にエラーが発生しました。")
            st.text(f"エラー内容: {e}")

# 候補リストを取得
candidates = st.session_state["candidates"]

if candidates:
    st.markdown("### 商品の候補")
    for candidate in candidates:
        st.write(candidate)

    # 手入力オプションを表示
    st.markdown("### 候補を参考に入力してください")
    custom_name = st.text_input(
        "商品名", 
        value=st.session_state.get("custom_name", ""), 
        key="custom_name"
    )
    custom_features = st.text_area(
        "特徴", 
        value=st.session_state.get("custom_features", ""), 
        key="custom_features"
    )
    custom_price = st.text_input(
        "おおよその小売価格（円）", 
        value=st.session_state.get("custom_price", ""), 
        key="custom_price"
    )

    # 入力内容をセッション状態に保存
    if custom_name != st.session_state.get("custom_name", ""):
        st.session_state["custom_name"] = custom_name
    if custom_features != st.session_state.get("custom_features", ""):
        st.session_state["custom_features"] = custom_features
    if custom_price != st.session_state.get("custom_price", ""):
        st.session_state["custom_price"] = custom_price

    # 入力完了ボタン
    if st.button("入力完了"):
        selected_summary = {
            "商品名": custom_name if custom_name else "未入力",
            "特徴": custom_features if custom_features else "未入力",
            "おおよその小売価格": custom_price if custom_price else "未入力"
        }
        st.write("以下の内容が入力されました：")
        st.json(selected_summary)

                # Cloudinaryにアップロード
        st.markdown("### Cloudinaryに画像を保存中...")
        upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
        res = requests.post(
            upload_url,
            files={"file": st.session_state["image_bytes"]},
            data={"upload_preset": upload_preset}
        )

        if res.status_code == 200:
            image_url = res.json()["secure_url"]
            st.image(image_url, caption="保存された画像", use_column_width=True)
            st.success("画像の保存とURL取得に成功しました！")
        else:
            st.error("画像の保存に失敗しました")
            st.text(f"エラーコード: {res.status_code}")
            st.text(f"レスポンス: {res.text}")

        # ダウンロード用CSVの生成
        if res.status_code == 200:
            selected_summary["画像URL"] = image_url
            df = pd.DataFrame([selected_summary])
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="この情報をダウンロード",
                data=csv,
                file_name="item_summary.csv",
                mime="text/csv"
            )