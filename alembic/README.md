## Alembic

We use [alembic](https://alembic.sqlalchemy.org/en/latest/) to manage our database migrations for Fareview.

### Steps to generate migration

1. `alembic revision --autogenerate -m "A concise commit message."`
2. Check the auto-generated migration file to see if it makes any sense
3. Once confirm, run `alembic upgrade head` to apply the database migration (Otherwise simply just delete the generated migration file)

_NOTE: You can always use `alembic downgrade -1` to revert any database migrations_

### How to generate migration for an existing database

-   https://stackoverflow.com/a/56651578/10067850
-   Remember to run `alembic stamp head` to tell `sqlalchemy` that the current migration represents the state of the database

## Examples of SQL Queries

```sh
psql -v brand="'<brand>'" postgres -h 127.0.0.1 -d fareview -f <path>/<filename>.sql

# E.g.:

$ pwd
/home/jerryng/Personal/fareview

psql -v brand="'heineken'" postgres -h 127.0.0.1 -d fareview -f alembic/examples/get_all_by_brand.sql
```

-   [Count the number of historical prices of all available products](./examples/get_number_of_prices.sql)
-   [Get the price list of all available products](./examples/get_all_latest.sql)
-   [Get current and previous price in the same table for a single brand](./examples/get_all_by_brand.sql)
