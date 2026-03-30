"""
Quản lý bộ nhớ được chia sẻ giữa các agent.
Mô phỏng đơn giản bằng một dictionary. Trong thực tế, đây có thể là Redis hoặc một DB.
"""
from collections import deque

class SharedMemory:
    def __init__(self, max_log_size=50):
        # Một log chung mà tất cả agent có thể đọc/ghi
        self.shared_log = deque(maxlen=max_log_size)

    def write_to_shared_log(self, agent_id: str, message: str):
        """Một agent ghi thông tin vào bộ nhớ chung."""
        log_entry = f"Agent '{agent_id}': {message}"
        self.shared_log.append(log_entry)
        # print(f"Wrote to Shared Memory: {log_entry}")

    def read_shared_log(self, num_entries: int=-1) -> str:
        """Đọc N entry gần nhất từ bộ nhớ chung."""
        if num_entries == -1 or num_entries > len(self.shared_log):
            num_entries = len(self.shared_log)
        entries = list(self.shared_log)[-num_entries:]
        return "\n".join(entries) if entries else "No shared log entries."