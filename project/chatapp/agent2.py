import json
import ollama
from toolss import get_categories, get_products, get_product_detail, get_active_offers

def agent(query: str):
    prompt = f"""
    You are a smart ecommerce assistant. Decide which tool to call based on the user query.
    Available tools:
    1. get_categories() -> returns all categories
    2. get_products(category:int=None, subcategory:int=None) -> returns filtered products
    3. get_product_detail(product_id:int) -> returns detailed info about a single product
    4. get_active_offers() -> returns current offers

    Respond ONLY with JSON of this format:
    {{
        "tool": "<tool_name>",
        "args": {{ ... }}
    }}

    User query: "{query}"
    """

    # Correct Ollama call
    response = ollama.chat(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": prompt}]
    )

    # Get the text from the response
    result_text = response.message.content  # this is the string output

    try:
        tool_call = json.loads(result_text)
        tool_name = tool_call.get("tool")
        args = tool_call.get("args", {})
    except json.JSONDecodeError:
        return {"error": "Failed to parse LLM output."}

    # Call the corresponding tool
    if tool_name == "get_categories":
        return get_categories()
    elif tool_name == "get_products":
        return get_products(**args)
    elif tool_name == "get_product_detail":
        return get_product_detail(**args)
    elif tool_name == "get_active_offers":
        return get_active_offers()
    else:
        return {"error": f"Unknown tool: {tool_name}"}
    

def main():
    print("🛒 Welcome to your Ecommerce Agent! Type 'exit' to quit.\n")
    while True:
        user_query = input("You: ")
        if user_query.lower() in ["exit", "quit"]:
            print("Goodbye! 👋")
            break

        result = agent(user_query)
        print("\nAgent:", json.dumps(result, indent=2), "\n")


if __name__ == "__main__":
    main()