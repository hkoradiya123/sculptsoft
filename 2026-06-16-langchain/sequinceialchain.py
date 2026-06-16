import os
from dotenv import load_dotenv

load_dotenv()

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatNVIDIA(
    model="deepseek-ai/deepseek-v4-flash", 
    temperature=0.4
)


# Prompt 1

name_prompt = PromptTemplate(
    input_variables=["cuisine"],
    template="""
Suggest a restaurant name
for {cuisine} cuisine.
Return only the restaurant name.
"""
)


# Prompt 2

menu_prompt = PromptTemplate(
    input_variables=["restaurant_name"],
    template="""
Generate 5 menu items for
{restaurant_name}.
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


# Sequential LCEL Workflow

full_chain = (
    {
        "restaurant_name": name_chain
    }
    | menu_chain
)


result = full_chain.invoke(
    {
        "cuisine": "Indian"
    }
)

print(result)

# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser

# from langchain_nvidia_ai_endpoints import ChatNVIDIA


# prompt = PromptTemplate(
#     input_variables=["cuisine"],
#     template="""
#         Suggest a fancy restaurant name
#         for {cuisine} cuisine.
#         Return only the restaurant name.
#         """
#     )

# chain = (
#     prompt
#     | llm
#     | StrOutputParser()
# )

# response = chain.invoke(
#     {"cuisine": "Indian"}
# )

# print(response)