import openai
import streamlit as st
import json
import google_serp
import prompts
import blog_posts
import tokens_count
import os

# Set Streamlit configuration
st.set_page_config(
    page_title="GalaiGPT | BETA",
    page_icon="🤖",
)


hide_streamlit_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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

st.sidebar.markdown("[FIND YOUR SECRET KEY 🔽](https://platform.openai.com/account/api-keys)")


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

if "cumulative_tokens" not in st.session_state:
    st.session_state.cumulative_tokens = 0
if "cumulative_cost" not in st.session_state:
    st.session_state.cumulative_cost = 0

st.title("GalaiGPT 🤖")
st.write(" Your AI-powered marketing assistant! 🎯")

# Set the API key if it's provided
if api_key:
    openai.api_key = api_key
else:
    st.markdown("[FIND YOUR SECRET KEY TO START](https://platform.openai.com/account/api-keys)")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initialize a boolean variable to track whether the introduction has been sent
if "introduced" not in st.session_state:
    st.session_state.introduced = False

if not st.session_state.introduced:
    # Define the introduction message
    introduction_message = """
    Here's how I can help in some marketing tasks:

    1.I'll craft engaging marketing content.
    2.I'll find SEO keywords for your website.
    3.I'll can create effective email marketing campaigns.
    4.I'll assist in running successful online ad campaigns.
    5.I'll develop a winning marketing strategy.

    Feel free to share your marketing goals or challenges. Together, we'll achieve success 🚀📈.

    I've been trained & developed by Galai Ala 👦‍💻 [https://galaiala.web.app]
    """

    # Append the introduction message to the chat
    st.session_state.messages.append({"role": "assistant", "content": introduction_message})


# Handle user input
if prompt := st.chat_input("Chat With Me"):
    start_prompt_used = ""

    # Check for "/reset" command from the user
    if prompt.strip().lower() == "/reset":
        st.session_state.messages = []  # Clear the conversation
        st.session_state.cumulative_tokens = 0  # Reset cumulative tokens
        st.session_state.cumulative_cost = 0  # Reset cumulative cost
        st.sidebar.markdown(
            f"**Total Tokens Used This Session:** {st.session_state.cumulative_tokens}"
        )
        st.sidebar.markdown(
            f"**Total Cost This Session:** ${st.session_state.cumulative_cost:.2f}"
        )
        st.write("Conversation and counters have been reset!")
        st.stop()  # Halts further execution for this run of the app

    # Handle other user commands (e.g., /summarize, /rewrite, /google)
    elif prompt.strip().lower().startswith("/summarize"):
        # Handle /summarize command
        blog_url = prompt.split(" ", 1)[1].strip()
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Summarizing: " + blog_url)
            blog_summary_prompt = blog_posts.get_blog_summary_prompt(blog_url)
            response_obj = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": blog_summary_prompt}],
                temperature=temperature,
                top_p=top_p,
                stream=True,
            )
            blog_summary = ""
            for response in response_obj:
                blog_summary += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(blog_summary + "▌")

            start_prompt_used = blog_summary_prompt + blog_summary

            message_placeholder.markdown(blog_summary)  # Display the summary in chat
            st.session_state.messages.append(
                {"role": "assistant", "content": blog_summary}
            )

    elif prompt.strip().lower().startswith("/rewrite"):
        # Handle /rewrite command
        input_text = prompt.split(" ", 1)[1].strip()
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Rewriting...")
            rewrite_prompt = prompts.rewrite_prompt(input_text)
            response_obj = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": rewrite_prompt}],
                temperature=temperature,
                top_p=top_p,
                stream=True,
            )
            new_written_text = ""
            for response in response_obj:
                new_written_text += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(new_written_text + "▌")

            start_prompt_used = rewrite_prompt + new_written_text

            message_placeholder.markdown(new_written_text)
            st.session_state.messages.append(
                {"role": "assistant", "content": new_written_text}
            )

    elif prompt.strip().lower().startswith("/google"):
        # Handle /google command
        input_query = prompt.split(" ", 1)[1].strip()
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown(
                "Searching Google For: " + input_query + " ..."
            )
            search_results = google_serp.search_google_web_automation(input_query)
            over_all_summary = ""

            source_links = "\n \n Sources: \n \n"

            for result in search_results:
                blog_url = result["url"]
                source_links += blog_url + "\n \n"
                message_placeholder.markdown(f"Search Done, Reading {blog_url}")
                blog_summary_prompt = blog_posts.get_blog_summary_prompt(blog_url)
                response_obj = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": blog_summary_prompt}],
                    temperature=temperature,
                    top_p=top_p,
                    stream=True,
                )

                blog_summary = ""
                for response in response_obj:
                    blog_summary += response.choices[0].delta.get("content", "")

                over_all_summary = over_all_summary + blog_summary
                start_prompt_used = blog_summary_prompt + blog_summary

            message_placeholder.markdown(f"Generating Final Search Report...")

            new_search_prompt = prompts.google_search_prompt(over_all_summary)

            response_obj = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": new_search_prompt}],
                temperature=temperature,
                top_p=top_p,
                stream=True,
            )
            research_final = ""
            for response in response_obj:
                research_final += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(research_final + "▌")

            start_prompt_used = start_prompt_used + new_search_prompt + research_final

            message_placeholder.markdown(research_final + source_links)
            st.session_state.messages.append(
                {"role": "assistant", "content": research_final + source_links}
            )

    else:
        # Handle regular user input
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            response_obj = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                temperature=temperature,
                top_p=top_p,
            )

            for response in response_obj:
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            start_prompt_used = prompt + full_response

            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

    if show_token_cost:
        total_tokens_used = tokens_count.count_tokens(start_prompt_used, model)
        total_cost = tokens_count.estimate_input_cost_optimized(
            model, total_tokens_used
        )
        st.session_state.cumulative_tokens += total_tokens_used
        st.session_state.cumulative_cost += total_cost

        # Redisplay the updated cumulative tokens and cost in the left sidebar
        st.sidebar.markdown(
            f"**Total Tokens Used This Session:** {st.session_state.cumulative_tokens}"
        )
        st.sidebar.markdown(
            f"**Total Cost This Session:** ${st.session_state.cumulative_cost:.6f}"
        )
