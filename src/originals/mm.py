import streamlit as st
from google import genai
from google.genai import types

# 1. API Key update: Use an empty string for the canvas environment.
# In a real Streamlit app, use: api_key = st.secrets["GEMINI_API_KEY"]
api_key = ""

# Sidebar: API key & settings
with st.sidebar:
    st.markdown("## Options")
    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = [{"role": "model", "content": "Hi! I'm Gemini. Ask me anything!"}]
        st.rerun()

# Initialize client
# The client automatically handles the API key when passed as an empty string in this environment.
client = genai.Client(api_key=api_key)

# App UI
st.title("Gemini Chat AI")
st.caption("Powered by Google GenAI SDK + Streamlit • **Real-time Streaming Enabled**")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "content": "Hi! I'm Gemini. Ask me anything!"}
    ]

# Display history
# Note: Streamlit's st.chat_message maps 'model' to 'assistant' for the icon.
for msg in st.session_state.messages:
    with st.chat_message(msg["role"] if msg["role"] != "model" else "assistant"):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Stream response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            # 2. **Implement History and Streaming**

            # Convert Streamlit's simple history format into the SDK's expected Content/Part format
            contents = []
            for m in st.session_state.messages:
                # Map Streamlit role ('user', 'model') to the SDK's role ('user', 'model')
                role = m['role'] if m['role'] != 'assistant' else 'model'
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=m['content'])]
                    )
                )

            # Use generate_content_stream for real-time output
            response_stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=contents,  # Pass the entire conversation history
            )

            # Iterate through the stream and update the placeholder
            for chunk in response_stream:
                full_response += chunk.text
                # Display the partial response with a cursor effect
                placeholder.markdown(full_response + "▌")

            # Final display without the cursor
            placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Error: {type(e).__name__} - {str(e)}")
            full_response = "Sorry, something went wrong. Try again!"

    # Save assistant response
    # Use 'model' role, which Streamlit correctly displays as 'assistant' icon
    st.session_state.messages.append({"role": "model", "content": full_response})