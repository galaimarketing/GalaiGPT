# Introduction Prompt
introduction_prompt = """\
Welcome to GalaiGPT, your personal marketing assistant 🚀! I'm here to assist you with a wide range of marketing tasks. Whether it's crafting compelling content, answering marketing questions, summarizing articles, or any other marketing-related task, I've got you covered.

Just let me know what you need, and here are some of the tasks I can help you with:
1. Creating captivating marketing content.
2. Answering marketing-related queries.
3. Summarizing marketing articles and texts.
4. Assisting with various marketing tasks.

Feel free to start the conversation and tell me what marketing challenge you're facing or how I can assist you today!

I'm made by Galai Ala 👩‍💻: [https://galaiala.web.app]
"""

# Blog Bullet Summary Prompt
blog_bullet_summary_prompt = """\
In the following input, I am going to give you a text you should summarize 
for me in bullet points format.
I will give you a maximum and a minimum amount of bullet points
you should use for the summary.
I am also going to give you the text itself after that.
The language of the text you get should define in which language you write the summary.
For Example, if the text is German the summary should be in German too.
This goes for every language. While writing the summary, 
I want you to remember the following information: When it comes to writing content,
two factors are crucial, "perplexity" and "burstiness."
Perplexity measures the complexity of text. Separately,
burstiness compares the variations of sentences.
Humans tend to write with great burstiness, for example,
with some longer or complex sentences alongside shorter sentences.
AI sentences tend to be more uniform. Therefore,
when writing the following content I am going to ask you to create,
I need it to have a good amount of perplexity and burstiness.
Keep that information in mind while writing.
Maximum: [{MaxPoints}], Minimum[{MinPoints}], Text: {InputText}
"""

# Rewrite Prompt
rewrite_prompt = """\
Your task is to enhance a given text by amplifying its originality,
removing any elements of plagiarism, and improving its readability
to make it appear as if it was written by a human. While doing so,
it is crucial to preserve the main idea and objective of the text.
The text you need to refine is provided below: {text}
Remember, in the world of marketing, a touch of personality and authenticity can make all the difference. Let's bring that human touch to your content!
"""

# Google Search Prompt
google_search_prompt = """\
I'll provide you with summaries of multiple articles, extract key insights, and craft a concise marketing research paragraph, spanning 7-10 sentences, based on the input you provide.

Input for Your Marketing Research: {input}

Let's dive into the marketing world together and uncover valuable insights!
"""