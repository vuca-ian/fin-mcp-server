from .stock_feature import create_tech_indiction_features
from ..utils.plot import plot_kline
import logging
import os
import pandas as pd
import yfinance as yf

class Stock:
    def __init__(self, symbol, stock_config:dict, config:dict):
        self.logger = logging.getLogger("fin_stock")
        self.symbol = symbol
        self.config = config
        self.source = stock_config['source']
        self.temp_dir = stock_config['temp_dir']
        self._data = self.get_yahoo_data(symbol)
    
    def get_yahoo_data(self, symbol: str):
        """
        get data from Yahoo Finance
        """
        data = yf.download(symbol, period="max", auto_adjust=True, timeout=30)
        if data.empty:
            raise ValueError(f"No data found for symbol: {symbol}")
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)  # 删除第一层（如 'Price'）
            data = data.dropna(axis=1, how='all')     # 删除全空列（如 'index'）
        data.reset_index(inplace=True)
        return data


    def plot_with_tech_indicators(self, windows:int = 30):
        data = create_tech_indiction_features(self._data, self.config)
        if data.empty:
            self.logger.warning("警告：没有数据可用于绘图")
            return None
        actual_windows = min(int(windows), len(data))
        if actual_windows <= 0:
            self.logger.warning("警告：没有足够的数据进行绘图")
            return None
        # 获取最后一行数据作为当前点
        if len(data) > 0:
            current_data = data.iloc[-1]  # 使用iloc[-1]获取Series而不是DataFrame
        else:
            current_data = data.iloc[0] if len(data) > 0 else None
            
        if current_data is None:
            self.logger.warning("警告：无法获取当前数据点")
            return None
        plot_path = os.path.join(os.getcwd(), self.temp_dir)
        chart_path = plot_kline(data[-windows:], current_data, plot_path, self.symbol)
        return chart_path


    @property
    def data(self):
        return self._data
    