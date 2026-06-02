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
