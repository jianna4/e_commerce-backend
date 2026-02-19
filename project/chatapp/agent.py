import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent

# Import your tools (already decorated with @tool)
from .langchaintools import ( get_categories,get_products,get_product_detail,get_active_offers,)

load_dotenv()


model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)


SYSTEM_PROMPT = """
You are a professional AI shopping assistant for a clothing and footwear store.

Rules:
- ALWAYS call tools for real data.
- NEVER invent products, prices, or offers.
- When user asks about categories → call get_categories.
- When user asks about products → call get_products.
- When user asks about specific product → call get_product_detail.
- When user asks about discounts → call get_active_offers.
- If you need clarification, ask politely.
- Format responses clearly and professionally.
"""


agent_executor = create_agent(
    model=model,
    tools=[
        get_categories,
        get_products,
        get_product_detail,
        get_active_offers,
    ],
    system_prompt=SYSTEM_PROMPT,
)
