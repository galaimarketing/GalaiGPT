import openai
import streamlit as st
import json
import google_serp
import prompts
import blog_posts
import tokens_count

# Set Streamlit configuration as the first command
st.set_page_config(
    page_title="GalaiGPT | BETA",
    page_icon="🤖",
)

# Initialize OpenAI API key
api_key = None

# Check if secret key is provided in the sidebar
st.sidebar.header("Settings")
st.sidebar.markdown("[GET YOUR SECRET KEY](https://platform.openai.com/account/api-keys)")
secret_key = st.sidebar.text_input("Enter Secret Key Here ↓")

# Check if secret key is provided and set OpenAI API key
if secret_key:
    api_key = secret_key
    openai.api_key = api_key

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
temperature_default = settings.get("temperature", 0.7)
top_p_default = settings.get("top_p", 1.0)
model_default = settings.get("model", "gpt-3.5-turbo")

show_token_cost = True

# Initialize temperature and other variables before the API key check
temperature = st.sidebar.slider("Temperature", 0.1, 1.0, temperature_default)
top_p = st.sidebar.slider("Top P", 0.1, 1.0, top_p_default)
model = st.sidebar.selectbox(
    "Model",
    ["gpt-3.5-turbo", "gpt-4", "gpt-3.5-turbo-16k"],
    index=0 if model_default == "gpt-3.5-turbo" else 1,
)

# Check if neither API key nor secret key is provided
if not (api_key or secret_key):
    st.error("Please enter a valid OpenAI API key or secret key to use GalaiGPT. 🔑")
    st.markdown("[GET YOURS FROM HERE 😊👍](https://platform.openai.com/account/api-keys)")
    st.stop()

# Update settings with the new values
settings.update(
    {
        "api_key": api_key,
        "show_token_cost": show_token_cost,
        "temperature": temperature,
        "top_p": top_p,
        "model": model,
    }
)
save_settings(settings)

# Initialize the chat messages
if "cumulative_tokens" not in st.session_state:
    st.session_state.cumulative_tokens = 0
if "cumulative_cost" not in st.session_state:
    st.session_state.cumulative_cost = 0

st.title("GalaiGPT 🤖")
st.write("Hello there! I'm GalaiGPT, Your AI-powered Marketing Assistant! 🎯 Think of me as your go-to resource for all things marketing-related. From inspiring you with content ideas for social media to strategizing effective ad campaigns, I'm here to assist you in every step along the way. 😊 Say Thanks to [Galai Ala](https://galaiala.web.app) Who Trained Me! 👦‍💻")

# Store chat messages in a list
chat_messages = []

# Display chat messages
for message in chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Ask me anything about marketing"):
    start_prompt_used = ""

    # Check for "/reset" command from the user
    if prompt.strip().lower() == "/reset":
        chat_messages = []  # Clear the conversation
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
    else:
        # Handle other user commands (e.g., /summarize, /rewrite, /google)
        if prompt.strip().lower().startswith("/summarize"):
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
                chat_messages.append({"role": "assistant", "content": blog_summary})

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
                chat_messages.append({"role": "assistant", "content": new_written_text})

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
                chat_messages.append({"role": "assistant", "content": research_final + source_links})

        else:
            # Handle regular user input
            with st.chat_message("user"):
                st.markdown(prompt)
            chat_messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("GalaiGPT")
                # Send the user input to OpenAI and get a response
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful and professional marketing assistant named GalaiGPT. You are capable of excelling in various tasks, including crafting engaging content ideas for social media platforms, writing compelling descriptions for products or services, writing effective ad copies, providing guidance on running successful ad campaigns, and developing winning marketing strategies. Your answers depend on the user needs. You reply in a human-friendly way.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                )
                # Get the generated response from OpenAI
                ai_message = response.choices[0].message["content"].strip()
                st.write(ai_message)

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

st.session_state.chat_messages = chat_messages
