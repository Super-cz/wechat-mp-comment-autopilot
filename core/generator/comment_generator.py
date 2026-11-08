import yaml
from pathlib import Path
from typing import Dict, Any, List
from openai import OpenAI

class CommentGenerator:
    def __init__(self, config: Dict[str, Any], prompts_path: Path = None):
        self.config = config
        self.llm_cfg = config.get("llm", {})
        self.my_account = config.get("my_account", {})
        
        if prompts_path is None:
            prompts_path = Path(__file__).resolve().parent.parent.parent / "config" / "prompts.yaml"
            
        with open(prompts_path, "r", encoding="utf-8") as f:
            self.prompts = yaml.safe_load(f)

        self.client = OpenAI(
            api_key=self.llm_cfg.get("api_key", "mock-key"),
            base_url=self.llm_cfg.get("base_url", "https://api.deepseek.com/v1"),
        )
        self.model = self.llm_cfg.get("model", "deepseek-chat")
        self.temperature = self.llm_cfg.get("temperature", 0.7)

    def generate_comments(self, article: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        根据文章内容生成一级评论的多策略候选神评 (争夺精选)
        """
        title = article.get("title", "")
        digest = article.get("digest", "")
        content = article.get("content", "")
        if len(content) > 2000:
            content = content[:2000] + "...(后文省略)"

        article_context = f"【文章标题】：{title}\n【文章摘要】：{digest}\n【核心正文节选】：{content}"
        account_context = (
            f"【我方公众号】：{self.my_account.get('name')}\n"
            f"【我方赛道与受众】：{self.my_account.get('target_audience_description')}\n"
            f"【人设风格】：{self.my_account.get('tone_style')}"
        )

        results = []
        strategies = self.prompts.get("strategies", {})

        for strat_key, strat_val in strategies.items():
            if strat_val.get("type") == "second_level":
                continue # 二级跟评走专门接口

            strat_name = strat_val.get("name", strat_key)
            strat_prompt = strat_val.get("prompt", "")

            user_instruction = (
                f"{account_context}\n\n"
                f"{article_context}\n\n"
                f"【本次留言策略要求 - {strat_name}】：\n"
                f"{strat_prompt}\n\n"
                f"请直接输出符合要求的 1 条评论内容，字数在 50~120 字之间，不要包含任何前缀或解释性说明："
            )

            results.append(self._invoke_or_mock(strat_key, strat_name, user_instruction, title))

        return results

    def generate_second_level_reply(self, article: Dict[str, Any], hot_comment: Dict[str, Any]) -> Dict[str, str]:
        """
        针对已被精选的高赞热门留言，生成高情商二级跟评 (免作者审核借势截流)
        """
        title = article.get("title", "")
        comment_author = hot_comment.get("author", "热评读者")
        comment_text = hot_comment.get("content", "")
        likes = hot_comment.get("likes", 99)

        strategy_cfg = self.prompts.get("strategies", {}).get("reply_to_hot_comment", {})
        strat_name = strategy_cfg.get("name", "热门留言神级跟评型")
        strat_prompt = strategy_cfg.get("prompt", "")

        user_instruction = (
            f"【我方公众号】：{self.my_account.get('name')}\n"
            f"【我方赛道与受众】：{self.my_account.get('target_audience_description')}\n\n"
            f"【原文章标题】：{title}\n"
            f"【目标精选高赞留言】（已有 {likes} 赞，作者: {comment_author}）：\n"
            f"“{comment_text}”\n\n"
            f"【二级跟评策略要求】：\n"
            f"{strat_prompt}\n\n"
            f"请直接输出一条对该精选热评的回复内容（字数在 40~100 字之间，幽默或深刻，不要包含任何生硬推广）："
        )

        return self._invoke_or_mock("reply_to_hot_comment", strat_name, user_instruction, title, is_reply=True)

    def _invoke_or_mock(self, strat_key: str, strat_name: str, instruction: str, title: str, is_reply: bool = False) -> Dict[str, str]:
        try:
            if not self.llm_cfg.get("api_key") or "xxxx" in self.llm_cfg.get("api_key"):
                mock_text = self._generate_mock_reply() if is_reply else self._generate_mock_comment(strat_key)
                return {"strategy": strat_key, "strategy_name": strat_name, "content": mock_text}

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompts.get("system_prompt", "")},
                    {"role": "user", "content": instruction},
                ],
                temperature=self.temperature,
                max_tokens=250,
            )
            comment_text = response.choices[0].message.content.strip()
            if comment_text.startswith('"') and comment_text.endswith('"'):
                comment_text = comment_text[1:-1]
            return {"strategy": strat_key, "strategy_name": strat_name, "content": comment_text}
        except Exception as e:
            return {"strategy": strat_key, "strategy_name": strat_name, "content": f"[生成异常: {e}]"}

    def _generate_mock_comment(self, strategy: str) -> str:
        if strategy == "insight_supplement":
            return "文中提到的痛点确实是行业常态。我们在实操中还发现一个关键杠杆：把高频重复环节模块化之后，交付效率至少能翻两倍。作者梳理的框架很扎实，值得收藏复盘！"
        elif strategy == "golden_quote_summary":
            return "信息差的本质是行动力差，工具差的本质是认知差。与其焦虑技术迭代，不如把最基础的业务闭环打磨扎实。一语中的的好文！"
        else:
            return "深度认同作者关于长期复利的判断。不过在落地前期的冷启动阶段，大家普遍遇到的最大卡点往往是资源匹配，不知各位同行在这个阶段都是怎么破局的？"

    def _generate_mock_reply(self) -> str:
        return "层主这句话直接说到了心坎里！很多时候大家不是缺方法，而是卡在第一步的执行惯性上。顺着层主的思路，如果能配合现成的模板工具，起步阻力会小一大半。"
