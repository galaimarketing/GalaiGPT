# prompts.py

# Introduction
print("🤝 Hello! I'm GalaiGPT, created by Galai Ala (visit Galai Ala's website [here](https://galaiala.web.app)), and I'm here to assist you in fine-tuning a chatbot to appear as a professional marketing agent. Let's get started!")

# Task explanation
print("🎯 Your task is to create a smart chatbot capable of assisting users with their marketing needs in a professional and effective manner.")

# Important questions
print("🔍 To begin, let's ask a few important questions that will guide the chatbot's responses and improve the user experience.")

# Question 1
print("❓ Question 1: What products or services does the chatbot need to assist users with? Please provide the relevant details.")
product_details = input("User's response: ")

# Question 2
print("❓ Question 2: Who is the target audience for the marketing efforts? Please provide any specific information about the target audience.")
target_audience = input("User's response: ")

# Question 3
print("❓ Question 3: What are the main goals of the marketing campaigns? Please provide the objectives and desired outcomes.")
marketing_goals = input("User's response: ")

# Platform question
print("💻 Additionally, please specify the platform on which the chatbot will be deployed for marketing assistance.")

# Summary of the task
print("📝 Great! Now that we have gathered the necessary information, we can proceed with fine-tuning the chatbot to provide professional marketing assistance.")

blog_bullet_summary_prompt = """\
In the following input, I am going to give you a text you should summarize 
for me a bullet points format.
I will give you a maximum and a minimum amount of bullet points
you should use for the summary.
I am also going to give you the text itself after that.
The language of the text you get should define in which language you write the summary.
For Example, if the text is German the summary should be in German too.
This goes for every language.While writing the summary 
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
Maximum: [{MaxPoints}], Minimum[{MinPoints}], Text: {InputText} """

# Rewrite prompt
rewrite_prompt = """Your task is to enhance a given text by amplifying its originality,
removing any elements of plagiarism, and improving its readability
to make it appear as if it was written by a human. While doing so,
it is crucial to preserve the main idea and objective of the text.
The text you need to refine is provided below: {text}"""

# Google search prompt
google_search_prompt = "I will provide you with summaries of multiple articles, extract the main points, and create a small research paragraph consisting of 7-10 sentences. Input: {input}"

# Conclusion
print("🚀 Fantastic! With these prompts, we can now fine-tune the chatbot to be an effective marketing agent. Good luck with your fine-tuning process!")
