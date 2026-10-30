\# SpendWise



SpendWise is a personal finance tracker built with Flask and PostgreSQL.



It allows users to record income and expenses, manage categories, view their current balance, edit or delete transactions, and generate monthly spending reports.



\## Features



\- Add income and expense transactions

\- Categorize transactions

\- View total income

\- View total expenses

\- Calculate the current balance automatically

\- Edit existing transactions

\- Delete transactions

\- Sort income before expenses

\- Generate monthly spending reports

\- Filter reports by month and year

\- Responsive, styled dashboard



\## Technologies



\- Python

\- Flask

\- PostgreSQL

\- Psycopg

\- Jinja2

\- HTML

\- CSS



\## Database design



The application uses two main tables.



\### categories



Stores available transaction categories.



| Column | Description |

|---|---|

| category\_id | Primary key |

| name | Unique category name |



\### transactions



Stores income and expense records.



| Column | Description |

|---|---|

| transaction\_id | Primary key |

| category\_id | Foreign key to categories |

| amount | Transaction amount |

| transaction\_type | Either income or expense |

| transaction\_date | Date of the transaction |

| description | Description of the transaction |



Relationship:



```text

categories 1 ──── \* transactions



One category can be associated with many transactions.



Database constraints

The database uses:



Primary keys

Foreign keys

Unique category names

Positive transaction amounts

A check constraint limiting transaction types to income or expense

An index on transaction dates

Installation

1\. Clone the project

git clone YOUR\_GITHUB\_REPOSITORY\_URL

cd spendwise

2\. Install the Python packages

py -m pip install flask "psycopg\[binary]" python-dotenv

3\. Create the database

Create a PostgreSQL database named:



spendwise

Then create the tables:



CREATE TABLE categories (

&#x20;   category\_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

&#x20;   name VARCHAR(100) NOT NULL UNIQUE

);



CREATE TABLE transactions (

&#x20;   transaction\_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

&#x20;   category\_id INTEGER REFERENCES categories(category\_id),

&#x20;   amount NUMERIC(10, 2) NOT NULL CHECK (amount > 0),

&#x20;   transaction\_type VARCHAR(10) NOT NULL

&#x20;       CHECK (transaction\_type IN ('income', 'expense')),

&#x20;   transaction\_date DATE NOT NULL DEFAULT CURRENT\_DATE,

&#x20;   description TEXT

);



CREATE INDEX idx\_transactions\_date

&#x20;   ON transactions(transaction\_date);

Add some starter categories:



INSERT INTO categories (name)

VALUES

&#x20;   ('Entertainment'),

&#x20;   ('Food'),

&#x20;   ('Income'),

&#x20;   ('Salary'),

&#x20;   ('Transport')

ON CONFLICT (name) DO NOTHING;

4\. Create the environment file

Create a file named .env in the project folder:



DATABASE\_URL=postgresql://postgres:YOUR\_PASSWORD@localhost:5432/spendwise

Replace YOUR\_PASSWORD with your local PostgreSQL password.



Never commit .env to GitHub.



5\. Run the application

py app.py

Open the application at:



http://127.0.0.1:5000

Example reports

The monthly report groups expenses by category and calculates the total spent during the selected month.



Example:



Food          £54.25

Transport     £12.00

Entertainment  £8.00

Skills demonstrated

This project demonstrates:



Relational database design

Primary and foreign keys

Database constraints

SQL joins

SQL aggregation

GROUP BY

Date filtering

Parameterized SQL queries

CRUD operations

Flask routing

HTML form handling

Environment variable configuration

Basic application styling

Future improvements

Possible future features include:



User authentication

Multiple user accounts

Budget tracking

CSV export

Charts and visual reports

Recurring transactions

Automated tests

Docker deployment

Cloud deployment

Security notes

This project uses parameterized SQL queries to reduce SQL injection risk.



The database password is stored in .env, which is excluded through .gitignore.



This application is intended for local development and portfolio demonstration. Additional authentication and security configuration would be required before production deployment.







