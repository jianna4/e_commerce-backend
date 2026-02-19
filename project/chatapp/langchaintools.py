# chatapp/tools.py
import requests
from langchain.tools import tool

BASE_URL = "http://127.0.0.1:8000/api"  # adjust if needed


@tool
def get_categories() -> list:
    """
    Use this tool when the user wants to see available product categories.

    Call this when the user says things like:
    - "What categories do you have?"
    - "Show me product types"
    - "What sections are in the store?"
    - "Do you have men's or women's categories?"

    Returns:
    A list of active categories.
    Each category contains:
    - id: unique category ID
    - name: category name
    - slug
    - description
    - subcategories: list of subcategories inside this category

    Important:
    - Always call this tool instead of guessing category names.
    - Do not invent categories.
    """
    response = requests.get(f"{BASE_URL}/categories/")
    return response.json()


@tool
def get_products(category: int = None, subcategory: int = None) -> list:
    """
    Use this tool when the user wants to see products.

    Call this when the user says:
    - "Show me products"
    - "What shoes do you have?"
    - "Show products in category 2"
    - "Show items in subcategory 5"
    - "What do you have in sneakers?"

    Optional Parameters:
    - category: The ID of a category to filter products.
    - subcategory: The ID of a subcategory to filter products.

    Returns:
    A list of available products.
    Each product contains:
    - id
    - name
    - description
    - display_price (final price including active discount if any)
    - price (original price)
    - stock
    - sizes
    - images
    - active_offer (if any)

    Important:
    - If the user specifies a category or subcategory, use the correct ID.
    - If no filter is provided, return all available products.
    - Never invent product data.
    """
    params = {}
    if category:
        params["category"] = category
    if subcategory:
        params["subcategory"] = subcategory

    response = requests.get(f"{BASE_URL}/products/", params=params)
    return response.json()


@tool
def get_product_detail(product_id: int) -> dict:
    """
    Use this tool when the user asks about a specific product.

    Call this when the user says:
    - "Tell me about product 5"
    - "Show details for item 12"
    - "What sizes does product 3 have?"
    - "Does product 7 have a discount?"
    - "What colors are available for this product?"

    Parameter:
    - product_id: The unique ID of the product.

    Returns:
    A dictionary containing detailed information about one product:
    - id
    - name
    - description
    - display_price (final price after discount if active)
    - price (original price)
    - stock
    - sizes (with color and quantity information)
    - images
    - active_offer (if there is a valid campaign)

    Important:
    - Only call this tool when a specific product ID is known.
    - If product is not found, return a structured error.
    - Do not guess product details.
    """
    response = requests.get(f"{BASE_URL}/products/{product_id}/")
    return response.json()


@tool
def get_active_offers() -> list:
    """
    Use this tool when the user asks about discounts, promotions, or special deals.

    Call this when the user says:
    - "What offers are active?"
    - "Do you have any discounts?"
    - "Show me promotions"
    - "What items are on sale?"

    Returns:
    A list of currently active offers.
    Each offer contains:
    - id
    - new_price
    - old_price
    - percentage_off
    - campaign (title, description, start_date, end_date)
    - product (basic product information)
    - is_active

    Important:
    - Only returns offers that are currently valid.
    - Never assume a product is discounted without calling this tool.
    """
    response = requests.get(f"{BASE_URL}/offers/")
    return response.json()
