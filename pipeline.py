import logging
import os
from datetime import date
from decimal import Decimal, InvalidOperation

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


def validate_records(records):
    required_fields = {"date", "base", "quote", "rate"}

    for row_number, record in enumerate(records, start=1):
        missing_fields = required_fields - record.keys()
        if missing_fields:
            raise ValueError(
                f"Record {row_number} is missing fields: {missing_fields}"
            )

        try:
            date.fromisoformat(record["date"])
            rate = Decimal(str(record["rate"]))
        except (TypeError, ValueError, InvalidOperation) as error:
            raise ValueError(
                f"Record {row_number} has an invalid date or rate."
            ) from error

        if not isinstance(record["base"], str) or len(record["base"]) != 3:
            raise ValueError(f"Record {row_number} has an invalid base currency.")

        if not isinstance(record["quote"], str) or len(record["quote"]) != 3:
            raise ValueError(f"Record {row_number} has an invalid quote currency.")

        if not rate.is_finite() or rate <= 0:
            raise ValueError(f"Record {row_number} has an invalid exchange rate.")


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

    validate_records(records)
    logger.info("Validated all %d exchange-rate records", len(records))

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