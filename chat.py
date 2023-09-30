import openai
import streamlit as st
import json
import google_serp
import prompts
import blog_posts
import tokens_count
import os

# Set page configuration
st.set_page_config(
    page_title="GalaiGPT",
    page_icon="🤖",
)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Define functions to interact with the JSON file
def load_settings():
    try:
        with open("settings.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_settings(settings):
    with open("settings.json", "w") as file:
        json.dump(settings, file, indent=4)

# Load settings or use default values if not found
settings = load_settings()

show_token_cost_default = settings.get("show_token_cost", False)
api_key_default = settings.get("api_key", "")
temperature_default = settings.get("temperature", 0.7)
top_p_default = settings.get("top_p", 1.0)
model_default = settings.get("model", "gpt-3.5-turbo")

# Sidebar settings
st.sidebar.header("Settings")

show_token_cost = True

api_key = st.sidebar.text_input("Secret Key", api_key_default)
temperature = st.sidebar.slider("Temperature", 0.1, 1.0, temperature_default)
top_p = st.sidebar.slider("Top P", 0.1, 1.0, top_p_default)
model = st.sidebar.selectbox(
    "Model",
    ["gpt-3.5-turbo", "gpt-4", "gpt-3.5-turbo-16k"],
    index=0 if model_default == "gpt-3.5-turbo" else 1,
)

# Update settings with the new values
settings.update(
    {
        "show_token_cost": show_token_cost,
        "api_key": api_key,
        "temperature": temperature,
        "top_p": top_p,
        "model": model,
    }
)
save_settings(settings)

# Initialize session state variables
if "cumulative_tokens" not in st.session_state:
    st.session_state.cumulative_tokens = 0
if "cumulative_cost" not in st.session_state:
    st.session_state.cumulative_cost = 0

st.title("GalaiGPT")
st.write("Your Personal AI Marketing Assistant, Always Ready to Help 🚀")

# Set the API key if it's provided
if api_key:
    openai.api_key = api_key
else:
    st.warning("Please provide a valid Secret Key.")
    st.stop()

# Initialize chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Introduction message
if not st.session_state.get("introduced", False):
    introduction_message = prompts.introduction_prompt
    st.session_state.messages.append({"role": "assistant", "content": introduction_message})
    st.session_state.introduced = True

# Chat input
if prompt := st.text_input("You:", key="input"):
    start_prompt_used = ""

    # Check for "/reset" command from the user
    if prompt.strip().lower() == "/reset":
        st.session_state.messages = []  # Clear the conversation
        st.session_state.cumulative_tokens = 0  # Reset cumulative tokens
        st.session_state.cumulative_cost = 0  # Reset cumulative cost
        st.write("Conversation and counters have been reset!")

    else:
        # Handle other user commands and inputs
        if prompt.strip().lower().startswith("/summarize"):
            # Handle /summarize command
            blog_url = prompt.split(" ", 1)[1].strip()
            blog_summary = blog_posts.get_blog_summary_prompt(blog_url)
            start_prompt_used = blog_summary

        elif prompt.strip().lower().startswith("/rewrite"):
            # Handle /rewrite command
            input_text = prompt.split(" ", 1)[1].strip()
            rewritten_text = prompts.rewrite_prompt.format(text=input_text)
            start_prompt_used = rewritten_text

        elif prompt.strip().lower().startswith("/google"):
            # Handle /google command
            input_query = prompt.split(" ", 1)[1].strip()
            search_results = google_serp.search_google_web_automation(input_query)
            start_prompt_used = search_results

        else:
            # Handle regular user input
            response = prompts.generate_response(prompt, st.session_state.messages)
            start_prompt_used = response

        # Display the response
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": start_prompt_used})
        st.text("Assistant:", start_prompt_used)

        if show_token_cost:
            total_tokens_used = tokens_count.count_tokens(start_prompt_used, model)
            total_cost = tokens_count.estimate_input_cost_optimized(model, total_tokens_used)
            st.session_state.cumulative_tokens += total_tokens_used
            st.session_state.cumulative_cost += total_cost

            # Display the updated cumulative tokens and cost
            st.sidebar.markdown(
                f"**Total Tokens Used This Session:** {st.session_state.cumulative_tokens}"
            )
            st.sidebar.markdown(
                f"**Total Cost This Session:** ${st.session_state.cumulative_cost:.6f}"
            )
