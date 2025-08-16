from argparse import Namespace
from dotenv import load_dotenv
from typing import Any, Dict, Optional,Type, TypeVar, get_type_hints
import copy
import json
import logging
import os
import re
import yaml
logger = logging.getLogger("fin_mcp_server")
VAR_PATTERN = re.compile(r'\$\{([^}]+)}')


def get_value_by_path(data: Dict[str, Any], path: str, separator: str = '.') -> Any:
    """使用点分隔符路径从嵌套数据结构中获取值"""
    keys = path.split(separator)
    current = data

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and key.isdigit():
            index = int(key)
            if 0 <= index < len(current):
                current = current[index]
            else:
                return None
        else:
            return None

    return current
def get_var_value(context: Dict[str, Any], var_name: str, default: Optional[str] = None) -> str:
    """获取变量值，支持点分隔符路径"""
    # 尝试从当前上下文中获取
    value = get_value_by_path(context, var_name)
    if value is not None:
        return str(value)

    # 尝试从环境变量中获取
    env_value = os.getenv(var_name)
    if env_value is not None:
        return env_value

    # 尝试从环境变量中获取（小写）
    env_value_lower = os.getenv(var_name.lower())
    if env_value_lower is not None:
        return env_value_lower

    # 返回默认值（如果提供）
    if default is not None:
        return default

    # 未找到且无默认值
    raise ValueError(f"无法解析变量: {var_name}")
def resolve_value(context: Dict[str, Any], value: Any) -> Any:
        """递归解析值中的变量引用"""
        # 处理字典
        if isinstance(value, dict):
            return {k: resolve_value(context, v) for k, v in value.items()}

        # 处理列表
        elif isinstance(value, list):
            return [resolve_value(context, item) for item in value]

        # 处理字符串
        elif isinstance(value, str):
            # 查找所有变量引用
            matches = VAR_PATTERN.findall(value)

            # 如果没有变量引用，直接返回
            if not matches:
                return value

            # 替换变量引用
            resolved_value = value
            for var_expr in matches:
                # 处理带默认值的变量: ${VAR:default}
                if ':' in var_expr:
                    var_name, default = var_expr.split(':', 1)
                    var_value = get_var_value(context, var_name.strip(), default.strip())
                else:
                    var_value = get_var_value(context, var_expr)

                # 替换变量
                resolved_value = resolved_value.replace(f'${{{var_expr}}}', str(var_value))

            # 递归解析，因为替换后可能产生新的变量引用
            return resolve_value(context, resolved_value)

        # 其他类型直接返回
        else:
            return value
def load_config(encoding: str = "utf-8"):
    load_dotenv()
    config_path = os.getenv("YML", os.path.join(os.getcwd(), "config.yml"))
    try:
        with open(config_path, 'r',encoding = encoding) as file:
            config = yaml.safe_load(file)
            config.update({k.lower(): v for k, v in os.environ.items()})
            # 创建一个临时上下文用于解析
            temp_ctx = copy.deepcopy(config)
            config = resolve_value(temp_ctx, temp_ctx)
            return Namespace(**config)
    except FileNotFoundError:
        logger.error(f"Configuration file {config_path} not found.")
        raise
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        logger.error(f"Error parsing configuration file {config_path}: {exc}")
        raise