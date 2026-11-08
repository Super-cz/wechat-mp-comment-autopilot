#!/usr/bin/env python3
import sys
import argparse
import yaml
from pathlib import Path

from core.storage.db import Database
from core.evaluator.audience_matcher import AudienceMatcher
from core.generator.comment_generator import CommentGenerator
from core.monitor.target_account_monitor import TargetAccountMonitor
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
    print(f"⚙️ 当前运行模式: {mode}")
    print("=" * 65)

    config = load_config()
    db = Database()
    monitor = TargetAccountMonitor(config)
    evaluator = AudienceMatcher(config)
    generator = CommentGenerator(config)

    if mode == "auto_adb":
        executor = AdbExecutor(config)
    else:
        executor = CopilotNotifier(config)

    # 检查每日配额
    daily_count = db.get_daily_comment_count()
    max_daily = config.get("execution", {}).get("max_daily_comments", 15)
    if daily_count >= max_daily:
        print(f"🛑 今日留言次数 ({daily_count}) 已达安全上限 ({max_daily})，触发风控休眠机制。")
        return

    # 1. 抓取最新文章
    articles = monitor.fetch_recent_articles()
    print(f"📡 监控到 {len(articles)} 篇候选文章，开始逐一评估...")

    for article in articles:
        url = article["url"]
        title = article["title"]

        if db.is_article_processed(url):
            print(f"⏩ [已处理] 跳过历史文章: {title}")
            continue

        # 2. 受众契合度与热度评估
        passed, score, heat_level, reason = evaluator.evaluate_article(article)
        print(f"\n📊 评估结果: 【{title}】")
        print(f"   得分: {score}/100 | 热度等级: {heat_level} | 契合度判断: {'✅ 通过' if passed else '❌ 未达标'}")
        print(f"   原因: {reason}")

        if not passed:
            print("   跳过非目标受众文章。")
            continue

        # 3. 大模型高情商神评生成
        print("🧠 正在调用大模型生成多策略候选神评...")
        comments = generator.generate_comments(article)

        # 4. 存储到数据库
        art_id = db.save_article(url, title, article["account_name"], score, heat_level)
        db.save_comments(art_id, comments)

        # 5. 执行分发 (副驾提醒或真机自动发表)
        executor.dispatch_comment(article, comments)
        db.increment_daily_comment()

    print("\n✅ 流水线本轮扫描处理完毕！")

def single_evaluate(url: str):
    config = load_config()
    evaluator = AudienceMatcher(config)
    generator = CommentGenerator(config)

    print(f"🔍 正在测试单篇文章评估与神评生成: {url}")
    mock_article = {
        "title": "测试文章：如何利用自动化工作流搭建高粘性私域流量池",
        "url": url,
        "account_name": "实战干货实验室",
        "digest": "本文深入分享利用AI智能体与自动化工具做公众号流量增长的底层逻辑与全套SOP...",
        "content": "在当今注意力稀缺的时代，单靠手工搬运和被动等待已经很难获得流量爆发。本文探讨如何用自动化工作流打通公域截流到私域沉淀...",
        "read_count": 8200,
        "comment_count": 35
    }
    passed, score, heat_level, reason = evaluator.evaluate_article(mock_article)
    print(f"得分: {score} | 热度: {heat_level} | 通过: {passed} | 原因: {reason}")

    if passed:
        comments = generator.generate_comments(mock_article)
        print("\n💡 生成神评结果:")
        for idx, c in enumerate(comments, 1):
            print(f"{idx}. [{c['strategy_name']}]: {c['content']}\n")

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
