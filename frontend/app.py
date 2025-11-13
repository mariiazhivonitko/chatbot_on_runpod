import streamlit as st
import requests

system_prompt = """### Instruction:
You are CyThIA, an expert cybersecurity assistant. 
Your task is to provide clear, accurate, and logical answers to cybersecurity-related questions. 
Focus on correctness and clarity.

### Input:
{user_question}

### Response:
"""

st.set_page_config(page_title="CyThIA Chatbot")
st.title("CyThIA Chatbot")

API_URL = "https://qf7v1l7ujtvff9-8501.proxy.runpod.net/chat"
MODEL_NAME = "CyThIA-Llama3"

# --- Button to form for users' feedback ---
st.link_button("feedback", "https://e5fgg25x.forms.app/spa-feedback-form", help=None, type="primary", icon=None, disabled=False, use_container_width=None, width="content")

# --- Initialize chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display chat history ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat input ---
if prompt := st.chat_input("Ask me anything about cyber security..."):
    # Append user message first
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare the formatted prompt
    formatted_prompt = system_prompt.format(user_question=prompt)


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

        # Feedback stars
        sentiment_mapping = ["one", "two", "three", "four", "five"]
        selected = st.feedback("stars")
        if selected is not None:
            st.markdown(f"You selected {sentiment_mapping[selected]} star(s).")


    # Append assistant message after rendering
    st.session_state.messages.append({"role": "assistant", "content": response})

   
