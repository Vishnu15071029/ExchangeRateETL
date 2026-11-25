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
