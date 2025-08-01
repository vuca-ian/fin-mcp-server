from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
import logging
import uvicorn
import json
import os
import yaml
from argparse import Namespace
from fin_mcp_server.stock import Stock

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s -  %(filename)s:%(lineno)d - %(message)s"
)
logger = logging.getLogger("FIN_MCP_SERVER")
async def startup_event():
    logger.info("Application initialized")
async def shutdown_event():
    logger.info("Application shutting down")

def load_config(yaml_file:str = None, encoding: str = "utf-8"):
    config_path = os.getenv("YML", yaml_file)
    try:
        with open(config_path, 'r',encoding = encoding) as file:
            config = yaml.safe_load(file)
            return Namespace(**config)
    except FileNotFoundError:
        logger.error(f"Configuration file {config_path} not found.")
        raise
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        logger.error(f"Error parsing configuration file {config_path}: {exc}")
        raise

global_config = load_config()
mcp_config = global_config.mcp
stock_config = global_config.stock

from starlette.requests import Request
async def gen_report(request: Request) -> str:
    """ Generate financial analysis report based on specified company stock information"""
    params =  request.query_params
    symbol = params.get("symbol")
    windows = int(params.get("windows", 30))
    try:
        logger.info(f"Getting data for {symbol}")
        stock = Stock(symbol=symbol, stock_config=stock_config, config = {})
        chart_path = stock.plot_with_tech_indicators(windows=windows)
        print(chart_path)
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return JSONResponse(content={"error": str(e)})
    return JSONResponse(content=chart_path)

def create_starlette_app():
    """Create a Starlette application that can server the provied fin server with API."""
    # 合并所有路由
    app = Starlette(
        debug=True,
        routes=[
            Route("/report", gen_report, methods=["GET"])
        ],
        on_startup=[startup_event],
        on_shutdown=[shutdown_event]
    )
    return app

app=create_starlette_app()
def start():
    host = mcp_config['host']
    port = mcp_config['port']
    logger.info(f"FIN_QT_SERVER starting  on {host}:{port}")
    uvicorn.run(f"{__name__}:app", host=host, port=port,reload=True,log_level="info")


if __name__ == "__main__":
    start()