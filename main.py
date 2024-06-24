import streamlit as st
from ai_assistant import AIAssistant
from api_utils import AnthropicAPIError
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from agent import Agent

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def verify_tavily_api_key():
    return Agent.verify_tavily_api_key()

def main():
    st.title("AI Assistant with Mixture of Agents and Tree of Thought")

    if not verify_tavily_api_key():
        st.error("Failed to verify Tavily API key. Please check your .env file and try again.")
        st.stop()

    initialize_session_state()

def initialize_session_state():
    if 'assistant' not in st.session_state:
        st.session_state.assistant = AIAssistant()
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    if 'follow_up' not in st.session_state:
        st.session_state.follow_up = False

def display_conversation():
    for i, message in enumerate(st.session_state.conversation):
        if message["role"] == "user":
            st.text_area("You:", value=message["content"], height=100, key=f"user_{i}", disabled=True)
        else:
            st.text_area("Assistant:", value=message["content"], height=200, key=f"assistant_{i}")

def main():
    st.title("AI Assistant with Mixture of Agents and Tree of Thought")

    if not verify_tavily_api_key():
        st.stop()

    initialize_session_state()

    if not st.session_state.follow_up:
        user_input = st.text_input("You: ", key="user_input")
    else:
        user_input = st.text_area("Follow-up question or additional context:", key="follow_up_input", height=100)

    if st.button("Send"):
        st.session_state.conversation.append({"role": "user", "content": user_input})
        
        try:
            with st.spinner("Thinking..."):
                response = st.session_state.assistant.respond(user_input)
            st.session_state.conversation.append({"role": "assistant", "content": response})
            st.session_state.follow_up = True
        
        except AnthropicAPIError as e:
            st.error(f"An error occurred while processing your request: {str(e)}")
            logger.error(f"Error in assistant response: {str(e)}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            logger.exception("Unexpected error in Streamlit UI")

    display_conversation()

    if st.button("Clear Conversation"):
        st.session_state.conversation = []
        st.session_state.assistant = AIAssistant()
        st.session_state.follow_up = False

    st.info("Note: The assistant's responses are displayed in editable text areas for easy copying, but edits are not saved or processed.")

if __name__ == "__main__":
    main()