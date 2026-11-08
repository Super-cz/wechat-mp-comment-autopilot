import re
from typing import Dict, Any, List, Tuple

class AudienceMatcher:
    def __init__(self, config: Dict[str, Any]):
        self.rules = config.get("evaluation_rules", {})
        self.my_account = config.get("my_account", {})
        self.required_keywords = self.rules.get("required_keywords", [])
        self.blacklist_keywords = self.rules.get("blacklist_keywords", [])
        self.min_score = self.rules.get("min_audience_relevance_score", 70)

    def evaluate_article(self, article: Dict[str, Any]) -> Tuple[bool, int, str, str]:
        """
        评估文章是否值得引流留言。
        返回: (是否通过, 得分, 热度等级, 评估原因)
        """
        title = article.get("title", "")
        content = article.get("content", "") or article.get("digest", "")
        full_text = f"{title} {content}"

        # 1. 黑名单过滤 (政治、高争议、违规等一票否决)
        for bad_word in self.blacklist_keywords:
            if bad_word in full_text:
                return False, 0, "low", f"命中黑名单关键词: {bad_word}"

        # 2. 关键词匹配度计算
        score = 50 # 基础分
        matched_required = []
        for kw in self.required_keywords:
            count = len(re.findall(re.escape(kw), full_text, re.IGNORECASE))
            if count > 0:
                matched_required.append(kw)
                score += min(count * 5, 20)

        # 若完全没有匹配到核心赛道词，则扣分
        if not matched_required and self.required_keywords:
            score -= 30

        # 3. 自身公众号定位标签契合度
        my_tags = self.my_account.get("domain_tags", [])
        matched_tags = []
        for tag in my_tags:
            if tag in full_text:
                matched_tags.append(tag)
                score += 10

        # 4. 标题吸引力与爆款度加分
        clickbait_markers = ["深度", "复盘", "实测", "首发", "独家", "终局", "曝光", "揭秘", "干货", "指南"]
        for marker in clickbait_markers:
            if marker in title:
                score += 3

        score = max(0, min(100, score))

        # 5. 热度等级估计 (基于预估或文章已有数据)
        read_count = article.get("read_count", 0)
        comment_count = article.get("comment_count", 0)

        if read_count > 10000 or comment_count > 50:
            heat_level = "viral"
        elif read_count > 3000 or comment_count > 10:
            heat_level = "high"
        elif read_count > 500:
            heat_level = "medium"
        else:
            heat_level = "normal"

        passed = score >= self.min_score
        reason = f"匹配关键词: {matched_required}, 领域标签: {matched_tags}, 得分: {score}"

        return passed, score, heat_level, reason
