"""
Search utility functions.
"""
import pandas as pd
import re


def search_products_with_code(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """
    Search products by keywords in product_name using regex.
    
    Args:
        df: DataFrame with 'product_code' and 'product_name' columns
        query: Search query (e.g. "camera dome")
    Returns:
        DataFrame: matching rows with product_code and product_name
    """
    keywords = query.lower().split()
    regex_pattern = "".join(f"(?=.*{re.escape(word)})" for word in keywords)
    regex = re.compile(regex_pattern, re.IGNORECASE)

    mask = df["product_name"].apply(lambda x: bool(regex.search(str(x))))
    return df[mask]

