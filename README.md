# WeChat Official Account Comment LeadGen & Copilot
# 微信公众号文章评论区高权重引流与智能助手机器人

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)

## 1. 业务逻辑与核心发现 (Core Insight)

在微信公众号文章评论区，**以公众号身份留言**后：
1. 读者点击该留言的头像与昵称，会**直接跳转到你的公众号主页**。
2. 读者在主页可以直接完成**关注、阅读历史图文、发送私信**等操作。
3. 这是一个极高信噪比、精准截流垂直赛道目标受众（尤其是高价值读者与行业从业者）的天然入口。

---

## 2. 核心痛点与现实挑战 (The WeChat Reality Check)

| 挑战维度 | 核心障碍 | 解决方案 / 对策 |
| :--- | :--- | :--- |
| **精选留言机制 (审核墙)** | 微信公众号评论**非实时展示**，必须经过文章作者手动「选入精选」才会对外公开。无脑硬广、机器套话 100% 被拒并拉黑。 | **价值先行 (Give Before Take)**：利用大模型生成深度提炼、观点补充或共鸣型神评，让号主觉得「这条留言提升了我文章的质感」并主动置顶。 |
| **黄金抢占窗口 (时效性)** | 文章发布 15~30 分钟内是号主审核留言和早期读者点赞最密集的黄金期。一旦错过，留言被压在底层甚至无人审核。 | **近实时监控机制**：定向监控对标大号发布状态，第一时间拉取内容、触发评估与生成。 |
| **受众垂直契合度** | 泛流量无意义，必须匹配与自身公众号定位高度契合的垂直受众。 | **多维评分引擎**：基于主题向量相似度、关键词密度与受众画像对文章进行评分，未达阈值不留言。 |
| **微信极端严格的风控** | 纯协议 Hook / 模拟协议封号风险极高（涉及封禁留言能力甚至公众号主体）。 | **双轨执行方案**：<br>1. **物理真机/桌面 UI 自动化**（ADB / UIAutomator / PC微信 CEF）；<br>2. **半自动 Copilot 巡航模式**（系统推送 3 个候选神评至企微/飞书，人工一键确认提交）。 |

---

## 3. 系统架构 (System Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                   1. 监控与发现 (Monitor)                    │
│   - 对标大号列表轮询 / 订阅更新感知                         │
│   - 搜一搜 / 看一看热度检测                                 │
└──────────────────────────────┬──────────────────────────────┘
                               │ 发现新发文章
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 2. 文章初筛与受众评估 (Evaluator)            │
│   - 文章正文与排版解析 (Title, Digest, Content)             │
│   - 受众匹配度评分 (Audience Relevance Score)               │
│   - 爆款热度潜力预测 (Heat Velocity Prediction)             │
└──────────────────────────────┬──────────────────────────────┘
                               │ 评分达标 (Score >= Threshold)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                3. 高情商神评生成引擎 (LLM Generator)         │
│   - 策略 A: 【干货补充型】补充行业数据/前沿案例 (号主最爱精选)│
│   - 策略 B: 【犀利总结型】金句提炼、洞察本质 (高赞神评)      │
│   - 策略 C: 【争议共鸣型】引发第二波讨论，提升互动率         │
│   - 严禁任何形式的生硬联系方式/外链广告                      │
└──────────────────────────────┬──────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐
│  4A. 全自动执行 (Auto-Pilot)  │ │  4B. 智能副驾 (Copilot 模式) │
│ - Android ADB / UIAutomator2 │ │ - 飞书/企业微信机器人 Webhook │
│ - PC 微信自动化 (Playwright)  │ │ - 运营人员移动端一键审核/复制 │
│ - 拟人随机延时 & 防封策略    │ │ - 零封号风险，精选率最高     │
└──────────────┬───────────────┘ └──────────────┬───────────────┘
               │                                │
               └───────────────┬────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 5. 数据复盘与引流追踪 (Analytics)           │
│   - 留言是否被选入精选追踪                                  │
│   - 点赞数、跟评数变化监控                                  │
│   - 主页新增粉丝转化相关性分析                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 目录结构 (Repository Structure)

```bash
wechat-mp-comment-autopilot/
├── config/
│   ├── config.example.yaml     # 核心配置模板（监控号列表、评分权重、API Key等）
│   └── prompts.yaml            # 大模型神评生成提示词模板库
├── core/
│   ├── monitor/                # 文章监控模块
│   │   ├── __init__.py
│   │   ├── base_monitor.py
│   │   └── target_account_monitor.py
│   ├── evaluator/              # 文章受众与热度评估器
│   │   ├── __init__.py
│   │   └── audience_matcher.py
│   ├── generator/              # LLM 留言生成引擎
│   │   ├── __init__.py
│   │   └── comment_generator.py
│   ├── executor/               # 执行驱动模块
│   │   ├── __init__.py
│   │   ├── base_executor.py
│   │   ├── adb_executor.py     # 真实手机自动化驱动
│   │   └── copilot_notifier.py # 协同副驾推送 (企微/飞书/Webhook)
│   └── storage/                # 本地数据存储与历史去重
│       ├── __init__.py
│       └── db.py
├── main.py                     # CLI 主调度入口
├── requirements.txt            # 项目依赖
└── README.md                   # 架构与使用指南
```

---

## 5. 快速启动 (Quick Start)

### 5.1 环境安装
```bash
git clone https://github.com/Super-cz/wechat-mp-comment-autopilot.git
cd wechat-mp-comment-autopilot
pip install -r requirements.txt
```

### 5.2 配置文件
```bash
cp config/config.example.yaml config/config.yaml
# 编辑 config/config.yaml，填入你的 OpenAI/DeepSeek API Key 及对标账号和受众标签
```

### 5.3 运行模式
```bash
# 1. 运行巡航副驾模式 (推荐：安全稳健，推送到飞书/企微审核)
python main.py --mode copilot

# 2. 单次测试文章评估与神评生成
python main.py --mode evaluate --url "https://mp.weixin.qq.com/s/xxxxxx"

# 3. 运行自动监控流水线
python main.py --mode run
```

---

## 6. 免责声明 (Disclaimer)

本项目仅用于技术交流与微信公众号生态运营合规探索。使用本项目时，请严格遵守《微信公众平台运营规范》及相关法律法规。禁止利用本项目进行垃圾广告轰炸、违规导流或恶意营销。
