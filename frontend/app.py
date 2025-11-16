import streamlit as st
import requests

system_prompt = """You are CyThIA, a helpful and accurate cybersecurity assistant.

Rules:
- Give clear, correct cybersecurity answers using short paragraphs or bullet points.
- Do NOT repeat the same sentence, definition, or list within a response.
- Do NOT restart your answer after finishing it.
- Do NOT output multiple versions of the same answer.
- If the user asks a new question, answer it once, cleanly, and concisely.
- Never provide hacking or illegal instructions.
- Never invent tools, commands, or facts. If unsure, ask for clarification.
- Stay friendly, safe, practical, and beginner-focused.

Goal: give one complete, non-repetitive answer per user request.
"""


st.set_page_config(page_title="CyThIA Chatbot")
st.title("CyThIA Chatbot")

API_URL = "https://3s48yidawh6atm-8501.proxy.runpod.net/chat"
MODEL_NAME = "CyThIA-Mistral"

# --- Button to form for users' feedback ---
st.link_button("feedback", "https://e5fgg25x.forms.app/spa-feedback-form", help=None, type="primary", icon=None, disabled=False, use_container_width=None, width="content")

# --- Initialize chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""
if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# --- Display chat history ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat input ---
if prompt := st.chat_input("Ask me anything about cyber security..."):
    # Append user message first
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare the formatted prompt
    formatted_prompt = {
        "system_prompt": system_prompt,
        "user_message": prompt
    }


    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # Create assistant container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

        # Call backend API
        try:
            response_data = requests.post(
                f"{API_URL}/{MODEL_NAME}",
                json={"message": formatted_prompt},  # Simplified input
                timeout=120
            )
            response_data.raise_for_status()
            response = response_data.json().get("response", "No response received.")
        except requests.exceptions.RequestException:
            response = "The chatbot service is temporarily unavailable."

        # Update placeholder in-place
        message_placeholder.markdown(response)

    
    # Append assistant message after rendering
    st.session_state.messages.append({"role": "assistant", "content": response})

     # Feedback stars
sentiment_mapping = ["one", "two", "three", "four", "five"]
selected = st.feedback("faces")
if selected is not None:
    rating = selected + 1
    # Save feedback to backend FastAPI
    try:
        requests.post(
            f"{API_URL}/feedback",
            json={
                "question": st.session_state.last_prompt,
                "answer": st.session_state.last_response,
                "rating": rating
        },
            timeout=50
        )
        st.success(f"Thanks for your feedback!")
        # Clear last prompt/response so feedback can't be submitted twice
        st.session_state.last_prompt = ""
        st.session_state.last_response = ""
    except:
        st.warning("Couldn't send feedback to server.")
    


