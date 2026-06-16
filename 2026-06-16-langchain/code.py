import os
from dotenv import load_dotenv

load_dotenv()

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import PromptTemplate

llm = ChatNVIDIA(
    model="deepseek-ai/deepseek-v4-flash", 
    temperature=0.4
)


# from langchain_core.chains import LLMChain

# Initialize the free hosted NIM model
# llm = ChatNVIDIA(
#     model="meta/llama-3.1-70b-instruct", 
#     temperature=0.7
# )



# # Invoke the model normally
# response = llm.invoke("What are the benefits of using microservices?")
# print(response.content)


# prompt = PromptTemplate(
#     input_variables=["cuisine"],
#     template="""
#             Suggest one restaurant name
#             for {cuisine} cuisine
#             """
#     )

# response = llm.invoke(prompt.format(cuisine="pakistan"))
# print(response.content)



# response_stream = llm.stream("helo how are you and what can u do?")


# for chunk in response_stream:
#     chunk.content = chunk.content.replace("###", "")
#     chunk.content = chunk.content.replace("**", "")
#     print(chunk.content, end='', flush=True)


# ----------llm chain -------------
# prompt = PromptTemplate(
#     input_variables=["topic"],
#     template="Give me a one-sentence fact about {topic}."
# )
# chain = LLMChain(llm=llm, prompt=prompt)

# # Execute the chain
# response = chain.run(topic="quantum computing")

# print(response)


# 3. Create the chain using the pipe operator


# This replaces: chain = LLMChain(llm=llm, prompt=prompt)
# 4. Run the chain by passing your inputs into .invoke()

# prompt = PromptTemplate.from_template(
#     "Give me a one-sentence fact about {topic}. What are the benefits of using {topic}?",
# )

# chain = prompt | llm


name_prompt = PromptTemplate(
    input_variables=["cuisine"],
    template="""
Suggest a restaurant name
for {cuisine} cuisine
"""
)

# Prompt 2

menu_prompt = PromptTemplate(
    input_variables=["restaurant_name"],
    template="""
Generate menu for
{restaurant_name}
"""
)

# Chains

name_chain = (
    name_prompt
    | llm
    | StrOutputParser()
)

menu_chain = (
    menu_prompt
    | llm
    | StrOutputParser()
)

# Sequential Workflow

restaurant_name = name_chain.invoke(
    {"cuisine": "Indian"}
)

menu = menu_chain.invoke(
    {
        "restaurant_name":
        restaurant_name
    }
)

print(menu)




# response = chain.stream({"topic": "microservices"})

# for chunk in response:
#     chunk.content = chunk.content.replace("###", "")
#     chunk.content = chunk.content.replace("**", "")
#     print(chunk.content, end='', flush=True)