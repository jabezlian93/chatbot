import streamlit as st
from openai import OpenAI

st.title("💬 Assistant Chatbot")

openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    if "thread_id" not in st.session_state:
        # Ein neuer Thread für die Unterhaltung
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    # Vergangene Nachrichten anzeigen
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Frag mich etwas..."):
        # User-Nachricht speichern
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Nachricht an den Assistant schicken
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt,
        )

        # Assistant laufen lassen
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id="asst_1CF4BN4xt2iQSwBe6WTJZTyx",  # deine ID einsetzen
        )

        # Warten, bis er fertig ist (polling)
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break

        # Antwort auslesen
        messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        assistant_msg = messages.data[0].content[0].text.value

        # Im Chat anzeigen
        with st.chat_message("assistant"):
            st.markdown(assistant_msg)

        st.session_state.messages.append({"role": "assistant", "content": assistant_msg})

