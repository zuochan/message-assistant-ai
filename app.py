import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from gtts import gTTS
import io
import json 
import uuid
import base64




# Set up OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def section_title(title, emoji="✨", color="#f0f8ff"):
    st.markdown(f"""
    <div style="background-color:{color}; padding:10px 15px; border-radius:8px; margin-top:20px; margin-bottom:10px;">
        <h4 style="margin:0;">{emoji} {title}</h4>
    </div>
    """, unsafe_allow_html=True)
    
def audio_to_base64(audio_bytes: bytes) -> str:
    return base64.b64encode(audio_bytes).decode("utf-8")
# --- result_card 関数内の修正 ---
def result_card(title, content, audio_bytes=None, bg="#ffffff"):
    copy_id = f"copy_{uuid.uuid4().hex}"
    escaped = json.dumps(content)
    
    audio_html = ""

    if audio_bytes:
        base64_audio = audio_to_base64(audio_bytes)
        audio_html = f"""
        <audio controls style="margin-top:10px; width: 100%;">
            <source src="data:audio/mp3;base64,{base64_audio}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """

    html_code = f"""
    <div style="
        background-color: {bg};
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        position: relative;
        font-family: system-ui;
    ">
        <strong style="font-size: 12px; font-weight: 600; color: #333;">{title}</strong>

        <pre id="{copy_id}" style="
                white-space: pre-wrap;
                font-family: system-ui, sans-serif;
                max-height: 150px;            /* 最大高さを指定 */
                overflow-y: auto;            /* 高さ超過時にスクロールバー表示 */
                padding-right: 8px;           /* スクロールバーによる文字切れ防止 */
                ">{content}</pre>
        <button onclick="copyToClipboard('{copy_id}')" style="
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: #f0f0f0;
            color: #333;
            padding: 4px 8px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 10px;
        ">📋 Copy</button>
        {audio_html}
    </div>

    <script>
    function copyToClipboard(id) {{
        var text = document.getElementById(id).innerText;
        navigator.clipboard.writeText(text).then(function() {{
            var btn = document.querySelector("button[onclick*='" + id + "']");
            btn.innerText = "✅ Copied!";
            setTimeout(() => {{
                btn.innerText = "📋 Copy";
            }}, 1500);
        }});
    }}
    </script>
    """

    components.html(html_code, height=320)
    
# Streamlitのページ設定
st.set_page_config(page_title="Message Assistant AI")
st.title("💬 Message Assistant AI")
st.markdown("Polish your English messages and generate better replies with AI.")

# --- Section 1: Message Polishing ---
section_title("Improve Your Message", emoji="✏️", color="#e6f7ff")

# 2カラム作成
col1, col2 = st.columns(2)

with col1:
    user_input = st.text_area("Write your English message here:", height=200)
    tone = st.selectbox("Choose tone for correction:", ["Natural", "Polite", "Casual", "Friendly", "Professional"])

with col1:
    if st.button("Improve Message"):
        if not user_input.strip():
            st.warning("Please write something to improve.")
        else:
            with st.spinner("Improving your message..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo", 
                    messages=[
                        {"role": "system", "content": "You are an English writing assistant."},
                        {"role": "user", "content": f"Please improve this message in a {tone.lower()} tone:\n\n{user_input}"}
                    ]
                )
                result = response.choices[0].message.content.strip()
                st.session_state["improved_message"] = result  # ✅ セッションに保存

# 改善メッセージがある場合のみ表示
with col2:
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    if "improved_message" in st.session_state:
        
        # 音声読み上げ用のMP3生成
        tts = gTTS(text=st.session_state["improved_message"], lang='en')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        mp3_bytes = mp3_fp.read()
        
        result_card("✅ Improved Message", st.session_state["improved_message"], audio_bytes=mp3_bytes, bg="#fefefe")
        

    # 翻訳機能（改善メッセージ翻訳）
    if "improved_message" in st.session_state:
        if st.button("🔁 Translate to Japanese", key="translate_improved"):
            with st.spinner("Translating..."):
                translation = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a translator who translates English into natural Japanese."},
                        {"role": "user", "content": f"Translate this message into Japanese:\n\n{st.session_state['improved_message']}"}
                    ]
                )
                st.session_state["translated_improved"] = translation.choices[0].message.content.strip()

        if "translated_improved" in st.session_state:
            st.info(st.session_state["translated_improved"])

# --- Separator ---
st.markdown("---")

# --- Section 2: Reply Generator ---
section_title("Generate Reply Suggestions", emoji="💌", color="#fff0f6")

# 2カラム作成
col3, col4 = st.columns(2)

with col3:
    partner_message = st.text_area("📩 Paste the message you received (in English):", height=200)
    reply_tone = st.selectbox("Choose reply tone:", ["Natural", "Polite", "Casual", "Friendly", "Professional"])

with col3:
    if st.button("Suggest Reply"):
        if not partner_message.strip():
            st.warning("Please paste a message to respond to.")
        else:
            with st.spinner("Generating reply..."):
                prompt = (
                    f"Imagine you're replying to the following message in a {reply_tone.lower()} tone:\n"
                    f"{partner_message}\n"
                    "Generate a reply as if you were my friend."
                )
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful English communication assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                replies = response.choices[0].message.content.strip()
                st.session_state["reply_suggestions"] = replies  # ✅ セッションに保存
with col4:
    if "reply_suggestions" in st.session_state:
        result_card("✨ Suggested Replies", st.session_state["reply_suggestions"], bg="#fefefe")
        
        # 音声読み上げ用のMP3生成
        tts = gTTS(text=st.session_state["reply_suggestions"], lang='en')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        # 音声再生ボタン
        st.audio(mp3_fp, format="audio/mp3")

# 翻訳機能（返信候補翻訳）
if "reply_suggestions" in st.session_state:
    if st.button("🔁 Translate replies to Japanese", key="translate_replies"):
        with st.spinner("Translating..."):
            translation = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a translator who translates English into natural Japanese."},
                    {"role": "user", "content": f"Translate this message into Japanese:\n\n{st.session_state['reply_suggestions']}"}
                ]
            )
            st.session_state["translated_replies"] = translation.choices[0].message.content.strip()

    if "translated_replies" in st.session_state:
        st.markdown("#### 🌐 Japanese Translation")
        st.info(st.session_state["translated_replies"])