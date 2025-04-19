import streamlit as st
from openai import OpenAI
import os
import pandas as pd
from io import BytesIO
import requests
import base64

from dotenv import load_dotenv
load_dotenv()

# OpenAI API キーを環境変数から取得
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Cloudinaryの設定
cloud_name = os.getenv("CLOUDINARY_NAME")
upload_preset = os.getenv("CLOUDINARY_PRESET")

st.title("頂いたもの解析アプリ")
st.write("画像をアップロードすると、その商品が何かを推測して5つの候補を表示します。")

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