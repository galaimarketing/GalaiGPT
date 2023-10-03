import openai
import streamlit as st
import json
import tokens_count

# Set Streamlit configuration as the first command
st.set_page_config(
    page_title="GalaiGPT | BETA",
    page_icon="🤖",
)

# Get the API key from Streamlit Secrets
api_key = st.secrets.get("OPENAI_API_KEY")

# Check if secret key is provided in the sidebar
st.sidebar.header("Settings")
st.sidebar.markdown("[GET YOUR SECRET KEY](https://platform.openai.com/account/api-keys)")
secret_key = st.sidebar.text_input("Enter Secret Key Here ↓")

# Check if secret key is provided and set OpenAI API key
if secret_key:
    api_key = secret_key
    openai.api_key = api_key

# Check if neither API key nor secret key is provided
if not (api_key or secret_key):
    st.error("Please enter a valid OpenAI API key or secret key to use GalaiGPT. 🔑")
    st.markdown("[GET YOURS FROM HERE 😊👍](https://platform.openai.com/account/api-keys)")
    st.stop()

# Initialize the chat history
chat_history = []

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

# Handle user input
if prompt := st.text_input("Ask me anything about marketing"):
    start_prompt_used = ""

    # Check for "/reset" command from the user
    if prompt.strip().lower() == "/reset":
        chat_history = []  # Clear the conversation history
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
        # Append the user's message to the chat history
        chat_history.append({"role": "user", "content": prompt})

        try:
            # Include the entire chat history in the input messages
            messages = [{"role": message["role"], "content": message["content"]} for message in chat_history]
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
            )
            # Get the generated response from OpenAI
            ai_message = response.choices[0].message["content"].strip()

            # Append the assistant's message to the chat history
            chat_history.append({"role": "assistant", "content": ai_message})

            st.write(ai_message)
        except openai.error.AuthenticationError as e:
            st.error("Authentication failed. Please check your API key and try again.")

        if show_token_cost:
            # Calculate token usage and cost based on the entire conversation history
            total_tokens_used = tokens_count.count_tokens(" ".join([message["content"] for message in chat_history]), model)
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
