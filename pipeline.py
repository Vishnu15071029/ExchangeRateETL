import logging
import os

import pyodbc
import requests
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

API_URL = "https://api.frankfurter.dev/v2/rates"
API_PARAMS = {
    "base": "USD",
    "quotes": "INR,EUR,GBP",
}


def main():
    logger.info("Starting exchange-rate pipeline")

    load_dotenv()
    connection_string = os.getenv("SQL_CONNECTION_STRING")

    if not connection_string:
        raise ValueError("SQL_CONNECTION_STRING is missing. Check the .env file.")

    response = requests.get(API_URL, params=API_PARAMS, timeout=10)
    response.raise_for_status()
    records = response.json()
    logger.info("Received %d exchange-rate records from the API", len(records))

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
        logger.info("Loaded %d exchange-rate records into SQL Server", len(records))

    except pyodbc.Error:
        logger.exception("Database load failed; rolling back the transaction")
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()