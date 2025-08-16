import mplfinance as mpf
from matplotlib import pyplot as plt
from matplotlib.legend import Legend
import pandas as pd
import os 
from datetime import datetime
def plot_kline(df: pd.DataFrame, cur:pd.DataFrame, path:str, symbol:str):
    os.makedirs(path, exist_ok=True)
    
    try:
        df = df.copy().set_index('Date')
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
    except Exception as e:
        print(f"日期格式转换错误: {e}")
        df.index = pd.to_datetime(df.index, infer_datetime_format=True)
    # 处理当前数据点
    if isinstance(cur, pd.DataFrame):
        current_data = cur.iloc[0]
    else:
        current_data = cur
    current_date = current_data['Date'] if isinstance(current_data['Date'], (str, pd.Timestamp)) else current_data['Date'].iloc[0]
    try:
        if isinstance(current_date, pd.Timestamp):
            save_date = current_date.strftime('%Y-%m-%d')
        else:
            # 处理字符串日期
            save_date = str(current_date)[:10]  # 取前10个字符作为日期
    except Exception:
        save_date = "unknown"
    # 创建专业级K线配置
    mc = mpf.make_marketcolors(
        up='#00FF00',  # 阳线颜色
        down='#FF0000', # 阴线颜色
        edge='black',   # K线边框
        wick={'up':'green','down':'red'}, # 影线颜色
        volume='#1F77B4' # 成交量颜色
    )
    style = mpf.make_mpf_style(
        base_mpf_style='yahoo',
        rc={
            'font.size': 10,
            'axes.labelsize': 11,
            'axes.titlesize': 14,
        },
        marketcolors=mc,
        gridstyle=':',      # 网格样式
        y_on_right=False,    # Y轴位置
        # figure_facecolor='#FFFFFF',  # 图表背景色
        gridaxis='horizontal'  # 只显示水平网格线
    )
    # 添加技术指标
    apds = [
        mpf.make_addplot(df['EMA5'], color='orange', width=1.5, label='EMA5'),
        mpf.make_addplot(df['EMA20'], color='blue', width=1.5, label='EMA20'),
        mpf.make_addplot(df['UpperBB'], color='grey', linestyle='--', label='UpperBB'),
        mpf.make_addplot(df['LowerBB'], color='grey', linestyle='--', label='LowerBB'),
        # MACD指标
        mpf.make_addplot(df['MACD'], panel=2, color='#1f77b4', ylabel='MACD', label='MACD'),
        mpf.make_addplot(df['MACD_SIGNAL'], panel=2, color='#ff7f0e', label='MACD_SIGNAL'),
        mpf.make_addplot(df['MACD_HIST'], type='bar', panel=2, color='#4dbeee', label='MACD_HIST',
                        alpha=0.5, secondary_y=False),
        # MACD指标
        mpf.make_addplot(df['K'], panel=3, color='#1f77b4', ylabel='KDJ', label='K'),
        mpf.make_addplot(df['D'], panel=3, color='#ff7f0e', label='D'),
        mpf.make_addplot(df['J'], panel=3, color='#4dbeee',
                        alpha=0.5, secondary_y=False, label='J'),
        # RSI指标
        mpf.make_addplot(df['RSI'], panel=4, color='#2ca02c', ylabel='RSI', label='RSI',ylim=(0, 100)),
        # OBV指标
        mpf.make_addplot(df['OBV'], panel=5, color='#9467bd', ylabel='OBV', label='OBV'),
        mpf.make_addplot(df['OBV_SMA'], panel=5, color='#ff7f0e', label='OBV_SMA20'),
        # CCI指标
        mpf.make_addplot(df['CCI'], panel=6, color='gold', ylabel='CCI',  label='CCI')
    ]
    # 计算合适的Y轴范围以包含布林带
    price_columns = ['Open', 'High', 'Low', 'Close', 'UpperBB', 'LowerBB']
    available_price_columns = [col for col in price_columns if col in df.columns]

    if available_price_columns:
        price_data = df[available_price_columns]
        min_price = price_data.min().min()
        max_price = price_data.max().max()
        
        # 添加一些边距
        price_range = max_price - min_price
        margin = price_range * 0.05  # 5%的边距
        ylim = (min_price - margin, max_price + margin)
    else:
        ylim = None
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    if len(df) > 1:
        prev_close = df['Close'].iloc[-2]
        current_close = df['Close'].iloc[-1]
        price_change = current_close - prev_close
        price_change_pct = (price_change / prev_close) * 100
        price_info = f"{current_close:.2f} ({'+' if price_change >= 0 else ''}{price_change:.2f}, {'+' if price_change_pct >= 0 else ''}{price_change_pct:.2f}%)"
    else:
        price_info = f"{df['Close'].iloc[-1]:.2f}"
    # 专业级绘图参数
    fig, axlist = mpf.plot(df,
             type='candle',
             style=style,
             update_width_config=dict(
                candle_linewidth=0.8,
                volume_width=0.8
             ),
             addplot=apds,
             volume=True,
             title={
                 "title": f'{symbol} -Professional Technical Analysis Chart\n{save_date} | Close: {price_info} | Updated: {current_time}',
                 "va": 'bottom',
                 "y":0.98
             },
             ylabel='Price',
             ylabel_lower='Volume',
             figsize=(15, 18),
             figratio=(12, 6),
             figscale=1.5,
             panel_ratios=(4, 1, 1, 1,1, 1, 1),
            #  datetime_format='%Y-%m-%d',
             xrotation=45,
             ylim=ylim,
             tight_layout=True,
             returnfig=True
                           )
    ax = axlist[0]  # 获取主坐标轴
    x_pos = df.index.get_loc(cur['Date'])  # 转换为数值坐标
    ax.scatter(x_pos, cur['High']*1.008, marker='v', color='gold',  s=100, zorder=5,edgecolors='black', label='Current Point')
    # 添加箭头标注
    ax.annotate(f"Latest\nO:{cur['Open']:.2f}\nH:{cur['High']:.2f}\nL:{cur['Low']:.2f}\nC:{cur['Close']:.2f}",
                xy=(x_pos, cur['High'] * 1.001),
                xytext=(x_pos - 3, cur['High']* 1.01),
                arrowprops=dict(arrowstyle="->", color='gold', lw=1.2),
                bbox=dict(pad=0.2, facecolor='gold', alpha=0.9,edgecolor='#2C3E50'),
                fontsize=9,
                ha='center')
    # RSI 添加水平线，70、30两条水平线
    try:
        if len(axlist) > 3:
            macd_ax = axlist[3]  # MACD在panel=2，但在axlist中是第4个元素（索引3）
            handles, labels = macd_ax.get_legend_handles_labels()
            if handles:
                macd_legend = Legend(macd_ax, handles, labels,
                                   loc='upper left',
                                   frameon=True,
                                   framealpha=0.9,
                                   borderaxespad=0.5,
                                   fontsize=8)
                macd_ax.add_artist(macd_legend)
    except Exception as e:
        print(f"添加MACD图例时出错: {e}")
    ax_rsi = axlist[8]
    ax_rsi.axhline(70, color='#E74C3C', linestyle='--', linewidth=1, label='70 ', alpha=0.7)
    ax_rsi.axhline(30, color='#2ECC71', linestyle='--', linewidth=1, label='30 ', alpha=0.7)
    ax_rsi.text(0.02, 0.8, 'Overbought (70)',
           transform=ax_rsi.transAxes,
           color='#E74C3C',
           fontsize=9,
           verticalalignment='top')

    ax_rsi.text(0.02, 0.2, 'Oversold (30)',
               transform=ax_rsi.transAxes,
               color='#2ECC71',
               fontsize=9,
               verticalalignment='bottom')
    # 在所有子图绘制垂直线
    for ax in axlist:
        ax.axvline(x=x_pos,
                  color='#FF6B6B',
                  linestyle='--',
                  alpha=0.5,
                  linewidth=1.5,
                  zorder=3)
     # 进一步调整子图间距
    fig.subplots_adjust(
        hspace=0.08,  # 水平间距压缩到最小
        left=0.06,    # 左侧边距
        right=0.94,   # 右侧边距
        top=0.98     # 顶部边距
    )
    handles, labels = ax.get_legend_handles_labels()
    leg = Legend(ax, handles, labels,
            loc='best',
            frameon=True,
            framealpha=0.9,
            borderaxespad=0.5)
    ax.add_artist(leg)
    
    save_path = f"{path}/kline-{symbol}-{save_date}.png"
    plt.savefig(save_path,dpi=300, bbox_inches='tight')
    plt.close()
    return save_path,f"kline-{symbol}-{save_date}.png"