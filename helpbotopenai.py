import openai
import os

# Set your API key in code (not secure for production!)
os.environ["OPENAI_API_KEY"] = "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"

# Then create the client
client = openai.OpenAI()

def chat_with_openai(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    system_prompt = (
        "You are a helpful assistant. Use the following help guide to answer user questions:\n"
        "HELP DOCUMENT:\n"
        "To reset your password, click 'Forgot Password' on the login screen. "
        "You'll receive an email with a link to create a new one.\n"
        "If you don't receive it, check your spam folder or contact support."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "How do I reset my password?"}
    ]

    answer = chat_with_openai(messages)
    print("Bot:", answer)