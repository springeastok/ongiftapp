import streamlit as st
import openai
from openai import OpenAI
import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
# 例: Macの場合（ヒラギノ角ゴ）
plt.rcParams['font.family'] = 'Hiragino Maru Gothic Pro'
import numpy as np

import os # OSが持つ環境変数OPENAI_API_KEYにAPIを入力するためにosにアクセスするためのライブラリをインポート
import dotenv # .envファイルを読み込むためのライブラリをインポート
from dotenv import load_dotenv
load_dotenv() # .envファイルを読み込むためのライブラリをインポート
# アクセスの為のキーをopenai.api_keyに代入し、設定
api_key = os.getenv("OPENAI_API_KEY")

os.environ["OPENAI_API_KEY"] = api_key # 環境変数OPENAI_API_KEYにAPIを代入 

# openAIの機能をclientに代入
client = OpenAI()

# アプリのタイトルを設定
st.title("恩 Gift Diary")

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
def run_gpt(content_text_to_GPT, content_kind_of_to_gpt, content_maxStr_to_gpt):
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

    # リクエスト文を作成
    request_to_gpt = (
        "以下の内容を基にダイアリーを作成してください。\n"
        + user_info
        + "日付: " + content_date_to_gpt_str + "\n"
        + "タイトルをつけてください。\n"
        + "内容: " + content_text_to_GPT + "\n"
        + "文体: " + content_kind_of_to_gpt + "\n"
        + "文字数: " + content_maxStr_to_gpt + "文字以内\n"
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
    gender = selectbox_with_others("恩の相手の性別(選択式)", ["男性", "女性"])
    age = selectbox_with_others("恩の相手の年齢(選択式)", ["10代", "20代", "30代", "40代", "50代", "60代", "70代以上"])

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
        content_maxStr_to_gpt = str(st.sidebar.slider('恩の感情レベル：その気持ちの感じかたの主観的強さを記録', 1,5,10))
        content_maxStr_to_gpt = str(st.sidebar.slider('嬉P度：その気持ちに加えて自分が感じた主観的な「嬉しさ」の度合いを記録', 1,5,10))
        content_maxStr_to_gpt = str(st.sidebar.slider('心のキョリ好影響度：相手との関係への主観的な好影響度合いを記録', 1,5,10))
        st.sidebar.date_input('恩返し予定日', datetime.date.today())
        content_text_to_gpt_list.append(selectbox_with_others("恩返し案(選択式)", ["物や食べ物をプレゼント", "言葉をかける", "時間や労力をかける", "経済的なお返しをする"]))


    elif mode == "返した恩":
        content_text_to_gpt_list.append(selectbox_with_others("恩の種類(選択式)", ["物や食べ物をプレゼント", "言葉をかける", "時間や労力をかける", "経済的なお返しをする"]))
        content_text_to_gpt_list.append(st.sidebar.text_input("具体的な内容について書いてください", placeholder="具体的な内容(フリー記述)"))
        content_text_to_gpt_list.append(st.sidebar.text_input("恩のシチュエーション／恩返しの機会", placeholder="恩返しの機会(フリー記述)"))
        content_text_to_gpt_list.append(selectbox_with_others("恩の感情/特に強く感じた気持ちを選んでください", ["感謝", "喜び", "感動", "興奮", "親しみ", "安心", "期待", "戸惑い", "安心", "恥ずかしさ", "申し訳なさ"]))
        content_maxStr_to_gpt = str(st.sidebar.slider('恩の感情レベル：その気持ちの感じかたの主観的強さを記録', 1,5,10))
        content_maxStr_to_gpt = str(st.sidebar.slider('嬉P度：その気持ちに加えて自分が感じた主観的な「嬉しさ」の度合いを記録', 1,5,10))
        content_maxStr_to_gpt = str(st.sidebar.slider('心のキョリ好影響度：相手との関係への主観的n好影響度合いを記録', 1,5,10))
    
    else:  # mode == "送った恩"
        content_text_to_gpt_list.append(selectbox_with_others("恩の種類(選択式)", ["物や食べ物をプレゼント", "言葉をかける", "時間や労力をかける", "経済的に負担をする"]))
        content_text_to_gpt_list.append(st.sidebar.text_input("具体的な内容について書いてください", placeholder="具体的な内容(フリー記述)"))
        content_text_to_gpt_list.append(st.sidebar.text_input("恩のシチュエーション／機会", placeholder="恩を送る機会(フリー記述)"))
        content_text_to_gpt_list.append(selectbox_with_others("恩の感情/特に強く感じた気持ちを選んでください", ["感謝", "喜び", "感動", "興奮", "親しみ", "安心", "期待", "戸惑い", "安心", "恥ずかしさ", "申し訳なさ"]))
        content_maxStr_to_gpt = str(st.sidebar.slider('恩の感情レベル：その気持ちの感じかたの主観的強さを記録', 1,5,10))
        content_maxStr_to_gpt = str(st.sidebar.slider('嬉P度：その気持ちに加えて自分が感じた主観的な「嬉しさ」の度合いを記録', 1,5,10))
        content_maxStr_to_gpt = str(st.sidebar.slider('心のキョリ好影響度：相手との関係への主観的な好影響度合いを記録', 1,5,10))
    
    return content_text_to_gpt, content_text_to_gpt_array, content_text_to_gpt_list

# ラジオボタンでモード選択
select_box = ["受けた恩", "返した恩", "送った恩"]
radio_select = st.sidebar.radio("恩の方向", select_box)

# 入力UIの表示
content_text_to_gpt, content_text_to_gpt_array, content_text_to_gpt_list = build_content_inputs(radio_select)

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
content_maxStr_to_gpt = str(st.sidebar.slider('ダイアリーの最大文字数', 100,500,1000))

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
    ax.fill(angles, scores, color='blue', alpha=0.25)
    ax.plot(angles, scores, color='blue', linewidth=2)
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
    if (content_text_to_gpt != ""):
        output_content.write("ダイアリー生成中")  # 状況案内を表示
        warning_text.write("")  # 正常に実行されているので、エラーを書き込む箱を空欄書き込みでリセット処理

        # chatGPTにリクエストするためのメソッドを設定
        output_content_text = run_gpt(content_text_to_gpt, content_kind_of_to_gpt, content_maxStr_to_gpt)

        # ダイアリーのタイトルを抽出（例: 最初の行をタイトルとする）
        diary_title = output_content_text.split("\n")[0] if "\n" in output_content_text else "生成されたタイトル"
        
        # 恩の日付をタイトルに追加
        diary_title_with_date = f"{content_date_to_gpt.strftime('%Y-%m-%d')} - {diary_title}"

        # ダイアリーの内容を表示
        st.write("生成ダイアリー")
        st.write(diary_content)  # 固定のテキスト
        st.write(content_date_to_gpt.strftime('%Y-%m-%d'))
        st.write(output_content_text)  # 生成されたダイアリーを表示

        # 編集可能なテキストエリアを表示
        st.write("生成されたダイアリーを編集してください:")
        editable_content = st.text_area("編集可能なダイアリー", value=output_content_text, height=300)

        # 編集後の内容をダウンロードするボタンを設置
        st.download_button(
            label='Download',
            data=editable_content,
            file_name='edited_output.txt',
            mime='text/plain',
        )
    else:
        warning_text.write("恩情報が不足しています")  # 書かせたい内容がないので、エラーとして表示

    # サンプルスコア（実際には入力データから計算）
    scores = [
        int(st.sidebar.slider("影響度", 1, 10, 5)),
        int(st.sidebar.slider("感動度", 1, 10, 7)),
        int(st.sidebar.slider("距離感の変化", 1, 10, 6)),
        int(st.sidebar.slider("お返ししたい気持ち", 1, 10, 8)),
        int(st.sidebar.slider("心情的繋がりの強さ", 1, 10, 9))
    ]
    labels = ["影響度", "感動度", "距離感の変化", "お返ししたい気持ち", "心情的繋がりの強さ"]

    # レーダーチャートを描画
    radar_chart = plot_radar_chart(scores, labels, title=diary_title_with_date)

    # スコア分析を縦に表示
    st.subheader("感動チャート")
    st.pyplot(radar_chart)