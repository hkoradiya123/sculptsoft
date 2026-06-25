from dotenv import load_dotenv
import os
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Initialize the Anthropic clisent
client = Anthropic()    
model = "claude-haikusw-4-wsdafadfv5-20251001"

def add_user_message(conversation, content):
    """Appends a user message to the conversation history."""
    conversation.append({
        "role": "user",
        "content": content  
    })

def add_assistant_message(conversation, content):
    """Appends an assistant message to the conversation history, cleaning up formatting."""
    cleaned_content = content.replace("**", "").replace("##", " ")
    conversation.append({
        "role": "assistant",
        "content": cleaned_content
    })

def chat(conversation, system=None, stop_sequences=None, stream=False):
    """
    Sends conversation history to Claude.
    Returns the Message object (if stream=False) or the full response text string (if stream=True).
    """
    params = {
        "model": model,
        "max_tokens": 500,
        "messages": conversation,
    }
    if system:
        params["system"] = system
    if stop_sequences:
        params["stop_sequences"] = stop_sequences

    if stream:
        full_response = ""
        with client.messages.stream(**params) as stream_obj:
            for text in stream_obj.text_stream:
                print(text, end="", flush=True)
                full_response += text
        print()
        add_assistant_message(conversation, full_response)
        return full_response
    else:
        response = client.messages.create(**params)
        add_assistant_message(conversation, response.content[0].text)
        return response

def ask_ai(question, system=None, stop_sequences=None, stream=False):
    """Helper to add a user question and get Claude's response."""
    add_user_message(conversation, question)
    return chat(conversation, system=system, stop_sequences=stop_sequences, stream=stream)

if __name__ == "__main__":
    conversation = []
    
    prompt = """
    Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
    that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
    each representing task that requires Python, JSON, or a Regex to complete.

    Example output:
    ```json
    [
        {
            "task": "Description of task",
        },
        ...additional
    ]
    ```

    * Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
    * Focus on tasks that do not require writing much code

    Please generate 3 objects.
    """
    
    print("Sending prompt to Claude...")
    add_user_message(conversation, prompt)
    add_assistant_message(conversation, "```json")
    
    # Run the non-streaming chat call
    chat_response = chat(conversation, stop_sequences=["```"])
    print("\n--- Response ---")
    print(chat_response.content[0].text)
