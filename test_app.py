import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_list_products(client):
    resp = client.get("/products")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 5


def test_recommend_returns_category_affinity(client):
    resp = client.get("/recommend/u1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["user_id"] == "u1"
    assert isinstance(data["recommended_product_ids"], list)


def test_recommend_unknown_user_falls_back(client):
    resp = client.get("/recommend/unknown_user")
    assert resp.status_code == 200
    assert len(resp.get_json()["recommended_product_ids"]) > 0


def test_metrics_score_perfect_match(client):
    resp = client.post("/metrics/score", json={
        "recommended": [1, 2, 3], "relevant": [1, 2, 3], "k": 3
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["precision_at_k"] == 1.0
    assert data["recall_at_k"] == 1.0
    assert data["hit_rate_at_k"] == 1.0


def test_metrics_score_no_match(client):
    resp = client.post("/metrics/score", json={
        "recommended": [1, 2, 3], "relevant": [9, 10], "k": 3
    })
    data = resp.get_json()
    assert data["precision_at_k"] == 0.0
    assert data["hit_rate_at_k"] == 0.0


def test_metrics_score_rejects_bad_input(client):
    resp = client.post("/metrics/score", json={"recommended": "not-a-list", "relevant": [1]})
    assert resp.status_code == 400
