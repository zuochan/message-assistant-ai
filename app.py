import streamlit as st
from openai import OpenAI

# Set up OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Message Assistant AI")
st.title("💬 Message Assistant AI")
st.markdown("Polish your English messages and generate better replies with AI.")

# --- Section 1: Message Polishing ---
st.header("✏️ Improve Your Message")

user_input = st.text_area("Write your English message here:", height=200)

tone = st.selectbox("Choose tone for correction:", ["Natural", "Formal", "Casual"])

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
            st.success("✅ Improved Message:")
            st.text_area("Result", result, height=200)

# --- Separator ---
st.markdown("---")

# --- Section 2: Reply Generator ---
st.header("💌 Generate Reply Suggestions")

partner_message = st.text_area("📩 Paste the message you received (in English):", height=200)

reply_tone = st.selectbox("Choose reply tone:", ["Polite", "Casual", "Friendly", "Professional"])

if st.button("Suggest Reply"):
    if not partner_message.strip():
        st.warning("Please paste a message to respond to.")
    else:
        with st.spinner("Generating reply..."):
            prompt = (
                f"Imagine you're replying to the following message in a {reply_tone.lower()} tone:\n"
                f"{partner_message}\n"
                "Generate 3 different replies in bullet point format."
            )
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful English communication assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            replies = response.choices[0].message.content.strip()
            st.markdown("### ✨ Suggested Replies")
            st.markdown(replies)

