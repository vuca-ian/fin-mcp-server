from mcp.server import  FastMCP
from mcp.types import TextContent
from .stock import Stock
from .utils.llm import create_llm_client
from .utils.image import encode_image_to_base64
from .utils.env import load_config
import json
import logging
import os



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger("fin_mcp_server")


global_config = load_config()
mcp_config = global_config.mcp
stock_config = global_config.stock
mcp = FastMCP("fin_mcp_server", **mcp_config)
llm_config = global_config.llm
llm_client = create_llm_client(llm_config)

@mcp.tool(name="get_compony_info", description="获取公司信息")
async def get_compony_info(symbol: str):
    try:
        logger.info(f"Getting data for {symbol}")
        stock = Stock(symbol=symbol, stock_config=stock_config, config = {})
        data = stock.get_company_info(symbol)
        return [TextContent(type='text', text=json.dumps(data))]
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return [TextContent(type='text', text=json.dumps({"error": str(e)}))]

@mcp.tool(name="get_data", description="获取股票数据,周期默认为 30d, 也可以取值 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
async def get_data(symbol: str, period: str = "30d"):
    """Fetch the data from yfinance through a company name

    Args:
        symbol: The symbol name to fetch the stock data
        period: The period to fetch the data for. Defaults to "30d". Can be one of "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max" of rows to return
    """
    try:
        logger.info(f"Getting data for {symbol}")
        stock = Stock(symbol=symbol, stock_config=stock_config, config = {})
        data = stock.get_history_data(period)
        return [TextContent(type='text', text=data.to_markdown())]
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return [TextContent(type='text', text=json.dumps({"error": str(e)}))]

@mcp.tool(name="get_quarterly_balance_sheet", description="获取股票的季度资产负债表")
async def get_quarterly_balance_sheet(symbol: str):
    """Fetch the data from yfinance through a company name

    Args:
        symbol: The symbol name to fetch the stock data
    """
    try:
        logger.info(f"Getting data for {symbol}")
        stock = Stock(symbol=symbol, stock_config=stock_config, config = {})
        data = stock.get_quarterly_balance_sheet()
        return [TextContent(type='text', text=data.to_markdown())]
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return [TextContent(type='text', text=json.dumps({"error": str(e)}))]

@mcp.tool(name="generate_fin_report", description="根据股票数据和k线图生成专业的金融分析报告")
async def generate_fin_report(symbol: str, windows:int=50):
    """ Generate financial analysis report based on specified company stock information
    Args:
        symbol: The symbol name to fetch the stock data
        windows: 图表显示的K线窗口大小
    """
    try:
        logger.info(f"Generating financial report for {symbol} with {windows} windows")
        stock = Stock(symbol=symbol, stock_config=stock_config, config = {})
        chart_path,image_name = stock.plot_with_tech_indicators(windows=windows)
        if not chart_path or not os.path.exists(chart_path):
            error_msg = f"图表生成失败: {chart_path}"
            logger.error(error_msg)
            return [TextContent(type='text', text=json.dumps({"error": error_msg}))]
        # 将图片转换为base64编码
        encoded_image = encode_image_to_base64(chart_path)
        if not encoded_image:
            error_msg = "图片编码失败"
            logger.error(error_msg)
            return [TextContent(type='text', text=json.dumps({"error": error_msg}))]
        
        system_message = (
                "你是一位专业的金融分析师，擅长技术分析和股票市场解读。\n"
                "请根据提供的K线图和技术指标进行详细分析，包括："
                "1. 价格趋势分析（短期、中期、长期趋势）\n"
                "2. 关键技术指标解读（MACD、RSI、KDJ、布林带、ATR等3个以上指标协同验证）\n"
                "3. 量价时空分析（结合波动周期与成交量分布）\n"
                "4. 动态支撑压力位计算（斐波那契+波动率ATR）\n"
                "5. 风险预警信号（黑天鹅事件概率模型）\n"
                "6. 风险收益比计算（基于ATR计算潜在盈亏比）\n"
                "7. 交易策略建议（包含止盈止损位，明确入场/离场条件)\n"
                "请提供专业、详细的分析报告。"
                "附加要求："
                "- 使用机构级术语（如\"轧空\"、\"多空转换点\"、\"背离\"）"
                "- 标注置信度等级（A/B/C级）"
                "- 区分日内/趋势策略适用性"
                "- 引用历史相似形态表现（如可提供）"
                "- 提供具体的价格目标位和止损位",
                "- 评估当前市场环境对策略的影响"
                "输出报告格式，以markdown格式输出，要求输出报告内容参考如下："
                "# [股票代码] [公司名称] - 金融分析报告\n"
                "*报告日期: [YYYY-MM-DD]*\n\n"
                "## 1. 核心指标概览\n"
                "| 指标 | 当前值 | 变化率 | 说明 |\n"
                "|------|--------|--------|------|\n"
                "| 当前股价 | $XX.XX | +X.XX% | 相比前一日收盘价 |\n"
                "| 开盘价 | $XX.XX | +X.XX% | 今日开盘价格 |\n"
                "| 最高价 | $XX.XX | +X.XX% | 今日最高价格 |\n"
                "| 最低价 | $XX.XX | +X.XX% | 今日最低价格 |\n"
                "| 成交量 | XXX万 | +X.XX% | 相比昨日成交量 |\n"
                "| 换手率 | XX.XX% | +X.XX% | 昨日换手率 |\n"
                
                "## K线图"
                "[图片地址]"
                "## 2. 基本面分析\n"
                "## 3. 风险提示\n"
                "## 4. 市场情绪分析\n"
                "## 5. 投资建议\n"
        )
        messages = [
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": encoded_image
                        }
                    },
                    {
                        "type": "text",
                        "text": f"请分析 {symbol} 的k线技术图表[图片地址：{stock_config.get("public_base_url")}/static/{image_name}]，提供详细的技术分析报告。图表显示了最近 {windows} 个交易日的数据。"
                    },
                ],
            }
        ]
        llm_response, _ = await llm_client.chat_completions(
            messages,
            temperature=llm_config.get("temperature", 0.7),
            max_tokens=llm_config.get("max_tokens", 4096),
        )
        # 处理LLM响应
        if hasattr(llm_response, 'content'):
            analysis_result = llm_response.content
        else:
            analysis_result = str(llm_response)
        logger.info(f"Successfully generated analysis report for {symbol}")
        return [TextContent(type='text', text=analysis_result)]
    except Exception as e:
        error_msg = f"生成报告时出错: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(type='text', text=json.dumps({"error": error_msg}))]


def main():
    mcp.run(transport=global_config.transport)
