"""
Quản lý bộ nhớ ngắn hạn (Working Memory), chủ yếu là lịch sử hội thoại gần đây.
"""
from collections import deque
import config

class ShortTermMemory:
    def __init__(self):
        self.history = deque(maxlen=config.SHORT_TERM_MEMORY_MAX_MESSAGES)

    def add_message(self, role: str, content: str):
        """Thêm một tin nhắn vào lịch sử."""
        self.history.append({"role": role, "content": content})

    def get_recent_history(self) -> str:
        """Lấy lịch sử hội thoại gần đây dưới dạng chuỗi định dạng."""
        if not self.history:
            return None
        
        formatted_history = "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.history
        )
        return formatted_history
