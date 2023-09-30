import openai
import streamlit as st
import json
import blog_posts
import prompts
import tokens_count
import os
from selenium import webdriver
from selenium_stealth import stealth
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from webdriver_manager.chrome import ChromeDriverManager

# ... (rest of the code remains the same)

def search_google(query, model, temperature, top_p):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Use ChromeDriverManager to automatically download and manage chromedriver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Linux",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    n_pages = 5
    results = []
    counter = 0
    for page in range(1, n_pages):
        url = (
            "http://www.google.com/search?q="
            + str(query)
            + "&start="
            + str((page - 1) * 10)
        )

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        search = soup.find_all("div", class_="yuRUbf")
        for h in search:
            counter = counter + 1
            title = h.a.h3.text
            link = h.a.get("href")
            rank = counter
            results.append(
                {
                    "title": h.a.h3.text,
                    "url": link,
                    "domain": urlparse(link).netloc,
                    "rank": rank,
                }
            )

    driver.quit()  # Close the Selenium WebDriver

    return results[:3]

# ... (rest of the code remains the same)

# Handle user input
if prompt := st.chat_input("Let's talk?"):
    start_prompt_used = ""

    if prompt.strip().lower() == "/reset":
        # ... (reset handling remains the same)

    elif prompt.strip().lower().startswith("/summarize"):
        # ... (/summarize handling remains the same)

    elif prompt.strip().lower().startswith("/rewrite"):
        # ... (/rewrite handling remains the same)

    elif prompt.strip().lower().startswith("/google"):
        # Handle /google command
        input_query = prompt.split(" ", 1)[1].strip()
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown(
                "Searching Google For: " + input_query + " ..."
            )
            search_results = search_google(input_query, model, temperature, top_p)

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

            new_search_prompt = prompts.google_search_prompt.format(
                input=over_all_summary
            )

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
        # ... (regular user input handling remains the same)

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
