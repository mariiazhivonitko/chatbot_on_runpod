import streamlit as st
import requests

st.set_page_config(page_title="CyThIA Chatbot")
st.title("💬 CyThIA Chatbot")

# --- Backend API URL ---
API_URL = "https://0k7fokvy2dvubs-8501.proxy.runpod.net/chat"
MODEL_NAME = "CyThIA-Mistral"  # only single model for now

# --- Session state for chat messages ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display chat history ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



# --- Chat input ---
if prompt := st.chat_input("Ask me..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Append user message
    with st.chat_message("user"):
        st.markdown(prompt)
        

    # Construct final prompt
    final_prompt = f"""### Instruction:
    {prompt}

    ### Response:
    """  

    # Create a placeholder for the assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤖 Thinking...")

        # Send request to backend
        try:
            response_data = requests.post(
                f"{API_URL}/{MODEL_NAME}",
                json={"message": prompt},
                timeout=120  # wait max 2 minutes
            )
            response_data.raise_for_status()
            response = response_data.json().get("response", "No response received.")
        except requests.exceptions.RequestException as e:
            response = f"The chatbot service is temporarily unavailable."

        # Replace placeholder with actual response
        message_placeholder.markdown(response)

    # Save assistant message in chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
