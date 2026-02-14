# Python E2E ETL Pipeline

This is an ETL pipeline that

- `Extracts` data from `PostgresDB` using `SQLalchemy`
- `Transform` using `Pandas`
- `Modelled` after OneBigTable model
- `Loaded` back to a DB as a datamart report

## Requirements 

- Python 3.9 or higher

## System Setup

1. Clone the Repo

``` bash
    git clone {git_url}
```

2. Create a virtual ENV

``` bash
 python -m venv venv
```

3. Install the dependencies.

```bash
pip install -r requirements.txt
```