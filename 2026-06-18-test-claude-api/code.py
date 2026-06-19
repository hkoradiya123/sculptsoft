from dotenv import load_dotenv

load_dotenv()

from anthropic import Anthropic

client = Anthropic(
#     api_key= load_dotenv().get("ANTHROPIC_API_KEY")
) 

model = "claude-haiku-4-5-20251001"

# message = client.messages.create(
#     model=model,
#     max_tokens=300,
#     messages=[
#         {
#             "role": "user",
#             "content": "Write a haiku about the beauty of nature."
#         }
#     ]
# )

# print(message.content[0].text)(

def add_user_message(messages, content):
    messages.append({
        "role": "user",
        "content": content
    })
    
def add_assistant_message(messages, content):
    messages.append({
        "role": "assistant",
        "content": content
    })
    
def chat(messages):
    response = client.messages.create(
        model=model,
        max_tokens=300,
        messages=messages
    )
    return response.content[0].text    # pyright: ignore[reportAttributeAccessIssue]

messages = []

add_user_message(messages, "tell me about demon slayer anime?")

response = chat(messages)
print(response)

add_assistant_message(messages, response)

add_user_message(messages, "who is the main character?")
response = chat(messages)
print(response)
