import os
import time
import random
from dotenv import load_dotenv
from ollama import Client, Tool

# Import your tool functions
from .langchaintools import (
    get_categories,
    get_products,
    get_product_detail,
    get_active_offers,
)

load_dotenv()


client = Client()

# System prompt
SYSTEM_PROMPT = """
You are a professional AI shopping assistant for a clothing and footwear store.

Rules:
- ALWAYS call tools for real data.
- if user asks about categories → call get_categories.
- if user asks about products → call get_products.
- if user asks about specific product → call get_product_detail.
- if user asks about discounts → call get_active_offers.
- If you need clarification, ask.
"""

# Wrap your functions as Ollama Tool objects
TOOLS = [
    Tool(name="get_categories", description="Returns all product categories", func=get_categories),
    Tool(name="get_products", description="Returns products in a category", func=get_products),
    Tool(name="get_product_detail", description="Returns details for a product", func=get_product_detail),
    Tool(name="get_active_offers", description="Returns all active offers", func=get_active_offers),
]

# Conversation history to maintain multi-turn context
conversation = [
    {"role": "system", "content": SYSTEM_PROMPT}
]


def loading_animation(text="Loading", duration=2):
    """Simulates a loading animation."""
    for _ in range(duration):
        for dots in range(1, 4):
            print(f"\r{text}{'.' * dots}   ", end="", flush=True)
            time.sleep(0.5)
    print("\r", end="")


def run_agent(user_input: str) -> str:
    """
    Sends user input to the Ollama model, allowing it to call your tools.
    Maintains conversation history for multi-turn chats.
    Includes immersive loading/thinking animations and error handling.
    """
    try:
    
        loading_animation("Thinking", duration=random.randint(2, 4))

        
        conversation.append({"role": "user", "content": user_input})

        
        response = client.chat(
            model="llama3.1", 
            messages=conversation,
            tools=TOOLS
        )

        # Extract model reply
        reply = response.get("message", {}).get("content", "")
        if not reply:
            raise ValueError("Model returned empty response.")

        
        conversation.append({"role": "assistant", "content": reply})

        # Simulate “fetching data” animation if certain keywords
        if any(word in reply.lower() for word in ["loading", "fetching", "retrieving"]):
            loading_animation("Fetching data from store", duration=3)

        return reply

    except Exception as e:
        # Handle any error gracefully
        error_messages = [
            "Oops! Something went wrong ",
            "Hmm… I ran into a snag ",
            "Sorry, my circuits are a bit frazzled "
        ]
        print(random.choice(error_messages))
        print(f"[Debug info: {e}]")
        return "Sorry, I couldn't process that. Could you try again?"


if __name__ == "__main__":
    print("🛍️ Welcome to the Shopping AI Assistant!")
    print("Type 'exit' or 'quit' to leave.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print(" Exiting assistant. Have a great shopping day!")
            break

        answer = run_agent(user_input)

        # Simulate typing effect for AI reply
        for char in answer:
            print(char, end="", flush=True)
            time.sleep(random.uniform(0.01, 0.03))
        print("\n")
