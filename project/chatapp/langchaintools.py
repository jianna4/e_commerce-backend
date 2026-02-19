# chatapp/tools.py
import requests
from langchain.tools import tool
from pydantic import BaseModel
from typing import List, Optional

BASE_URL = "http://127.0.0.1:8000/products"  # make sure your Django server runs here

# ----------------------------
# Input Schemas for tools
# ----------------------------
class ProductsInput(BaseModel):
    category: Optional[int] = None
    subcategory: Optional[int] = None

class ProductDetailInput(BaseModel):
    product_id: int

# ----------------------------
# Tools
# ----------------------------
@tool(args_schema=None)  # no arguments
def get_categories() -> List[dict]:
    """Fetch all active categories.
    it answers question like what products do you have?
    what type of eccomerce store are you?"""
    try:
        resp = requests.get(f"{BASE_URL}/categories/")
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return [{"error": f"Failed to fetch categories: {e}"}]
    except ValueError:
        return [{"error": "API returned invalid JSON"}]


@tool(args_schema=ProductsInput)
def get_products(category: Optional[int] = None, subcategory: Optional[int] = None) -> List[dict]:
    """Fetch products, optionally filtered by category/subcategory.
    it answers question like what shoes do you have?
    """
    try:
        params = {}
        if category: params["category"] = category
        if subcategory: params["subcategory"] = subcategory

        resp = requests.get(f"{BASE_URL}/products/", params=params)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return [{"error": f"Failed to fetch products: {e}"}]
    except ValueError:
        return [{"error": "API returned invalid JSON"}]


@tool(args_schema=ProductDetailInput)
def get_product_detail(product_id: int) -> dict:
    """Fetch detailed info about one product.
    it answers question like do you have red shoes in size 9?
    answers questions like do yuo have mum jeans in stock? what is the price of nike air max 90? what is the description of adidas ultraboost?
    """
    try:
        resp = requests.get(f"{BASE_URL}/products/{product_id}/")
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch product detail: {e}"}
    except ValueError:
        return {"error": "API returned invalid JSON"}


@tool(args_schema=None)
def get_active_offers() -> List[dict]:
    """Fetch all currently active offers."""
    try:
        resp = requests.get(f"{BASE_URL}/offers/")
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return [{"error": f"Failed to fetch offers: {e}"}]
    except ValueError:
        return [{"error": "API returned invalid JSON"}]
