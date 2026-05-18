# Using SQL for Data Science and Analytics

This folder contains code and resources for the Medium article:
[Using SQL for Data Science and Analytics](https://medium.com/@kylejones_47003/sqlfordatascience)

## Business context

SQL is the backbone of data science work in companies that rely on structured data. Despite the growing ecosystem of Python, R, and cloud-native tools, most real-world datasets still live in relational databases. These could be traditional systems like PostgreSQL and Oracle, data warehouses like Redshift, or cloud-native services like BigQuery. Wherever the data lives, SQL is usually the first gate you must pass through to work with it.

SQL excels at expressing relationships between entities. Whether you're calculating churn rates, aggregating sales by geography, or building user cohorts, these tasks begin with structured queries. SQL lets you describe what you want, not how to compute it --- this declarative style is a strength. You ask the database to give you "sales by region and quarter," and it handles the execution plan. You don't have to worry about iterating over rows or indexing strategies.

SQL can power end-to-end analytical pipelines. You can calculate features for machine learning, perform exploratory analysis, validate data quality, and generate business metrics --- all inside SQL. It often outperforms Python in terms of speed when data volumes grow, because databases are optimized for parallelized set operations.

## Disclaimer

Educational/demo code only. Not financial, safety, or engineering advice. Use at your own risk. Verify results independently before any production or operational use.

## License

MIT — see [LICENSE](LICENSE).