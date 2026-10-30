import os
from datetime import date, datetime
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
from psycopg.rows import dict_row

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)


def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL was not loaded from .env")

    return psycopg.connect(database_url)


@app.route("/", methods=["GET", "POST"])
def home():
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            if request.method == "POST":
                category_name = request.form["category"]
                amount = request.form["amount"]
                transaction_type = request.form["transaction_type"]
                transaction_date = request.form["transaction_date"]
                description = request.form["description"]

                cursor.execute(
                    """
                    SELECT category_id
                    FROM categories
                    WHERE name = %s
                    """,
                    (category_name,),
                )
                category = cursor.fetchone()

                cursor.execute(
                    """
                    INSERT INTO transactions
                        (
                            category_id,
                            amount,
                            transaction_type,
                            transaction_date,
                            description
                        )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        category["category_id"],
                        amount,
                        transaction_type,
                        transaction_date,
                        description,
                    ),
                )

                connection.commit()
                return redirect(url_for("home"))

            cursor.execute("""
                SELECT category_id, name
                FROM categories
                ORDER BY name
            """)
            categories = cursor.fetchall()

            cursor.execute("""
                SELECT
                    t.transaction_id,
                    c.name AS category,
                    t.amount,
                    t.transaction_type,
                    t.transaction_date,
                    t.description
                FROM transactions AS t
                LEFT JOIN categories AS c
                    ON c.category_id = t.category_id
                ORDER BY
                    CASE
                        WHEN t.transaction_type = 'income' THEN 0
                        ELSE 1
                    END,
                    t.transaction_date DESC
            """)
            transactions = cursor.fetchall()

            cursor.execute("""
                SELECT
                    COALESCE(
                        SUM(CASE
                            WHEN transaction_type = 'income' THEN amount
                            ELSE 0
                        END), 0
                    ) AS total_income,
                    COALESCE(
                        SUM(CASE
                            WHEN transaction_type = 'expense' THEN amount
                            ELSE 0
                        END), 0
                    ) AS total_expenses
                FROM transactions
            """)
            totals = cursor.fetchone()

    balance = totals["total_income"] - totals["total_expenses"]

    return render_template(
        "index.html",
        categories=categories,
        transactions=transactions,
        total_income=totals["total_income"],
        total_expenses=totals["total_expenses"],
        balance=balance,
    )


@app.get("/report")
def report():
    selected_month = request.args.get(
        "month",
        date.today().strftime("%Y-%m"),
    )

    try:
        month_start = datetime.strptime(
            selected_month,
            "%Y-%m",
        ).date()
    except ValueError:
        selected_month = date.today().strftime("%Y-%m")
        month_start = datetime.strptime(
            selected_month,
            "%Y-%m",
        ).date()

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    c.name AS category,
                    SUM(t.amount) AS total_spent
                FROM transactions AS t
                JOIN categories AS c
                    ON c.category_id = t.category_id
                WHERE t.transaction_type = 'expense'
                  AND t.transaction_date >= %s
                  AND t.transaction_date <
                      (%s + INTERVAL '1 month')::date
                GROUP BY c.name
                ORDER BY total_spent DESC
                """,
                (month_start, month_start),
            )
            spending = cursor.fetchall()

            cursor.execute(
                """
                SELECT COALESCE(SUM(t.amount), 0) AS total_spent
                FROM transactions AS t
                WHERE t.transaction_type = 'expense'
                  AND t.transaction_date >= %s
                  AND t.transaction_date <
                      (%s + INTERVAL '1 month')::date
                """,
                (month_start, month_start),
            )
            total_spent = cursor.fetchone()["total_spent"]

    return render_template(
        "report.html",
        spending=spending,
        total_spent=total_spent,
        report_month=month_start.strftime("%B %Y"),
        selected_month=selected_month,
    )


@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            if request.method == "POST":
                category_name = request.form["category"]
                amount = request.form["amount"]
                transaction_type = request.form["transaction_type"]
                transaction_date = request.form["transaction_date"]
                description = request.form["description"]

                cursor.execute(
                    """
                    SELECT category_id
                    FROM categories
                    WHERE name = %s
                    """,
                    (category_name,),
                )
                category = cursor.fetchone()

                cursor.execute(
                    """
                    UPDATE transactions
                    SET
                        category_id = %s,
                        amount = %s,
                        transaction_type = %s,
                        transaction_date = %s,
                        description = %s
                    WHERE transaction_id = %s
                    """,
                    (
                        category["category_id"],
                        amount,
                        transaction_type,
                        transaction_date,
                        description,
                        transaction_id,
                    ),
                )

                connection.commit()
                return redirect(url_for("home"))

            cursor.execute(
                """
                SELECT
                    transaction_id,
                    category_id,
                    amount,
                    transaction_type,
                    transaction_date,
                    description
                FROM transactions
                WHERE transaction_id = %s
                """,
                (transaction_id,),
            )
            transaction = cursor.fetchone()

            cursor.execute("""
                SELECT category_id, name
                FROM categories
                ORDER BY name
            """)
            categories = cursor.fetchall()

    if not transaction:
        return redirect(url_for("home"))

    return render_template(
        "edit.html",
        transaction=transaction,
        categories=categories,
    )


@app.post("/delete/<int:transaction_id>")
def delete_transaction(transaction_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM transactions
                WHERE transaction_id = %s
                """,
                (transaction_id,),
            )
            connection.commit()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)