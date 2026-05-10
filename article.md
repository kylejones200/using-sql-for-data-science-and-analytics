---
author: "Kyle Jones"
date_published: "May 14, 2025"
date_exported_from_medium: "November 10, 2025"
canonical_link: "https://medium.com/@kyle-t-jones/using-sql-for-data-science-and-analytics-719d2e1a0e0d"
---

# Using SQL for Data Science and Analytics SQL is the backbone of data science work in companies that rely on
structured data. Despite the growing ecosystem of Python, R, and...

### Using SQL for Data Science and Analytics
SQL is the backbone of data science work in companies that rely on structured data. Despite the growing ecosystem of Python, R, and cloud-native tools, most real-world datasets still live in relational databases. These could be traditional systems like PostgreSQL and Oracle, data warehouses like Redshift, or cloud-native services like BigQuery. Wherever the data lives, SQL is usually the first gate you must pass through to work with it.

SQL excels at expressing relationships between entities. Whether you're calculating churn rates, aggregating sales by geography, or building user cohorts, these tasks begin with structured queries. SQL lets you describe what you want, not how to compute it --- this declarative style is a strength. You ask the database to give you "sales by region and quarter," and it handles the execution plan. You don't have to worry about iterating over rows or indexing strategies.

SQL can power end-to-end analytical pipelines. You can calculate features for machine learning, perform exploratory analysis, validate data quality, and generate business metrics --- all inside SQL. It often outperforms Python in terms of speed when data volumes grow, because databases are optimized for parallelized set operations.

SQL is also universal. Analysts, data scientists, engineers, and business users often collaborate using SQL. The shared syntax means fewer translation layers, and the results are immediately reproducible.

But SQL lacks native support for machine learning, statistical testing, and visualization. That's where Python or R come in. The best data workflows use SQL for what it's good at --- access, joins, filters, aggregations --- and leave the rest to specialized tools.

In the rest of this article explores to use SQL as a full analytical tool by combining SQL with Python, using window functions and CTEs, engineering features, and building model-ready tables.

### Connecting to Data
Before writing a single SQL query, you need to connect to your database. This might be a local SQLite file, a cloud-based Postgres server, a production warehouse like Snowflake, or a sandboxed dataset in BigQuery. Regardless of where your data lives, the process usually involves three steps: setting up a connection, authenticating, and executing queries.

#### Local Database (SQLite)
SQLite is built into Python and great for testing. Here's how to connect and run queries:

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("local_data.db")
query = "SELECT * FROM orders LIMIT 5;"
df = pd.read_sql(query, conn)
conn.close
```

This works without installing a database server. Many tutorials and analytics pipelines start with SQLite for this reason.

#### PostgreSQL with SQLAlchemy
For most production-grade databases, use SQLAlchemy for connection and abstraction.

```python
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("postgresql+psycopg2://user:password@host:5432/database")
query = "SELECT * FROM customers LIMIT 10;"
df = pd.read_sql(query, engine)
```

If your database requires SSL or IAM authentication, you might need additional parameters. But the principle is the same: create an engine, write SQL, and pull the result into a DataFrame.

#### BigQuery
Google BigQuery can be accessed through the `google-cloud-bigquery` library. For example:

```python
from google.cloud import bigquery
client = bigquery.Client()

query = """
SELECT name, SUM(number) as total
FROM `bigquery-public-data.usa_names.usa_1910_2013`
WHERE state = 'TX'
GROUP BY name
ORDER BY total DESC
LIMIT 5;
"""
df = client.query(query).to_dataframe()
```

Authentication is handled via environment credentials or service accounts.

#### Why Python + SQL Is Powerful
SQL gives you expressive access to data. Python gives you analysis, modeling, and plotting. Together, they let you start with a query and end with an insight.

You can save reusable queries, wrap them in functions, or even parameterize them with Jinja templates. Many production workflows start with SQL and move into a Pandas pipeline. Some reverse it --- building queries from DataFrame inputs.

### Exploratory Analysis with SQL
Once you've connected to your database, the first thing you do is explore. Exploratory analysis in SQL mirrors what you'd do in pandas: count rows, look at group averages, identify extremes, and check for missing values. The difference is you're working with a query language, not a programming language.

#### Counts and Totals
Start with the basics: how many rows are in the table?

``` 
SELECT COUNT(*) FROM orders;
```

Count distinct customers:

``` 
SELECT COUNT(DISTINCT customer_id) FROM orders;
```

Aggregate sales:

``` 
SELECT SUM(order_total) AS total_sales FROM orders;
```

#### Group Aggregation
SQL's `GROUP BY` lets you summarize values by category---just like `groupby()` in pandas.

``` 
SELECT region, COUNT(*) AS num_orders, AVG(order_total) AS avg_order
FROM orders
GROUP BY region;
```

To dig deeper, group by more than one dimension:

``` 
SELECT region, EXTRACT(YEAR FROM order_date) AS year,
       SUM(order_total) AS yearly_sales
FROM orders
GROUP BY region, year;
```

This gives you a time series of sales by region.

#### Filtering and Sorting
Add `WHERE` to filter rows:

``` 
SELECT * FROM orders
WHERE order_total > 1000
ORDER BY order_total DESC
```

To inspect a specific segment:

``` 
SELECT customer_id, order_total, order_date
FROM orders
WHERE region = 'West' AND order_date >= '2023-01-01';
```

#### Derived Columns with CASE
You can define new variables in SQL using `CASE`.

``` 
SELECT order_id,
       order_total,
       CASE 
         WHEN order_total > 500 THEN 'High'
         WHEN order_total > 100 THEN 'Medium'
         ELSE 'Low'
       END AS order_size
FROM orders;
```

This kind of logic is useful for feature engineering, labeling, and dashboards.

#### NULL Checks
Check for missing data:

``` 
SELECT COUNT(*) AS total_orders,
       COUNT(order_total) AS non_null_orders,
       COUNT(*) - COUNT(order_total) AS missing_values
FROM orders;
```

Or flag nulls directly:

``` 
SELECT *,
       CASE 
         WHEN order_total IS NULL THEN 1 
         ELSE 0 
       END AS is_missing
FROM orders;
```

These tools --- counts, filters, grouping, and derived columns --- are the foundation of all analysis. In Python, you'd use `describe()` and `groupby()`. In SQL, it's `SELECT`, `GROUP BY`, `WHERE`, and `CASE`. Mastering this exploratory layer means you can answer 80% of business questions directly in SQL.

### Joins and Subqueries
Most useful data isn't in a single table. It's scattered across normalized tables --- customers, orders, products, reviews, employees. To analyze it, you have to join tables.

SQL joins are how you reassemble these pieces into a full picture. Once you learn how to combine tables, your analysis becomes richer and more flexible.

#### INNER JOIN
The most common type. Only returns rows where the join condition is satisfied in both tables.

``` 
SELECT o.order_id, o.order_total, c.customer_name
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id;
```

Use this when you're confident both tables have matching keys.

#### LEFT JOIN
Returns all rows from the left table and matching rows from the right. If there's no match, the result is NULL.

``` 
SELECT c.customer_name, o.order_id, o.order_total
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;
```

Use this when you want to preserve all customers --- even those with no orders.

#### FULL OUTER JOIN
Keeps all rows from both tables. Missing matches are filled with NULLs.

``` 
SELECT a.user_id, a.email, b.last_login
FROM active_users a
FULL OUTER JOIN login_events b ON a.user_id = b.user_id;
```

This is helpful for comparing two systems or detecting mismatches.

#### Joining on Composite Keys
Sometimes, relationships involve multiple keys:

``` 
SELECT *
FROM sales s
JOIN targets t
ON s.region = t.region AND s.year = t.year;
```

Make sure both keys are indexed for performance.

#### Subqueries
Subqueries are nested SELECTs. Use them to compute values on the fly.

Example: customers who placed above-average orders:

``` 
SELECT *
FROM orders
WHERE order_total > (
    SELECT AVG(order_total)
    FROM orders
);
```

Or to compute something per group:

``` 
SELECT region, customer_id, order_total
FROM orders
WHERE order_total = (
    SELECT MAX(order_total)
    FROM orders AS o2
    WHERE o2.customer_id = orders.customer_id
);
```

#### Common Table Expressions (CTEs)
CTEs improve readability. They let you define temporary tables in a query.

``` 
WITH top_customers AS (
    SELECT customer_id, SUM(order_total) AS total_spent
    FROM orders
    GROUP BY customer_id
    HAVING SUM(order_total) > 10000
)
SELECT c.customer_name, t.total_spent
FROM top_customers t
JOIN customers c ON t.customer_id = c.customer_id;
```

This is cleaner than deeply nested subqueries and can be chained.

Joins and subqueries unlock the true power of relational data. Once you understand how to combine tables and modularize queries, SQL becomes expressive. You stop thinking in tables and start thinking in relationships and flows.

### Window Functions and Advanced Analytics
Window functions add a layer of analytic power to SQL that goes beyond basic aggregation. They let you compute metrics across groups of rows --- without collapsing those groups into a single row. That means you can calculate running totals, differences from group averages, ranks, and more --- all while keeping the original row structure.

#### Syntax Overview
Every window function follows this basic structure:

``` 
function() OVER (
    PARTITION BY ...
    ORDER BY ...
)
```

Think of `PARTITION BY` like `GROUP BY`, but without collapsing rows. `ORDER BY` sets the sequence.

#### Ranking and Row Numbering
To rank customers within each region:

``` 
SELECT customer_id, region, order_total,
       RANK() OVER (PARTITION BY region ORDER BY order_total DESC) AS rank_in_region
FROM orders;
```

`RANK()` allows ties; `DENSE_RANK()` skips no ranks; `ROW_NUMBER()` assigns a unique number regardless.

#### Running Totals and Moving Averages
Running total of sales per customer:

``` 
SELECT customer_id, order_date, order_total,
       SUM(order_total) OVER (
           PARTITION BY customer_id
           ORDER BY order_date
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total
FROM orders;
```

7-day moving average of daily sales:

``` 
SELECT order_date, SUM(order_total) AS daily_sales,
       AVG(SUM(order_total)) OVER (
           ORDER BY order_date
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS moving_avg
FROM orders
GROUP BY order_date;
```

Here, the aggregation happens *before* the window function.

#### Lag, Lead, and Differences
Compare a row to its previous row:

``` 
SELECT order_date, customer_id, order_total,
       LAG(order_total) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order,
       order_total - LAG(order_total) OVER (PARTITION BY customer_id ORDER BY order_date) AS change
FROM orders;
```

You can also use `LEAD()` to look ahead. These are vital for change detection and behavioral analysis.

#### Percentiles and Distribution Positioning
Use `NTILE()` to break data into quantiles:

``` 
SELECT customer_id, order_total,
       NTILE(4) OVER (ORDER BY order_total) AS quartile
FROM orders;
```

To find the top 5% of orders:

``` 
SELECT *
FROM (
    SELECT *, PERCENT_RANK() OVER (ORDER BY order_total DESC) AS p_rank
    FROM orders
) ranked
WHERE p_rank <= 0.05;
```

This is useful for identifying outliers or VIP customers.

Window functions turn SQL into an analytics engine. They let you keep the row-level detail while adding context: how does this row compare to others in the same group? What came before it? What comes next?

With joins and window functions together, you can now build full-fledged analytical pipelines using only SQL.

### Feature Engineering in SQL
Feature engineering prepares raw data for modeling. This means converting messy, timestamped, relational data into structured columns that help a model make decisions. SQL excels at this step when the data lives in a relational database. You can create categorical labels, time-based features, normalized values, and encoded variables directly in SQL.

#### Binning and Categorization
Turn continuous values into buckets:

``` 
SELECT order_id, order_total,
       CASE
         WHEN order_total < 50 THEN 'Low'
         WHEN order_total BETWEEN 50 AND 200 THEN 'Medium'
         ELSE 'High'
       END AS order_size_category
FROM orders;
```

Or use `NTILE()` for data-driven bins:

``` 
SELECT order_id, order_total,
       NTILE(5) OVER (ORDER BY order_total) AS quintile
FROM orders;
```

#### Date and Time Transformations
Extract useful time-based features:

``` 
SELECT order_id, order_date,
       EXTRACT(DAYOFWEEK FROM order_date) AS weekday,
       EXTRACT(MONTH FROM order_date) AS month,
       EXTRACT(HOUR FROM order_timestamp) AS hour
FROM orders;
```

To create rolling windows:

``` 
WITH sales_by_day AS (
  SELECT order_date, SUM(order_total) AS daily_sales
  FROM orders
  GROUP BY order_date
)
SELECT order_date, daily_sales,
       AVG(daily_sales) OVER (
         ORDER BY order_date
         ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS rolling_week_avg
FROM sales_by_day;
```

#### Normalization and Scaling
You can z-score a column using window functions:

``` 
SELECT order_id, order_total,
       AVG(order_total) OVER () AS mean,
       STDDEV(order_total) OVER () AS stddev,
       (order_total - AVG(order_total) OVER ()) / STDDEV(order_total) OVER () AS z_score
FROM orders;
```

Use this when preparing inputs for distance-based models like k-NN.

#### Boolean and Dummy Features
Transform conditions into binary variables:

``` 
SELECT order_id, order_total,
       CASE WHEN order_total > 100 THEN 1 ELSE 0 END AS is_large_order,
       CASE WHEN region = 'West' THEN 1 ELSE 0 END AS is_west_region
FROM orders;
```

This is a common step before logistic regression or tree models.

#### One-Hot Encoding
SQL doesn't do one-hot encoding natively, but you can simulate it:

``` 
SELECT customer_id,
       MAX(CASE WHEN region = 'East' THEN 1 ELSE 0 END) AS region_east,
       MAX(CASE WHEN region = 'West' THEN 1 ELSE 0 END) AS region_west,
       MAX(CASE WHEN region = 'North' THEN 1 ELSE 0 END) AS region_north
FROM customers
GROUP BY customer_id;
```

If you need all possible values dynamically, do it in Python after the SQL step.

#### Reusable Features with Views and CTEs
To avoid repeating logic, you can define reusable layers:

``` 
CREATE VIEW customer_order_summary AS
SELECT customer_id,
       COUNT(*) AS num_orders,
       SUM(order_total) AS total_spent,
       AVG(order_total) AS avg_order_value
FROM orders
GROUP BY customer_id;
```

Then build features off the view:

``` 
SELECT c.*, o.total_spent
FROM customers c
LEFT JOIN customer_order_summary o ON c.customer_id = o.customer_id;
```

Feature engineering is where SQL becomes more than a query language. It becomes the engine behind reproducible, scalable data pipelines. By shaping raw tables into feature-rich datasets, you prepare for modeling, clustering, or forecasting --- without ever leaving the database.

#### Data Quality and Validation Checks
Before modeling or making business decisions, you need to make sure the data is clean. SQL is often your first line of defense against missing values, duplicates, mismatches, and outliers. Validation checks in SQL are fast, transparent, and easy to share with non-technical stakeholders.

#### Missing Values (NULLs)
Start by checking how many values are missing:

``` 
SELECT
  COUNT(*) AS total_rows,
  COUNT(column_name) AS non_null_rows,
  COUNT(*) - COUNT(column_name) AS null_rows
FROM table_name;
```

For column-by-column profiling:

``` 
SELECT
  COUNT(*) AS total,
  COUNT(customer_id) AS customer_id_present,
  COUNT(order_date) AS order_date_present,
  COUNT(order_total) AS order_total_present
FROM orders;
```

#### Null Imputation
To fill in missing values, you can use COALESCE:

``` 
SELECT COALESCE(order_total, 0) AS filled_order_total
FROM orders;
```

Or impute with averages:

``` 
SELECT
  order_id,
  COALESCE(order_total, AVG(order_total) OVER ()) AS imputed_total
FROM orders;
```

#### Detecting Duplicates
Find exact duplicates:

``` 
SELECT order_id, COUNT(*)
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

Detect near-duplicates (e.g., same customer, date, total):

``` 
SELECT customer_id, order_date, order_total, COUNT(*)
FROM orders
GROUP BY customer_id, order_date, order_total
HAVING COUNT(*) > 1;
```

#### Consistency Checks Across Tables
Check for orphaned foreign keys:

``` 
SELECT o.customer_id
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

This finds orders linked to nonexistent customers.

#### Outlier Detection
Find outliers using z-scores:

``` 
SELECT order_id, order_total,
       (order_total - AVG(order_total) OVER ()) / STDDEV(order_total) OVER () AS z
FROM orders
WHERE ABS((order_total - AVG(order_total) OVER ()) / STDDEV(order_total) OVER ()) > 3;
```

Or compare to percentiles:

``` 
WITH ranked AS (
  SELECT order_total,
         PERCENT_RANK() OVER (ORDER BY order_total) AS p_rank
  FROM orders
)
SELECT *
FROM ranked
WHERE p_rank < 0.01 OR p_rank > 0.99;
```

#### Distribution Profiling
Get a fast overview:

``` 
SELECT
  MIN(order_total),
  MAX(order_total),
  AVG(order_total),
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY order_total) AS median
FROM orders;
```

Or group by category:

``` 
SELECT region,
       COUNT(*) AS n,
       AVG(order_total) AS avg_total,
       STDDEV(order_total) AS std_total
FROM orders
GROUP BY region;
```

Data science depends on data you can trust. SQL gives you fast tools to audit and clean your inputs. These checks help you catch broken joins, wrong assumptions, and system bugs --- before they pollute your models or dashboards.

### SQL + Python for Modeling
SQL is excellent for transforming raw data into structured, clean tables. But it doesn't run regressions, build neural networks, or cross-validate models. That's where Python comes in. Together, they form a seamless pipeline: SQL shapes the data, Python models it.

#### Building Model-Ready Tables in SQL
Most modeling problems start with a question like: *what features predict churn?* You use SQL to pull the right features:

``` 
WITH customer_features AS (
  SELECT
    customer_id,
    MAX(order_date) AS last_order_date,
    COUNT(*) AS total_orders,
    AVG(order_total) AS avg_order_value,
    MAX(order_total) AS max_order
  FROM orders
  GROUP BY customer_id
)
SELECT c.customer_id, c.signup_date, f.*
FROM customers c
LEFT JOIN customer_features f ON c.customer_id = f.customer_id;
```

This is the dataset you'll use to train your model.

#### Reading SQL Tables into Python
Once you've prepared your final dataset in SQL, load it with pandas:

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://user:password@host:5432/database")
query = "SELECT * FROM customer_features;"
df = pd.read_sql(query, engine)
```

You now have a clean DataFrame with your target variable and predictors.

#### Minimal Feature Engineering in Python
In many cases, your SQL work reduces Python to:

```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

X = df.drop(columns=['customer_id', 'churned'])
y = df['churned']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
```

If you've done most of the cleaning, labeling, and encoding in SQL, your Python code becomes focused and reusable.

#### Dynamic SQL for Experiments
You can make SQL queries dynamic using Python string formatting:

``` 
region = 'West'
query = f"""
SELECT customer_id, order_total
FROM orders
WHERE region = '{region}'
"""
df = pd.read_sql(query, engine)
```

Or use Jinja2 for cleaner templating in more complex pipelines.

#### Writing Back to the Database
If you generate predictions in Python and want to store them back in SQL:

``` 
df_results.to_sql("predicted_churn", engine, if_exists="replace", index=False)
```

This helps share results with teams who work only in SQL or dashboards.

SQL and Python work best when you split responsibilities: SQL for shaping the data, Python for modeling and interpretation. SQL keeps your feature logic close to the source. Python makes the insights actionable.

#### Tips for Writing Maintainable SQL
Good SQL is readable, testable, and reusable. As your queries grow from quick filters to multi-CTE pipelines, the difference between a working query and a maintainable one becomes critical. Here's how to write SQL that future you --- or someone on your team --- can understand and build on.

#### Use Clear, Consistent Formatting
Write your SQL like code. Use indentation to make structure obvious.

Bad:

``` 
SELECT c.customer_id, c.name, o.order_total FROM customers c JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_total > 100;
```

Better:

``` 
SELECT
  c.customer_id,
  c.name,
  o.order_total
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_total > 100;
```

Put each major clause (`SELECT`, `FROM`, `JOIN`, `WHERE`, `GROUP BY`) on its own line. Indent nested queries and CASE statements.

#### Use Descriptive Aliases
Avoid one-letter aliases in production code unless it's a small query.

Bad:

``` 
SELECT a.name, b.total
FROM a JOIN b ON a.id = b.id;
```

Better:

``` 
SELECT
  customers.name,
  orders.total
FROM customers
JOIN orders ON customers.customer_id = orders.customer_id;
```

Or if brevity is needed:

``` 
SELECT
  c.name,
  o.total
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;
```

#### Use Common Table Expressions (CTEs)
If your query has multiple joins or subqueries, use `WITH` statements to modularize it.

``` 
WITH recent_orders AS (
  SELECT *
  FROM orders
  WHERE order_date > CURRENT_DATE - INTERVAL '30 days'
),
top_customers AS (
  SELECT customer_id, SUM(order_total) AS total_spent
  FROM recent_orders
  GROUP BY customer_id
)
SELECT c.customer_name, t.total_spent
FROM customers c
JOIN top_customers t ON c.customer_id = t.customer_id;
```

CTEs make each stage readable and easier to debug.

#### Avoid Repeating Logic
If you're using the same expression in multiple places, either alias it or compute it once in a CTE or view.

Bad:

``` 
SELECT
  order_total,
  (order_total - 50) / 10 AS z1,
  (order_total - 50) / 10 + 5 AS z2
FROM orders;
```

Better:

``` 
WITH standardized AS (
  SELECT
    order_id,
    (order_total - 50) / 10 AS z
  FROM orders
)
SELECT
  order_id,
  z,
  z + 5 AS z_plus_five
FROM standardized;
```

#### Comment Liberally
Explain why, not just what.

``` 
-- Calculate 30-day average per customer to track trends
WITH recent_orders AS (
  SELECT customer_id, order_total, order_date
  FROM orders
  WHERE order_date > CURRENT_DATE - INTERVAL '30 days'
)
```

Comments help others (and you, later) understand your assumptions.

#### Version and Share Your SQL
Keep long queries in `.sql` files under version control. Use Jupyter notebooks or markdown cells if sharing in notebooks. Reproducibility matters.

Readable SQL saves time. When queries grow, structure matters more than speed. Comments, clean formatting, and modular design turn your analysis into assets others can trust and reuse.

#### SQL is an Analytical Mindset
SQL is a way of thinking analytically --- about relationships between tables, about grouping and filtering, and about how data flows from raw transactions to actionable insight. If you can write a clean SQL query, you can trace a business question back to the rows that generate the answer.

Working in SQL forces clarity. You must name every column, specify every condition, and declare every transformation. There's no ambiguity, no hidden state. When you write `JOIN`, `WHERE`, `GROUP BY`, and `CASE`, you are encoding logic that mirrors the reasoning behind a dashboard metric, a data science feature, or a performance report.

SQL's declarative nature makes it collaborative. Analysts, engineers, and data scientists use the same syntax. A well-written query can serve as both code and documentation. And because SQL is so deeply embedded in the tools of modern data platforms learning to think in SQL gives you leverage anywhere structured data exists.

For data science, SQL remains the most efficient way to reshape, reduce, aggregate, and audit large volumes of data. It's not where you fit models or tune hyperparameters. But it is where you define the data that modeling depends on. Great features start in SQL. So do great questions.

When combined with Python, SQL becomes even more powerful. You can prepare features in-database, pull the results into pandas, train models, evaluate metrics, and return insights to a database or dashboard. You don't need to choose between SQL and Python. You need to know when to use each one.

SQL rewards precision and structure. And it scales! Learning SQL means you use it as a language for reasoning with data.
