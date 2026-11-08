from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseExecutor(ABC):
    @abstractmethod
    def dispatch_comment(self, article: Dict[str, Any], comments: List[Dict[str, str]]) -> bool:
        """
        分发或执行留言动作
        """
        pass
