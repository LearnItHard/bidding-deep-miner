# 🏗️ Bidding Deep Miner

**招投标项目深度挖掘 Skill** — 从模糊的项目名称出发，多渠道搜索、交叉比对、推理出具体工艺/技术方案。

## 场景

> 你有一个污水处理项目，项目名称只写了"某市污水处理厂扩建工程"，没提具体工艺。你想知道：
> - 它用的是什么工艺？（A²O？MBR？SBR？氧化沟？）
> - 有类似的参考项目吗？
> - 技术方案中提到了哪些关键设备/参数？

Bidding Deep Miner 会自动完成这个挖掘过程。

## 工作流程

```
项目名称/编号
    ↓
┌─ Collector ─────────────────────────────┐
│  招投标平台  ·  通用搜索  ·  学术搜索    │
└──────────────────┬──────────────────────┘
                   ↓
┌─ Extractor ─────────────────────────────┐
│  技术关键词提取  ·  证据分类  ·  可信度  │
└──────────────────┬──────────────────────┘
                   ↓
┌─ Analyzer ──────────────────────────────┐
│  多源交叉验证  ·  工艺推理  ·  置信度评估 │
└──────┬───────────────────────────────────┘
       ↓ (置信度 < 0.7 则迭代再搜索)
┌─ Reporter ──────────────────────────────┘
│  结构化深度挖掘报告
↓
📄 最终报告（含证据链、置信度、建议下一步）
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 直接运行
python main.py "某市污水处理厂扩建工程"

# 带项目编号
python main.py "某河流域水环境综合治理" --project-id HB2025084670010053

# 详细日志
python main.py "项目名称" --verbose

# 保存报告到文件
python main.py "项目名称" -o report.md
```

## 项目结构

```
bidding-deep-miner/
├── SKILL.md                        # Skill 定义（用于 Claude Code / OpenClaw）
├── README.md                       # 本文件
├── requirements.txt
├── main.py                         # CLI 入口
├── bidding_miner/
│   ├── __init__.py
│   ├── state.py                    # 共享状态定义
│   ├── agents.py                   # 4 个 Agent 实现
│   ├── graph.py                    # LangGraph 工作流
│   ├── tools.py                    # 工具函数
│   ├── config.py                   # LLM + 搜索引擎配置
│   ├── fetch.py                    # 网页抓取
│   ├── search_engine.py            # 搜索引擎回退
│   └── urls/
│       ├── __init__.py             # URL 数据源（优先复用 deep-research-agent）
│       └── ...                     # 招投标平台 URL 库
├── examples/
│   └── quick_start.py
└── doc/
    └── design.md
```

## 与 deep-research-agent 的关系

本 Skill **优先复用** `deep-research-agent` 的基础设施：
- LLM 配置（SiliconFlow API）
- 搜索引擎（4 引擎全并行）
- 网页抓取（Crawl4AI）
- 招投标 URL 库（国家级 + 省市级 + 政府采购）

如果 `deep-research-agent` 项目不可用，会自动回退到内置的简易实现。

## 作为 Claude Code / OpenClaw Skill 使用

将本目录放入 `.claude/skills/` 或 `~/.claude/skills/` 后，直接对话触发：

```
/bid-mine 某市污水处理厂扩建工程
/bid-mine "某河流域水环境综合治理工程" --deep
```

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
