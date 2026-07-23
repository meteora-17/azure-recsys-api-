# Recommendation Scoring API

A small Flask API deployed on Azure App Service, serving a naive category-affinity
recommender and the same Top-K ranking metrics (precision@k, recall@k, hit-rate@k)
used in the [Product Recommendation System](https://github.com/meteora-17/Dell-reccomender-system) project.

**Live:** http://shreeya-recsys-api.azurewebsites.net

## Endpoints

- `GET /health` — service status check
- `GET /products` — sample product catalog
- `GET /recommend/<user_id>` — category-affinity recommendations for a user
- `POST /metrics/score` — scores a recommendation list against ground-truth relevant items
  (`{"recommended": [1,2,3], "relevant": [2,3], "k": 3}`)

## Stack

Python, Flask, gunicorn, deployed to Azure App Service (Linux, free tier) via Azure CLI.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

## Test

```bash
pip install pytest
pytest test_app.py -v
```
