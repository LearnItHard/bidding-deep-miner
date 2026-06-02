# 🏗️ Bidding Deep Miner

**招投标项目深度挖掘 Skill** — 从模糊的项目名称出发，多渠道搜索、交叉比对、推理出具体工艺/技术方案。

## 场景

> 你有一个污水处理项目，项目名称只写了"某市污水处理厂扩建工程"，没提具体工艺。你想知道：
> - 它用的是什么工艺？（A²O？MBR？SBR？氧化沟？）
> - 有类似的参考项目吗？
> - 技术方案中提到了哪些关键设备/参数？

Bidding Deep Miner 会自动完成这个挖掘过程。

## 工作流程

Skill 采用**双循环架构**，自主完成挖掘全流程：

```
BOOTSTRAP（一次，轻量）
  解析项目 → 确定搜索渠道 → 形成搜索假设

内环（快速，自主，重复）
  选择渠道 → 执行搜索 → 抓取页面 → 提取信息 → 记录 → 下一轮

外环（周期，反思）
  审查证据 → 交叉验证 → 更新 findings.md →
  判断置信度 → 决定方向（深入/扩展/转向/结论）

FINALIZE（结束时）
  生成最终报告 → 归档
```

内环执行紧密的搜索-提取循环，外环退一步综合推理。置信度 ≥ 0.7 时输出结论。

## 快速开始

### 作为 Skill 使用（推荐）

将本仓库放入 Claude Code / OpenClaw 的 skills 目录：

```bash
# 克隆到 skills 目录
git clone https://github.com/LearnItHard/bidding-deep-miner.git \
  ~/.claude/skills/bidding-deep-miner
```

然后在对话中直接触发：

```
/bid-mine 某市污水处理厂扩建工程
/bid-mine "某河流域水环境综合治理工程"
```

Agent 会自动执行搜索→提取→验证→推理→报告全流程。

### 使用 Python 工具包

`bidding_miner/` 中的 Python 模块可供 Agent 在挖掘过程中调用，也可独立使用：

```python
from bidding_miner.search_engine import SimpleSearchEngine
from bidding_miner.urls import SearchableURL, build_search_url

# 构建招标平台搜索 URL
url = build_search_url(
    SearchableURL(name="中国招标投标公共服务平台",
                  base_url="https://bulletin.cebpubservice.com/",
                  query_param="search"),
    "污水处理厂扩建")
```

## 项目结构

```
bidding-deep-miner/
├── .gitignore                      # Git 忽略规则
├── SKILL.md                        # Skill 定义（用于 Claude Code / OpenClaw）
├── README.md                       # 本文件
├── requirements.txt                # 运行时依赖（requests, bs4, crawl4ai）
├── bidding_miner/                  # Python 工具包
│   ├── __init__.py                 # 包入口，版本 0.1.0
│   ├── fetch.py                    # 网页抓取（Crawl4AI 延迟导入，自动降级）
│   ├── search_engine.py            # 搜索引擎（DuckDuckGo HTML 直抓）
│   └── urls/
│       ├── __init__.py             # 招投标平台 URL 注册表 & 构建器
│       └── ...                     # 平台 URL 数据源
├── doc/
│   └── design.md                   # 架构设计文档
├── references/                     # Agent 参考指令集
│   ├── agent-continuity.md         # Agent 连续性设置
│   ├── evidence-grading.md         # 证据可信度分级
│   ├── progress-reporting.md       # 进度汇报规范
│   └── search-strategy.md          # 搜索策略指南
└── templates/                      # 挖掘流程模板
    ├── findings.md                 # 进化叙事综合模板
    ├── mining-log.md               # 决策时间线模板
    ├── mining-state.yaml           # 中央状态追踪模板
    └── report-template.md          # 最终报告模板
```

## 与普通搜索的区别

| | 普通搜索 | Bidding Deep Miner |
|--|---------|-------------------|
| 输入 | 直接搜项目名 | 项目名 → 多渠道搜索 → 推理 |
| 深度 | 搜到公告原文为止 | 提取技术关键词 → 交叉验证 |
| 结论 | 自行阅读判断 | 结构化报告 + 证据链 + 置信度 |
| 迭代 | 无 | 置信度不够自动发起新一轮搜索 |

## 证据可信度分级

| 级别 | 来源 | 权重 |
|------|------|------|
| P1 | 招标文件/技术规格书原文 | 最高 |
| P2 | 环评报告 / 可研报告 / 初步设计 | 高 |
| P3 | 中标公告 / 合同公告 / 企业资质 | 中 |
| P4 | 行业资讯 / 新闻报道 / 企业官网 | 低 |
| P5 | 搜索引擎摘要 / 论坛 / 百科 | 最低 |

## License

MIT
