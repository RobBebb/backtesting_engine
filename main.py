"""Main module for running the backtester."""

from datetime import datetime

from backtesting_engine.data_handler import DataHandler
from backtesting_engine.engine import Engine
from backtesting_engine.strategy import Strategy
from backtesting_engine.utils import AlpacaPeriod


def main():
    """Example usage of the backtesting_engine."""

    # class BuyAndSellSwitch(Strategy):
    #     def on_bar(self):
    #         if self.position_size == 0:
    #             self.buy("AAPL", 2)
    #             # print(self.current_idx, "buy")
    #         else:
    #             self.sell("AAPL", 2)
    #             # print(self.current_idx, "sell")

    # class BuyAndSellSwitch(Strategy):
    #     def on_bar(self):
    #         if self.position_size == 0:
    #             limit_price = self.close * 0.995
    #             self.buy_limit("AAPL", size=100, limit_price=limit_price)
    #             print(self.current_idx, OrderSide.BUY)
    #         else:
    #             limit_price = self.close * 1.005
    #             self.sell_limit("AAPL", size=100, limit_price=limit_price)
    #             print(self.current_idx, OrderSide.SELL)

    # class SMACrossover(Strategy):
    #     def on_bar(self):
    #         # print(f"Current index Type: {type(self.current_idx)}")
    #         # print(f"Current index: {self.current_idx}")
    #         order_size: int = 1
    #         limit_price: float = 0.0
    #         if self.data is None:
    #             raise ValueError("No data has been added to the engine for _get_stats.")
    #         # print(f"self.data: {self.data.head()}")
    #         if self.current_idx is None:
    #             raise ValueError(
    #                 "No current_idx has been added to the strategy for buy."
    #             )
    #         if self.cash is None:
    #             raise ValueError("No cash has been added to the strategy for buy.")

    #         if self.data.loc[self.current_idx].sma_12 is None:
    #             raise ValueError("No sma_12 has been added to the strategy for buy.")
    #         if self.data.loc[self.current_idx].sma_24 is None:
    #             raise ValueError("No sma_24 has been added to the strategy for buy.")
    #         sma_12 = self.data.at[self.current_idx].sma_12
    #         sma_24 = self.data.loc[self.current_idx].sma_24
    #         # print(f"Data: {self.data.loc[self.current_idx]}")
    #         if self.position_size == 0:
    #             if sma_12 > sma_24:  # type: ignore
    #                 limit_price = self.close * 0.995
    #                 # BUY AS MANY SHARES AS WE CAN!
    #                 order_size = self.cash / limit_price
    #                 self.buy_limit("AAPL", size=order_size, limit_price=limit_price)
    #         elif sma_12 < sma_24:  # type: ignore
    #             limit_price = self.close * 1.005
    #             self.sell_limit(
    #                 "AAPL", size=self.position_size, limit_price=limit_price
    #             )

    class SMACrossover(Strategy):
        def on_bar(self):
            if self.data is None:
                raise ValueError("No data has been added to the engine for _get_stats.")
            if self.cash is None:
                raise ValueError("No cash has been added to the strategy for buy.")
            order_size: float = 1.0
            limit_price: float = 0.0
            if self.position_size == 0:
                if (
                    self.data.at[self.current_idx, "sma_12"]
                    > self.data.at[self.current_idx, "sma_24"]
                ):
                    limit_price = self.close * 0.995
                    # BUY AS MANY SHARES AS WE CAN!
                    order_size = self.cash / limit_price
                    self.buy_limit("AAPL", size=order_size, limit_price=limit_price)
            elif (
                self.data.at[self.current_idx, "sma_12"]
                < self.data.at[self.current_idx, "sma_24"]
            ):
                limit_price = self.close * 1.005
                self.sell_limit(
                    "AAPL", size=self.position_size, limit_price=limit_price
                )

    exchange_code = "XNAS"
    symbol = ["AAPL"]
    # symbol_or_symbols = "NFLX"
    period = AlpacaPeriod.DAY.value
    start = datetime(2022, 1, 1)
    end = datetime(2022, 12, 31)

    # data = DataHandler(
    #     symbol=symbol, exchange_code=exchange_code, period=period, start=start, end=end
    # ).load_data_from_alpaca()
    data = DataHandler(
        symbol=symbol, exchange_code=exchange_code, period=period, start=start, end=end
    ).load_data_from_local_database()

    print(f"Data loaded from local database: {data.head()}")

    # Returna a DF with date as key and OHLCV data
    engine = Engine(initial_cash=100000)

    data["sma_12"] = data.close.rolling(12).mean()
    data["sma_24"] = data.close.rolling(24).mean()
    # Add two columns to the DF
    engine.add_data(data)
    engine.add_strategy(SMACrossover())
    # engine.add_strategy(BuyAndSellSwitch())
    stats = engine.run()
    print(stats)
    # print(engine._get_stats())
    engine.plot()


if __name__ == "__main__":
    main()
