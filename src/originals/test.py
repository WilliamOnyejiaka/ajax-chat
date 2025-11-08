import streamlit as st
from google import genai
from google.genai import types

# Use an empty string for the API key in this canvas environment.
api_key = ""

# Initialize client
client = genai.Client(api_key=api_key)

# --- State Initialization ---
# Initialize chat history (current session)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "content": "Hi! I'm Ajax, a rizz god Ask me anything!"}
    ]
# Initialize past chat storage
if "past_chats" not in st.session_state:
    st.session_state.past_chats = []
# Initialize a title for the current chat session
if "current_chat_title" not in st.session_state:
    st.session_state.current_chat_title = "New Chat"


def start_new_chat():
    """Saves the current chat to history and resets the state."""

    # 1. Check if the current chat is worth saving (i.e., has more than just the initial greeting)
    if len(st.session_state.messages) > 1:
        # Create a title from the first user message
        first_user_message = next((m for m in st.session_state.messages if m["role"] == "user"), None)
        title = first_user_message["content"][:30].strip() + "..." if first_user_message else "Untitled Chat"

        # Save the current chat messages and its title
        st.session_state.past_chats.append({
            "title": title,
            "messages": st.session_state.messages.copy()
        })

    # 2. Reset the current chat state
    st.session_state.messages = [{"role": "model", "content": "Hi! I'm Gemini. Ask me anything!"}]
    st.session_state.current_chat_title = "New Chat"
    st.rerun()


def load_past_chat(chat_index):
    """Loads a chat from history, sets it as current, and saves the old one if needed."""

    # 1. Save the *current* chat before loading a new one (similar to start_new_chat)
    if len(st.session_state.messages) > 1:
        first_user_message = next((m for m in st.session_state.messages if m["role"] == "user"), None)
        title = first_user_message["content"][:30].strip() + "..." if first_user_message else "Untitled Chat"

        # Check if this chat is already saved to avoid duplicates when switching back and forth
        is_saved = any(c['messages'] == st.session_state.messages for c in st.session_state.past_chats)
        if not is_saved:
            st.session_state.past_chats.append({
                "title": title,
                "messages": st.session_state.messages.copy()
            })

    # 2. Load the requested past chat
    chat_to_load = st.session_state.past_chats.pop(chat_index)
    st.session_state.messages = chat_to_load["messages"]
    st.session_state.current_chat_title = chat_to_load["title"]

    st.rerun()


# --- Sidebar: History & Settings ---
with st.sidebar:
    st.markdown("## Current Session")
    # Button to start a new chat
    if st.button("➕ Start New Chat", use_container_width=True):
        start_new_chat()

    st.markdown("---")
    st.markdown("## Chat History")

    # Display past chats in reverse order (most recent first)
    if st.session_state.past_chats:
        # We iterate over a copy of the list and use indices for loading
        for i, chat in enumerate(st.session_state.past_chats):
            # Using a temporary title for display clarity
            display_title = chat["title"]

            # Use st.columns to put the title and a load button side-by-side
            col1, col2 = st.columns([4, 2])
            with col1:
                st.markdown(f"**{display_title}**", )
            with col2:
                if st.button("Load", key=f"load_{i}"):
                    load_past_chat(i)
    else:
        st.info("No past chats saved yet.")

# --- App UI ---
st.title("Gemini Chat AI")
st.caption(f"Powered by Google GenAI SDK + Streamlit • **Session: {st.session_state.current_chat_title}**")

# Display history
for msg in st.session_state.messages:
    # Map 'model' role to 'assistant' for the Streamlit icon
    with st.chat_message(msg["role"] if msg["role"] != "model" else "assistant"):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    # If this is the first user message, set the chat title
    if st.session_state.current_chat_title == "New Chat":
        st.session_state.current_chat_title = prompt[:30].strip() + "..."

    with st.chat_message("user"):
        st.markdown(prompt)

    # Stream response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
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
    st.session_state.messages.append({"role": "model", "content": full_response})