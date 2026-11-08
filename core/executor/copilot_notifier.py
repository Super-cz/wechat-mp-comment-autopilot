import httpx
from typing import Dict, Any, List
from .base_executor import BaseExecutor

class CopilotNotifier(BaseExecutor):
    """
    智能副驾巡航模式：
    将高质量候选神评及文章直达链接推送到企业微信或飞书群，
    运营人员在手机上一键点击文章链接，长按复制神评即可在微信内完成留言。
    【优点】：0 封号风险，100% 走官方客户端合规流程，人机协同精选率最高。
    """
    def __init__(self, config: Dict[str, Any]):
        self.notif_cfg = config.get("notifications", {})
        self.feishu_webhook = self.notif_cfg.get("feishu_webhook", "")
        self.wechat_work_webhook = self.notif_cfg.get("wechat_work_webhook", "")

    def dispatch_comment(self, article: Dict[str, Any], comments: List[Dict[str, str]]) -> bool:
        title = article.get("title", "")
        url = article.get("url", "")
        account_name = article.get("account_name", "")

        print(f"\n[Copilot Notification] 🚀 发现高契合度爆款文章！")
        print(f"📌 来源账号: {account_name}")
        print(f"📖 文章标题: {title}")
        print(f"🔗 文章链接: {url}")
        print("💡 候选高赞神评 (任选一条复制发表):")
        for idx, c in enumerate(comments, 1):
            print(f"  [{idx}. {c.get('strategy_name')}]:")
            print(f"     \"{c.get('content')}\"")

        # 若配置了飞书 Webhook，发送富文本卡片
        if self.feishu_webhook and "xxxx" not in self.feishu_webhook:
            try:
                card_content = self._build_feishu_card(article, comments)
                httpx.post(self.feishu_webhook, json=card_content, timeout=10.0)
                print("✅ 成功推送到飞书机器人！")
            except Exception as e:
                print(f"⚠️ 飞书推送失败: {e}")

        return True

    def _build_feishu_card(self, article: Dict[str, Any], comments: List[Dict[str, str]]) -> Dict[str, Any]:
        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**来源号**：{article.get('account_name')}\n**标题**：[{article.get('title')}]({article.get('url')})"
                }
            },
            {"tag": "hr"}
        ]
        for c in comments:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"✨ **{c.get('strategy_name')}**：\n> {c.get('content')}"
                }
            })
        return {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": "🎯 公众号引流神评提醒 (抓紧抢前排)"},
                    "template": "blue"
                },
                "elements": elements
            }
        }
