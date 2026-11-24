import os

import pyodbc
import requests
from dotenv import load_dotenv


API_URL = "https://api.frankfurter.dev/v2/rates"
API_PARAMS = {
    "base": "USD",
    "quotes": "INR,EUR,GBP",
}


def main():
    load_dotenv()
    connection_string = os.getenv("SQL_CONNECTION_STRING")

    if not connection_string:
        raise ValueError("SQL_CONNECTION_STRING is missing. Check the .env file.")

    response = requests.get(API_URL, params=API_PARAMS, timeout=10)
    response.raise_for_status()
    records = response.json()

    if not records:
        raise ValueError("The API returned no exchange-rate records.")

    connection = pyodbc.connect(connection_string, timeout=5)

    try:
        cursor = connection.cursor()

        for record in records:
                            cursor.execute(
                """
                UPDATE dbo.ExchangeRates
                SET exchange_rate = ?
                WHERE rate_date = ?
                  AND base_currency = ?
                  AND quote_currency = ?;

                IF @@ROWCOUNT = 0
                BEGIN
                    INSERT INTO dbo.ExchangeRates
                        (rate_date, base_currency, quote_currency, exchange_rate)
                    VALUES (?, ?, ?, ?);
                END;
                """,
                record["rate"],
                record["date"],
                record["base"],
                record["quote"],
                record["date"],
                record["base"],
                record["quote"],
                record["rate"],
            )

        connection.commit()
        print(f"Loaded {len(records)} exchange-rate records into SQL Server.")

    except pyodbc.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()