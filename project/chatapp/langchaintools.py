# chatapp/tools.py
import requests
from langchain.tools import tool

BASE_URL = "http://127.0.0.1:8000/api"  # adjust if needed


@tool
def get_categories() -> str:
    """Get all active product categories"""
    response = requests.get(f"{BASE_URL}/categories/")
    return response.text


@tool
def get_products(category: int = None, subcategory: int = None) -> str:
    """
    Get products.
    Optional filters:
    - category (int)
    - subcategory (int)
    """
    params = {}
    if category:
        params["category"] = category
    if subcategory:
        params["subcategory"] = subcategory

    response = requests.get(f"{BASE_URL}/products/", params=params)
    return response.text


@tool
def get_product_detail(product_id: int) -> str:
    """Get detailed information for a specific product by ID"""
    response = requests.get(f"{BASE_URL}/products/{product_id}/")
    return response.text


@tool
def get_active_offers() -> str:
    """Get all currently active offers"""
    response = requests.get(f"{BASE_URL}/offers/")
    return response.text
