"""Minimal recommendation-serving API, deployed to Azure App Service.

Reuses the same Top-K ranking metrics logic from the Product Recommendation
System project, exposed as a small live service instead of an offline script.
"""

import os

from flask import Flask, jsonify, request

app = Flask(__name__)

USE_AZURE_SQL = os.environ.get("USE_AZURE_SQL", "false").lower() == "true"

# In-memory fallback (used for local dev and tests, no DB credentials needed)
PRODUCTS = {
    1: {"name": "Wireless Mouse", "category": "Electronics"},
    2: {"name": "Mechanical Keyboard", "category": "Electronics"},
    3: {"name": "Notebook", "category": "Stationery"},
    4: {"name": "Water Bottle", "category": "Home"},
    5: {"name": "Desk Lamp", "category": "Home"},
}

USER_HISTORY = {
    "u1": [1, 2],
    "u2": [3, 4],
    "u3": [1, 5],
}


def get_products():
    if USE_AZURE_SQL:
        import db
        return db.fetch_products()
    return PRODUCTS


def get_user_history(user_id):
    if USE_AZURE_SQL:
        import db
        return db.fetch_user_history(user_id)
    return USER_HISTORY.get(user_id, [])


@app.get("/health")
def health():
    return jsonify({"status": "ok", "data_source": "azure_sql" if USE_AZURE_SQL else "in_memory"})


@app.get("/products")
def list_products():
    return jsonify(get_products())


@app.get("/recommend/<user_id>")
def recommend(user_id):
    """Naive category-affinity recommender: suggest unseen products from
    categories the user has already interacted with."""
    products = get_products()
    history = get_user_history(user_id)
    seen_categories = {products[pid]["category"] for pid in history if pid in products}
    recs = [
        pid
        for pid, info in products.items()
        if pid not in history and info["category"] in seen_categories
    ]
    if not recs:
        recs = [pid for pid in products if pid not in history][:3]
    return jsonify({"user_id": user_id, "recommended_product_ids": recs})


def precision_at_k(recommended, relevant, k):
    if k <= 0:
        raise ValueError("k must be positive")
    top_k = recommended[:k]
    relevant_set = set(relevant)
    hits = sum(1 for item in top_k if item in relevant_set)
    return hits / k


def recall_at_k(recommended, relevant, k):
    relevant_set = set(relevant)
    if not relevant_set:
        return 0.0
    top_k = recommended[:k]
    hits = sum(1 for item in top_k if item in relevant_set)
    return hits / len(relevant_set)


def hit_rate_at_k(recommended, relevant, k):
    relevant_set = set(relevant)
    top_k = recommended[:k]
    return 1.0 if any(item in relevant_set for item in top_k) else 0.0


@app.post("/metrics/score")
def score():
    """Score a recommendation list against ground-truth relevant items.

    Expected JSON body:
    {"recommended": [1, 2, 3], "relevant": [2, 3], "k": 3}
    """
    body = request.get_json(force=True, silent=True) or {}
    recommended = body.get("recommended")
    relevant = body.get("relevant")
    k = body.get("k", 3)

    if not isinstance(recommended, list) or not isinstance(relevant, list):
        return jsonify({"error": "recommended and relevant must be lists"}), 400

    return jsonify({
        "precision_at_k": precision_at_k(recommended, relevant, k),
        "recall_at_k": recall_at_k(recommended, relevant, k),
        "hit_rate_at_k": hit_rate_at_k(recommended, relevant, k),
        "k": k,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
