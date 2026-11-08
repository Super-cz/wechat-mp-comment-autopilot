from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseMonitor(ABC):
    @abstractmethod
    def fetch_recent_articles(self) -> List[Dict[str, Any]]:
        """
        获取最近发布的公众号文章列表。
        返回的字典需包含:
        - title: str
        - url: str
        - account_name: str
        - publish_time: str
        - digest: str
        - content: str
        - read_count: int (可选)
        - comment_count: int (可选)
        """
        pass
