"""Azure SQL Database data-access layer.

Used only when USE_AZURE_SQL=true is set (i.e. when actually deployed with
a provisioned database). Local development and unit tests default to the
in-memory data in app.py, so no DB credentials are needed to run the test
suite or hack on the API locally.
"""

import os

import pymssql


def get_connection():
    return pymssql.connect(
        server=f"{os.environ['SQL_SERVER_NAME']}.database.windows.net",
        user=f"{os.environ['SQL_ADMIN_USER']}@{os.environ['SQL_SERVER_NAME']}",
        password=os.environ["SQL_ADMIN_PASSWORD"],
        database=os.environ["SQL_DATABASE_NAME"],
    )


def fetch_products():
    conn = get_connection()
    try:
        cur = conn.cursor(as_dict=True)
        cur.execute("SELECT id, name, category FROM Products")
        return {row["id"]: {"name": row["name"], "category": row["category"]} for row in cur}
    finally:
        conn.close()


def fetch_user_history(user_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT product_id FROM UserHistory WHERE user_id = %s", (user_id,))
        return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()
