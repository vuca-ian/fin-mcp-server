# Financial MCP Server

Financial MCP Server 是一个基于多模态大模型的金融技术分析工具，能够从 Yahoo Finance 下载股票数据，计算技术指标，生成专业的 K 线图，并利用 Qwen2.5-VL 等多模态大模型对图表进行分析，生成专业的金融分析报告。

## 项目简介

本项目旨在为金融分析师和投资者提供一个自动化技术分析工具，通过以下流程实现智能化金融分析：

1. 数据获取：从 Yahoo Finance 实时获取股票历史数据
2. 技术指标计算：计算包括 EMA、SMA、MACD、RSI、KDJ、布林带、ATR、OBV 等多种技术指标
3. 图表生成：生成包含主图 K 线和多个技术指标副图的专业金融图表
4. 智能分析：利用多模态大模型（如 Qwen2.5-VL）对生成的图表进行深度分析
5. 报告生成：输出专业的金融分析报告，包括趋势分析、买卖信号、风险评估等

### 核心特性

- 多模态分析：支持图像和文本的多模态大模型分析
- 丰富技术指标：内置多种常用技术指标计算
- 专业图表：生成符合金融行业标准的专业 K 线图

## 部署指南

环境要求

- Python 3.12+
- pip 包管理器
- ta-lib 金融量化技术分析库

## 配置文件

你需要一个 YAML 配置文件来配置服务器,在 config_demo.yml 中提供了一个默认配置文件，内容如下：

```yaml
mcp:
  transport: "stdio" # 或其他支持的传输方式

stock:
  source: "yahoo" # 数据源，支持 yahoo 或 local

llm:
  llm_type: "openai" # 支持 openai 或 ollama
  base_url: "https://api.openai.com/v1" # API 基础 URL
  api_key: "your-api-key" # API 密钥
  model: "gpt-4o-mini" # 使用的模型
  temperature: 0.7 # 生成温度
  max_tokens: 4096 # 最大令牌数
```

### MCP 配置

你可以将传输协议设置为`stdio`或`sse`。

#### STDIO

对于 `stdio` 协议，你可以这样设置:

```yaml
mcp:
  transport: "stdio"
```

#### SSE

对于 `sse` 协议，你可以这样设置:

```yaml
mcp:
  transport: "sse"
  host: "0.0.0.0"
  port: 8000
```

### LLM 配置

`model` 是要使用的模型名称, `api_key` 是模型的 API 密钥, `base_url` 是模型的 API 地址。我们支持以下模型。

- OpenAI 系列：GPT-4, GPT-4o, GPT-4o-mini 等
- Qwen 系列：Qwen2.5-VL, Qwen-VL 等多模态模型

## 启动服务

```
YML=config.yml python -m fin_mcp_server
```

## 输出示例

#### 生成的分析报告包含以下内容：

1. 价格趋势分析：短期、中期、长期趋势判断
2. 技术指标解读：MACD、RSI、KDJ 等指标协同验证
3. 量价关系分析：成交量与价格的配合关系
4. 支撑压力位：动态计算关键支撑和阻力位
5. 风险预警：潜在风险信号识别
6. 交易策略：具体的入场、止损、止盈建议
7. 置信度评估：A/B/C 三级置信度评级

## 注意事项

1. 数据源限制：Yahoo Finance 对请求频率有限制，请合理使用
2. API 成本：使用商业 API 会产生相应费用
3. 模型能力：不同模型的图像理解能力有所差异
4. 网络环境：确保网络连接稳定以获取数据和调用 API

## 许可证

本项目采用`APACHE`许可证，详情请参见 `LICENSE` 文件。
