1️⃣ 读取配置文件
从 config.json 里读取：

回测的起止时间 (start_date, end_date)

初始资金 (initial_cash)

需要回测的 ETF 列表 (tickers)

多因子权重 (weights) —— 例如 momentum, roe, growth, pe

2️⃣ 获取数据
用 yfinance 下载每个 ETF 的历史行情数据（Open, High, Low, Close, Volume）。

可能还会用 yahooquery 或 financialmodelingprep 获取 ETF 或成分股的 ROE / 盈利增长率 / PE 等财务指标。

3️⃣ 计算因子得分
对每个 ETF：

计算 动量因子（过去 X 个月的收益率）

获取或估算 ROE、盈利增长率、PE

按照配置文件里的权重对这些因子做加权，得到 综合评分。

4️⃣ 选出排名靠前的 ETF
每隔一段时间（比如每季度或每月）重新计算因子评分。

按照评分排序，选择排名最高的 3 个 ETF。

5️⃣ 组合调仓
每次调仓时，计算目标仓位（均分资金）。

使用 rebalancing（调仓），而不是每次全仓卖出后再买入。

记录每次的买卖行为，并在 log 里输出。

6️⃣ 回测执行
用 backtrader 的 Cerebro 引擎运行策略：

记录每次交易（买入/卖出）

计算回测结束后的 最终组合价值

7️⃣ 结果输出
打印每次调仓时的买卖记录（买入/卖出、价格、仓位大小、剩余现金）

打印最终投资组合的价值

