# memory.py
"""
Orchestrator - Lớp quản lý chính, kết hợp tất cả các loại bộ nhớ
và lắp ráp prompt cuối cùng.
"""
import config
from .longterm_memory import LongTermMemory
from .shorterm_memory import ShortTermMemory
from .shared_memory import SharedMemory
from prompt.prompt_builder import builder

class MemoryManager:
    def __init__(self, shared_memory: SharedMemory = None):
        self.ltm = LongTermMemory()
        self.stm = ShortTermMemory()
        self.shared_memory = shared_memory
        
        # Cấu hình API theo môi trường mới
        self.api_key = config.FPT_API_KEY
        base_url = config.FPT_API_BASE.rstrip("/")
        if "/v1" not in base_url:
             base_url += "/v1"
        self.endpoint_url = f"{base_url}/chat/completions"
        self.model_name = getattr(config, 'LLM_MODEL_NAME', 'SaoLa4-medium')
        
    def _transform_query(self, latest_query, recent_history) -> str:
        # TODO: This is where a more advanced query transformation (like HyDE or Multi-Query) would be implemented.
        # For now, we'll keep the simple contextual combination.
        # print("\n[Orchestrator] Transforming query...")
        transformed = f"{recent_history}"
        return transformed

    async def _execute_llm_call(self, system_prompt: str, user_prompt: str) -> str:
        import requests
        import json
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0
        }
        
        try:
            response = requests.post(
                self.endpoint_url, 
                headers=headers, 
                json=payload, 
                timeout=60.0
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                print(f"[MEMORY-LOG] ❌ Lỗi API Memory: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            print(f"[MEMORY-LOG] ❌ Lỗi kết nối Memory: {str(e)}")
            return ""

    def assemble_prompt(self, agent_profile: dict, latest_query: str) -> str:
        """
        Thực hiện toàn bộ quy trình RAG tối ưu và lắp ráp prompt.
        """
        # print("\n===== Assembling Optimized Prompt =====")
        # 1. Lấy lịch sử gần đây từ STM
        recent_history = self.stm.get_recent_history()
        # print(f"Recent conversation history: {recent_history or 'No recent history'}")

        # 2. Biến đổi truy vấn
        transformed_query = self._transform_query(latest_query, recent_history)
        # print(f"Transformed query: {transformed_query}")

        # 3. Truy xuất từ LTM. The LTM now handles reranking internally.
        # We pass both the broad and final k values.
        retrieved_results = self.ltm.retrieve(
            query=transformed_query, 
            top_k_broad=config.TOP_K_BROAD_RETRIEVAL,
            top_k_final=config.TOP_K_FINAL_RERANK
        )
        # print(f"Final retrieved results (top {config.TOP_K_FINAL_RERANK}): {retrieved_results}")
        
        # 4. Lắp ráp các phần của prompt
        dynamic_data = {}
        dynamic_data['related_information'] = "\n".join(f"- {item}" for item in retrieved_results) if retrieved_results else None
        dynamic_data['recent_conversation'] = recent_history
        dynamic_data['shared_log'] = self.shared_memory.read_shared_log() if self.shared_memory is not None else None
        dynamic_data['current_task'] = latest_query
        
        # 5. Điền vào template
        template = builder.env.get_template("master_agent.jinja2")
        final_prompt = template.render(agent=agent_profile, data=dynamic_data)
        
        # print("===== Prompt Assembly Complete =====")
        return final_prompt
