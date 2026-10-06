import streamlit as st
import ollama
from pypdf import PdfReader

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="AI Student Chatbot",
    page_icon="🎓",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #777;
    margin-bottom: 25px;
}

.card {
    padding: 20px;
    border-radius: 15px;
    background: #f7f9fc;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}

.history-card {
    padding: 15px;
    border-radius: 12px;
    background: #f5f7fb;
    border-left: 5px solid #4f46e5;
    margin-bottom: 12px;
}

.stat-box {
    text-align: center;
    padding: 15px;
    border-radius: 12px;
    background: #f7f9fc;
    border: 1px solid #e5e7eb;
}

</style>
""", unsafe_allow_html=True)


# ---------------- TITLE ----------------
st.markdown(
    '<div class="main-title">🎓 AI Student Chatbot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Your intelligent AI-powered study assistant</div>',
    unsafe_allow_html=True
)


# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "document_text" not in st.session_state:
    st.session_state.document_text = ""

if "file_name" not in st.session_state:
    st.session_state.file_name = ""


# ---------------- SIDEBAR ----------------
with st.sidebar:

    st.header("📚 Student Assistant")

    st.divider()

    subject = st.selectbox(
        "📖 Select Subject",
        [
            "General Knowledge",
            "AI & ML",
            "Python",
            "Java",
            "DBMS",
            "Computer Networks"
        ]
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "📄 Upload Study Notes",
        type=["pdf", "txt"]
    )

    if uploaded_file:

        if uploaded_file.name != st.session_state.file_name:

            if uploaded_file.name.endswith(".pdf"):

                reader = PdfReader(uploaded_file)

                text = ""

                for page in reader.pages:
                    text += page.extract_text() or ""

                st.session_state.document_text = text

            else:

                st.session_state.document_text = (
                    uploaded_file.read().decode("utf-8")
                )

            st.session_state.file_name = uploaded_file.name

        st.success("✅ Notes uploaded!")

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):

        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.info(
        "💡 Tip: Upload your notes and ask questions from them!"
    )


# ---------------- TABS ----------------
tab1, tab2 = st.tabs(
    ["💬 Chat", "🕘 Chat History"]
)


# ==================================================
# CHAT TAB
# ==================================================

with tab1:

    # ---------------- TOP STATS ----------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="stat-box">
            <h3>📚 Subject</h3>
            <b>{subject}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="stat-box">
            <h3>💬 Questions</h3>
            <b>{len(st.session_state.messages) // 2}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        if st.session_state.document_text:
            status = "✅ Notes Ready"
        else:
            status = "📄 No Notes"

        st.markdown(
            f"""
            <div class="stat-box">
            <h3>📄 Notes</h3>
            <b>{status}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # ---------------- WELCOME MESSAGE ----------------
    if not st.session_state.messages:

        st.markdown(
            """
            <div class="card">

            ### 👋 Welcome to your AI Study Assistant!

            Ask me anything about your studies.

            **You can:**
            - 📖 Ask subject questions
            - 📄 Upload PDF study notes
            - 🧠 Get simple explanations
            - 💡 Ask for examples
            - 📝 Prepare for exams

            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------- DISPLAY CHAT ----------------
    for message in st.session_state.messages:

        with st.chat_message(
            message["role"],
            avatar="👩‍🎓" if message["role"] == "user" else "🤖"
        ):

            st.markdown(message["content"])


    # ---------------- CHAT INPUT ----------------
    question = st.chat_input(
        "💬 Ask your study question..."
    )


    if question:

        # Save user question
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        # Display user question
        with st.chat_message(
            "user",
            avatar="👩‍🎓"
        ):
            st.write(question)


        # ---------------- AI PROMPT ----------------
        if st.session_state.document_text:

            prompt = f"""
You are an AI Student Assistant.

Subject: {subject}

Use the uploaded study notes when relevant.

Study Notes:
{st.session_state.document_text}

Student Question:
{question}

Instructions:
- Explain clearly and simply.
- Use easy student-friendly language.
- Give examples when useful.
- If the answer is present in the notes, prioritize the notes.
- Do not make the answer unnecessarily complicated.
"""

        else:

            prompt = f"""
You are an AI Student Assistant.

Subject: {subject}

Student Question:
{question}

Instructions:
- Explain the topic clearly.
- Use simple student-friendly language.
- Give examples when useful.
- For programming questions, provide simple code.
- For exam questions, give a structured answer.
"""


        # ---------------- AI RESPONSE ----------------
        with st.chat_message(
            "assistant",
            avatar="🤖"
        ):

            with st.spinner("🤖 AI is thinking..."):

                try:

                    response = ollama.chat(
                        model="llama3.2:3b",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    )

                    answer = response["message"]["content"]

                    st.markdown(answer)

                except Exception as e:

                    answer = (
                        "❌ Unable to connect to Ollama. "
                        "Please make sure Ollama is running."
                    )

                    st.error(answer)

        # Save AI response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


# ==================================================
# CHAT HISTORY TAB
# ==================================================

with tab2:

    st.subheader("🕘 Chat History")

    if not st.session_state.messages:

        st.info(
            "💬 No chat history yet. Start asking questions!"
        )

    else:

        # Count questions
        question_count = len(
            [
                m for m in st.session_state.messages
                if m["role"] == "user"
            ]
        )

        st.success(
            f"📊 You have asked {question_count} question(s)."
        )

        st.divider()

        # Display history
        for i, message in enumerate(
            st.session_state.messages
        ):

            if message["role"] == "user":

                st.markdown(
                    f"""
                    <div class="history-card">

                    <b>👩‍🎓 Question {i + 1}</b>

                    <p>{message["content"]}</p>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                with st.expander("🤖 AI Answer"):

                    st.write(
                        message["content"]
                    )


        # ---------------- DOWNLOAD HISTORY ----------------
        st.divider()

        history_text = ""

        for message in st.session_state.messages:

            if message["role"] == "user":

                history_text += (
                    "\n👩‍🎓 QUESTION:\n"
                    + message["content"]
                    + "\n\n"
                )

            else:

                history_text += (
                    "🤖 AI ANSWER:\n"
                    + message["content"]
                    + "\n"
                    + "-" * 50
                    + "\n"
                )


        st.download_button(
            label="📥 Download Chat History",
            data=history_text,
            file_name="chat_history.txt",
            mime="text/plain",
            use_container_width=True
        )