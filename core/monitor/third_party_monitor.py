import os
import httpx
from typing import List, Dict, Any
from .base_monitor import BaseMonitor

class ThirdPartyRankMonitor(BaseMonitor):
    """
    第三方数据平台 (如新榜、西瓜数据、清博等) 热榜与潜力爆文监控驱动：
    通过 API 拉取行业垂直赛道刚发布且阅读量上升速度较快的新生爆文。
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get("third_party_api", {}).get("api_key", "")
        self.api_url = config.get("third_party_api", {}).get("endpoint", "")
        self.target_category = config.get("third_party_api", {}).get("category", "科技互联网")
        self.enabled = config.get("third_party_api", {}).get("enabled", True)

    def fetch_recent_articles(self) -> List[Dict[str, Any]]:
        """
        拉取最新行业潜力爆文。若未配置真实 API Key，提供标准化合规模拟样本。
        """
        if not self.enabled:
            return []

        # 检查是否配置了真实凭据
        has_real_key = (
            self.api_key 
            and "your-" not in self.api_key 
            and "xxxx" not in self.api_key 
            and self.api_url
        )

        if has_real_key:
            try:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                params = {
                    "category": self.target_category,
                    "hours": 1,
                    "sort": "read_velocity_desc"
                }
                resp = httpx.get(self.api_url, headers=headers, params=params, timeout=10.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return self._parse_api_response(data)
            except Exception as e:
                print(f"⚠️ 第三方平台接口请求异常: {e}")

        # 默认返回行业规范测试样本
        return [
            {
                "title": "行业观察：2026年企业自动化工作流实战落地手册",
                "url": "https://mp.weixin.qq.com/s/sample_hot_trend_workflow",
                "account_name": "极客前沿研报",
                "publish_time": "刚刚",
                "digest": "低代码与大模型结合，中小团队如何跑通自动化效率变现与交付...",
                "content": "在企业服务和自动化赛道，工作流引擎一直是兵家必争之地。本文通过真实数据复盘，详细梳理了自动化工具与大模型在落地中的效率优化全过程...",
                "read_count": 8600,
                "comment_count": 42
            }
        ]

    def _parse_api_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        articles = []
        raw_list = data.get("data", {}).get("articles", [])
        for item in raw_list:
            articles.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "account_name": item.get("author", "") or item.get("account_name", ""),
                "publish_time": item.get("publish_time", ""),
                "digest": item.get("digest", ""),
                "content": item.get("content", ""),
                "read_count": item.get("read_count", 0),
                "comment_count": item.get("comment_count", 0),
            })
        return articles
