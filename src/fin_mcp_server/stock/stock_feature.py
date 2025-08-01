import pandas as pd
import talib as ta
import numpy as np

# Date,Close,High,Low,Open,Volume
def create_tech_indiction_features(df: pd.DataFrame, config: dict):
    default_config = {
        "ema_period": [5, 10, 20, 50, 100],
        "sma_period": [20, 100],
        "macd_slope": [3, 5, 10],
        "Volumeatility_window": [30]
    }
    if config is not None:
        default_config.update(config)
    data = df.copy()
    # 安全地处理数据类型转换，避免处理日期列
    date_columns = [col for col in data.columns if 'date' in col.lower() or 'time' in col.lower()]
    
    # 只转换非日期列的object类型列
    object_columns = data.select_dtypes(include=['object']).columns.tolist()
    columns_to_convert = [col for col in object_columns if col not in date_columns]
    try:
        # 确保日期列是datetime类型
        for date_col in date_columns:
            if date_col in data.columns:
                try:
                    data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
                except Exception as e:
                    print(f"转换日期列 {date_col} 时出错: {e}")
        
        # 安全地转换数据类型
        for col in columns_to_convert:
            try:
                data[col] = pd.to_numeric(data[col], errors='coerce')
            except Exception:
                print(f"警告：无法转换列 {col} 的数据类型")
                pass  # 如果转换失败，则保持原样
        for period in default_config['ema_period']:
            data[f'EMA{period}'] = ta.EMA(data['Close'], timeperiod=period)

        for period in default_config['sma_period']:
            data[f'SMA{period}'] = ta.SMA(data['Close'], timeperiod=period)

        data['RSI'] = ta.RSI(data['Close'], timeperiod=14)

        data['MACD'], data['MACD_SIGNAL'], data['MACD_HIST'] = ta.MACD(data['Close'],
                                                                    fastperiod=12,
                                                                    slowperiod=26,
                                                                    signalperiod=9)
        data['UpperBB'], data['MiddleBB'], data['LowerBB'] = ta.BBANDS(data['Close'], timeperiod=20)
        data['OBV'] = ta.OBV(data['Close'], data['Volume'])
        data['OBV_SMA'] = ta.SMA(data['OBV'], timeperiod=20)
        data['ATR'] = ta.ATR(data['High'], data['Low'], data['Close'], timeperiod=14)
        data['MOM'] = ta.MOM(data['Close'], timeperiod=10)
        data['CCI'] = ta.CCI(data['High'], data['Low'], data['Close'], timeperiod=14)
        data['PSY'] = data['Close'].rolling(12).apply(lambda x: sum(x > x.shift(1)) / 12 * 100)
        data['K'], data['D'] = ta.STOCH(data['High'].values, data['Low'].values, data['Close'].values, fastk_period=9,
                                        slowk_period=3,
                                        slowk_matype=ta.MA_Type.SMA, slowd_period=3, slowd_matype=ta.MA_Type.SMA)
        data['J'] = 3 * data['K'] - 2 * data['D']
    except Exception as e:
        print(f"计算技术指标时出错: {e}")
        import traceback
        traceback.print_exc()
        return data

    return data.replace([np.inf, -np.inf], np.nan).ffill().dropna()