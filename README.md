# ExchangeRateETL

A beginner Data Engineering project that extracts currency exchange rates from the Frankfurter API, validates and transforms the data with Python, and loads it into Microsoft SQL Server.

## Data flow

Frankfurter API -> Python extraction -> validation -> transformation -> SQL Server

## Current features

- Fetches USD exchange rates for EUR, GBP, and INR.
- Retries temporary API connection failures and timeouts up to 3 attempts.
- Validates required fields, dates, currency codes, and positive rates.
- Converts API values into consistent Python types before loading.
- Inserts new records or updates existing records without creating duplicates.
- Logs pipeline progress with timestamps.
- Uses environment variables for the SQL Server connection string.

## Technology

- Python
- Frankfurter REST API and JSON
- Microsoft SQL Server
- `pyodbc`
- `requests`
- `python-dotenv`
- `logging`
- Git and GitHub

## Setup on Windows

### Prerequisites

- Python
- Microsoft SQL Server
- ODBC Driver 18 for SQL Server
- Git

### 1. Create the database and table

In SQL Server Management Studio (SSMS), create the database:

```sql
CREATE DATABASE ExchangeRateETL;
GO
```

Then run the table creation script [sql/create_exchange_rates_table.sql](sql/create_exchange_rates_table.sql):

```sql
USE ExchangeRateETL;

IF OBJECT_ID(N'dbo.ExchangeRates', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.ExchangeRates (
        rate_date DATE NOT NULL,
        base_currency CHAR(3) NOT NULL,
        quote_currency CHAR(3) NOT NULL,
        exchange_rate DECIMAL(18, 8) NOT NULL,
        loaded_at DATETIME2(0) NOT NULL
            CONSTRAINT DF_ExchangeRates_loaded_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_ExchangeRates
            PRIMARY KEY (rate_date, base_currency, quote_currency),

        CONSTRAINT CK_ExchangeRates_exchange_rate_positive
            CHECK (exchange_rate > 0)
    );
END;
```

### 2. Configure the virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
SQL_CONNECTION_STRING="DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=ExchangeRateETL;Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes"
```

### 4. Verify connections

Check the API endpoint and SQL Server connection:

```powershell
python api_check.py
python db_connection_check.py
```

### 5. Run the pipeline

```powershell
python pipeline.py
```
