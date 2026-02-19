# chatapp/agent.py
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from .langchaintools import (
    get_categories,
    get_products,
    get_product_detail,
    get_active_offers,
)

import os

llm = ChatOpenAI(
    model="gpt-4o-mini",  # or gpt-4o
    temperature=0
)

tools = [
    get_categories,
    get_products,
    get_product_detail,
    get_active_offers,
]

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,  # enables tool calling
    memory=memory,
    verbose=True,
)
