"""Data handler module for loading and processing data."""

from datetime import datetime
from typing import Optional, Union

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from dotenv import load_dotenv
from securities_load.securities.postgresql_database_functions import sqlalchemy_engine
from securities_load.securities.securities_table_functions import retrieve_ohlcv_from_to


class DataHandler:
    """Data handler class for loading and processing data."""

    def __init__(
        self,
        symbol: Union[str, list[str]],
        exchange_code: Optional[str] = None,
        period: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ):
        """Initialize the data handler."""
        self.symbol = list(map(str.upper, symbol))
        self.exchange_code = exchange_code
        self.timeframe = TimeFrame(amount=1, unit=TimeFrameUnit(period))
        self.start = start
        self.end = end

    def load_data_from_alpaca(self) -> pd.DataFrame:
        """Load equity data."""
        stock_client = StockHistoricalDataClient(
            "PKMDAQ4V5CCOOPF8BUUR", "HjCdK5Cgsr7vTMCveXibh4txCY1VjBfQvO6Ggw68"
        )
        # Set up the parameters
        request_params = StockBarsRequest(
            symbol_or_symbols=self.symbol,
            timeframe=self.timeframe,  # type: ignore
            start=self.start,
            end=self.end,
        )
        # Get the stock data
        # Returns a BarSet which is a dictionary keyed by symbol with a List of Bars
        # A Bar is a includes the symbol, timestamp, open, high, low, close, volume and
        # optionally the trade count, vwap and exchange

        bars = stock_client.get_stock_bars(request_params)

        # Convert it to a dataframe
        data = bars.df  # type: ignore
        data.drop(columns=["trade_count", "vwap"], inplace=True)
        data.dropna(inplace=True)
        data = data[~data.index.duplicated()]

        # if len(self.symbol_or_symbols) > 1:
        #     data = data.reset_index().set_index("symbol")
        #     result = {symbol: data.loc[symbol] for symbol in self.symbol_or_symbols}
        #     return {
        #         key: value if isinstance(value, pd.DataFrame) else value.iloc[0]
        #         for key, value in result.items()
        #     }
        # print(f"Data loaded from alpaca type: {type(data)}")
        # print(f"Load data from alpaca f{data.head()}")
        # return data
        data = data.reset_index().set_index("timestamp")

        return data

    def load_data_from_csv(self, file_path) -> pd.DataFrame:
        """Load data from CSV file."""
        return pd.read_csv(file_path, index_col="date", parse_dates=True)

    def load_data_from_local_database(self) -> pd.DataFrame:
        """Load data from a local database."""
        if isinstance(self.symbol, str):
            ticker = self.symbol
        elif isinstance(self.symbol, list):
            ticker = self.symbol[0]  # Assuming we want the first symbol in the list
        else:
            raise ValueError("Symbol must be a string or a list of strings.")
        if self.exchange_code is None:
            raise ValueError(
                "Exchange code must be provided for local database retrieval."
            )
        if self.start is None or self.end is None:
            raise ValueError(
                "Start and end dates must be provided for local database retrieval."
            )

        start_string_date = datetime.strftime(self.start, "%Y-%m-%d")
        end_string_date = datetime.strftime(self.end, "%Y-%m-%d")

        load_dotenv()
        engine = sqlalchemy_engine()
        return retrieve_ohlcv_from_to(
            engine,
            exchange_code=self.exchange_code,
            ticker=ticker,
            start_date=start_string_date,
            end_date=end_string_date,
        )
        return retrieve_ohlcv_from_to(
            engine,
            exchange_code=self.exchange_code,
            ticker=ticker,
            start_date=start_string_date,
            end_date=end_string_date,
        )
