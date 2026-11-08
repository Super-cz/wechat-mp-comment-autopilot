#!/usr/bin/env python3
import sys
import argparse
import yaml
from pathlib import Path

from core.storage.db import Database
from core.evaluator.audience_matcher import AudienceMatcher
from core.generator.comment_generator import CommentGenerator
from core.monitor.target_account_monitor import TargetAccountMonitor
from core.monitor.third_party_monitor import ThirdPartyRankMonitor
from core.executor.copilot_notifier import CopilotNotifier
from core.executor.adb_executor import AdbExecutor

def load_config() -> dict:
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "config" / "config.yaml"
    if not config_path.exists():
        config_path = base_dir / "config" / "config.example.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_pipeline(mode: str = "copilot"):
    print("=" * 65)
    print("🚀 微信公众号文章高权重引流与智能神评流水线启动")
    print(f"⚙️ 当前运行模式: {mode} (智能副驾巡航模式)")
    print("=" * 65)

    config = load_config()
    db = Database()
    
    # 双轨发现源：1. 核心对标大号列表 + 2. 第三方行业爆文榜单
    monitors = [
        TargetAccountMonitor(config),
        ThirdPartyRankMonitor(config),
    ]
    
    evaluator = AudienceMatcher(config)
    generator = CommentGenerator(config)

    if mode == "auto_adb":
        executor = AdbExecutor(config)
    else:
        executor = CopilotNotifier(config)

    # 检查每日配额
    daily_count = db.get_daily_comment_count()
    max_daily = config.get("execution", {}).get("max_daily_comments", 20)
    if daily_count >= max_daily:
        print(f"🛑 今日处理/推送次数 ({daily_count}) 已达安全上限 ({max_daily})，触发保护休眠。")
        return

    # 1. 抓取文章 (汇总两路数据源)
    all_articles = []
    for m in monitors:
        all_articles.extend(m.fetch_recent_articles())

    print(f"📡 双轨监控源共汇总到 {len(all_articles)} 篇候选文章，开始受众契合度分析...")

    for article in all_articles:
        url = article["url"]
        title = article["title"]

        if db.is_article_processed(url):
            print(f"⏩ [已处理] 跳过历史文章: {title}")
            continue

        # 2. 受众契合度与热度评估
        passed, score, heat_level, reason = evaluator.evaluate_article(article)
        print(f"\n📊 评估结果: 【{title}】")
        print(f"   来源: {article.get('account_name')} | 得分: {score}/100 | 热度等级: {heat_level} | 契合度: {'✅ 达标通过' if passed else '❌ 未达标'}")
        print(f"   原因: {reason}")

        if not passed:
            print("   ⏩ 过滤非目标赛道文章。")
            continue

        # 3. 大模型高情商神评生成
        print("🧠 正在调用大模型生成多维度高权重神评...")
        comments = generator.generate_comments(article)

        # 4. 存储到数据库
        art_id = db.save_article(url, title, article["account_name"], score, heat_level)
        db.save_comments(art_id, comments)

        # 5. 执行分发 (副驾提醒或真机自动发表)
        executor.dispatch_comment(article, comments)
        db.increment_daily_comment()

    print("\n✅ 本轮巡航扫描与神评生成处理完毕！")

def single_evaluate(url: str):
    config = load_config()
    evaluator = AudienceMatcher(config)
    generator = CommentGenerator(config)

    print(f"🔍 正在测试单篇文章评估与神评生成: {url}")
    mock_article = {
        "title": "测试文章：如何利用AI智能体与自动化工具搭建高粘性私域流量池与创业副业",
        "url": url,
        "account_name": "实战干货实验室",
        "digest": "本文深入分享利用AI大模型与自动化工具做公众号流量增长的底层逻辑与全套SOP...",
        "content": "在当今注意力稀缺的时代，单靠手工搬运和被动等待已经很难获得流量爆发。本文探讨如何用AI自动化工作流打通公域截流到私域沉淀，提升效率与商业变现...",
        "read_count": 8200,
        "comment_count": 35
    }
    passed, score, heat_level, reason = evaluator.evaluate_article(mock_article)
    print(f"得分: {score} | 热度: {heat_level} | 通过: {passed} | 原因: {reason}")

    if passed:
        comments = generator.generate_comments(mock_article)
        print("\n💡 【模式一】生成一级候选神评 (争夺精选/置顶):")
        for idx, c in enumerate(comments, 1):
            print(f"{idx}. [{c['strategy_name']}]: {c['content']}\n")

        # 模拟展示二级免审跟评能力
        mock_hot_comment = {
            "author": "创业老兵",
            "content": "现在做公域流量转化确实太卷了，前期的冷启动成本越来越高，如果团队没有技术底子，很难跑通自动化流程。",
            "likes": 128
        }
        reply = generator.generate_second_level_reply(mock_article, mock_hot_comment)
        print("⚡ 【模式二】生成二级高赞留言跟评 (免作者审核，借势截流):")
        print(f"原热评: “{mock_hot_comment['content']}” (👍 {mock_hot_comment['likes']})")
        print(f"推荐回复: {reply['content']}\n")

def main():
    parser = argparse.ArgumentParser(description="微信公众号评论区自动引流与神评生成系统")
    parser.add_argument("--mode", choices=["copilot", "auto_adb", "run", "evaluate"], default="copilot", help="运行模式")
    parser.add_argument("--url", type=str, default="", help="单篇测试文章URL")
    args = parser.parse_args()

    if args.mode == "evaluate":
        single_evaluate(args.url or "https://mp.weixin.qq.com/s/test_demo")
    else:
        run_pipeline(args.mode)

if __name__ == "__main__":
    main()
