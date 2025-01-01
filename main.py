import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import base64
import io

def text_to_speech(text, lang='ja'):
    """テキストを音声に変換してbase64エンコードされた音声データを返す"""
    try:
        tts = gTTS(text=text, lang=lang)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        audio_bytes = audio_fp.read()
        b64 = base64.b64encode(audio_bytes).decode()
        return f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    except Exception as e:
        st.error(f"音声変換中にエラーが発生しました: {e}")
        return None

def select_script(df):
    """データフレームからランダムに1行選択して削除"""
    if df.empty:
        return "これで終わりです。", "終了"

    selected_index = random.randint(0, len(df) - 1)
    selected = df.iloc[selected_index]

    df.drop(df.index[selected_index], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return selected['ひらがな'], selected['script']

class Karuta:
    def __init__(self, data):
        """かるたゲームの初期化"""
        self.data = data
        self.reset_scripts()
        self.current_hiragana = None
        self.current_yomifuda = None

    def reset_scripts(self):
        """スクリプトをリセット"""
        try:
            if isinstance(self.data, str):  # ファイルパスの場合
                self.scripts = pd.read_csv(self.data, encoding='utf-8')
            else:  # DataFrameの場合
                self.scripts = self.data.copy()
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            self.scripts = pd.DataFrame(columns=['ひらがな', 'script'])

    def read_out_script(self):
        """現在の読み札を読み上げ"""
        if self.current_hiragana and self.current_yomifuda:
            audio_html = text_to_speech(f"{self.current_hiragana}、{self.current_yomifuda}")
            if audio_html:
                st.markdown(audio_html, unsafe_allow_html=True)

    def select_yomifuda(self):
        """新しい読み札を選択して読み上げ"""
        self.current_hiragana, self.current_yomifuda = select_script(self.scripts)
        self.read_out_script()
        return self.current_hiragana, self.current_yomifuda

def main():
    st.header('かるたゲーム')
    if 'display_text' not in st.session_state:
        st.session_state.display_text = {'hiragana': '', 'yomifuda': ''}

    # サイドバーでファイルアップロード
    with st.sidebar:
        st.markdown("### ゲーム設定")
        uploaded_file = st.file_uploader("CSVファイルをアップロード", type=['csv'])

    # カルタゲームの初期化
    if 'karuta' not in st.session_state or uploaded_file:
        if uploaded_file is not None:
            # アップロードされたファイルを読み込む
            df = pd.read_csv(uploaded_file, encoding='utf-8')
            st.session_state.karuta = Karuta(df)
        else:
            # デフォルトのデータを使用
            default_data = pd.read_csv('data/scripts.csv', encoding='utf-8')
            st.session_state.karuta = Karuta(default_data)

    karuta = st.session_state.karuta

    # ボタンレイアウト
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button('あたらしい　よみふだ'):
            hiragana, yomifuda = karuta.select_yomifuda()
            st.session_state.display_text['hiragana'] = hiragana
            st.session_state.display_text['yomifuda'] = yomifuda
            st.rerun()

    with col2:
        if st.button('もういちど　よむ'):
            karuta.read_out_script()

    with col3:
        if st.button('リセット'):
            karuta.reset_scripts()
            st.session_state.display_text = {'hiragana': '', 'yomifuda': ''}
            st.rerun()

    # 残りの札数を表示
    if st.session_state.display_text['hiragana']:
        st.write(f"のこり: {len(karuta.scripts)}")

    st.markdown('---')

    # ひらがなの表示（読み札の前に表示）
    if st.session_state.display_text['hiragana']:
        st.markdown(f"# {st.session_state.display_text['hiragana']}")

    # 読み札を最後に表示
    if st.session_state.display_text['yomifuda']:
        st.markdown(f"### {st.session_state.display_text['yomifuda']}")

if __name__ == '__main__':
    main()