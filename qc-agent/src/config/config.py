import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
import json

# Load environment variables from .env file at the project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# --- Load MCP Server Configurations from JSON ---
try:
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
    with open(config_path, 'r') as f:
        data = json.load(f)
        MCP_SERVERS_CONFIG = data.get("mcp_servers") or data.get("mcpServers") or {}
    print(f"[INFO] Loaded {len(MCP_SERVERS_CONFIG)} MCP server configurations.")
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"WARNING: Could not load 'config.json': {e}. No MCP servers will be available.")
    MCP_SERVERS_CONFIG = {}

# Jira Configuration
JIRA_URL = os.getenv("JIRA_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# API Configuration - Thử lấy cả hai biến env cho đồng bộ với test_llm.py
FPT_API_BASE = os.getenv("FPT_API_BASE") or os.getenv("FPT_BASE_URL") or "https://mkp-api.fptcloud.com"
FPT_API_KEY = os.getenv("FPT_API_KEY", "")

# Danh sách các model khả dụng để UI và Agent dùng chung
AVAILABLE_MODELS = [
    "Qwen3-32B",
    "SaoLa4-medium",
    "SaoLa-Llama3.1-planner",
    "SaoLa4-small",
    "SaoLa3.1-medium",
    "Llama-3.3-70B-Instruct",
    "Llama-3.3-Swallow-70B-Instruct-v0.4",
    "Qwen2.5-Coder-32B-Instruct",
    "Qwen3-Coder-480B-A35B-Instruct",
    "gpt-oss-120b",
    "gpt-oss-20b",
    "DeepSeek-V3.2-Speciale",
    "GLM-4.5",
    "GLM-4.7",
    "Kimi-K2.5",
    "Alpamayo-R1-10B",
    "Nemotron-3-Super-120B-A12B"
]

# Cấu hình Model theo Vai trò (Role-based)
FAST_PLANNER_MODEL = "SaoLa-Llama3.1-planner"
SENIOR_TESTER_MODEL = "gpt-oss-120b"

DEFAULT_MODEL = os.getenv("LLM_MODEL_NAME", "Qwen3-32B")
LLM_MODEL_NAME = DEFAULT_MODEL # Giữ lại để tương thích ngược

# MCP Server Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")

# WORKING DIR
WORKING_DIR = os.getenv("WORKING_DIR") or os.getcwd()

# Cấu hình Model
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" # Model embedding nhỏ gọn và hiệu quả

# --- Vector Database Configuration ---
# Change the 'provider' to 'chroma' or 'qdrant' to switch databases.
# Qdrant's ":memory:" mode is great for fast, non-persistent development.
# Chroma's "chroma_db" path creates a persistent on-disk database.
# OPTIONS: "qdrant", "chroma"
VECTOR_DB_PROVIDER = "qdrant"

VECTOR_DB_CONFIG = {
    "provider": VECTOR_DB_PROVIDER,
    "config": {
        "qdrant": {
            "host": "localhost",  # Use ":memory:" for in-memory or a file path for persistence
            "port": 6333,
            "collection_name": "agent_long_term_memory",
            "embedding_model_name": EMBEDDING_MODEL_NAME
        },
        "chroma": {
            "path": "chroma_db", # Directory to store the database files
            "collection_name": "agent_long_term_memory",
            "embedding_model_name": EMBEDDING_MODEL_NAME
        }
    }[VECTOR_DB_PROVIDER]
}


# --- Embedding Model Configuration ---
EMBEDDING_API_PROVIDER = "openai"  # Lựa chọn: "local" hoặc "openai" (trỏ sang FPT)
# Model cho nhà cung cấp "local" (chạy trên máy)
EMBEDDING_MODEL_NAME_LOCAL = "all-MiniLM-L6-v2" 
# Model cho nhà cung cấp "openai" (qua API) được trỏ sang FPT Cloud
EMBEDDING_MODEL_BASE_URL = FPT_API_BASE
# Model mặc định trên FPT Cloud thường là multilingual-e5-large
EMBEDDING_MODEL_NAME_OPENAI = os.getenv("EMBEDDING_MODEL_NAME", "multilingual-e5-large")
EMBEDDING_MODEL_API_KEY = FPT_API_KEY
# Kích thước vector của model multilingual-e5-large là 1024
EMBEDDING_DIMENSION_OPENAI = int(os.getenv("EMBEDDING_DIMENSION", "1024")) 

# --- Cấu hình RAG ---
USE_RERANKER = False  # Bật/tắt tính năng rerank
RERANKER_MODEL_NAME = 'cross-encoder/ms-marco-MiniLM-L-6-v2' # Model rerank
TOP_K_BROAD_RETRIEVAL = 10 # Số lượng kết quả lấy về ban đầu
TOP_K_FINAL_RERANK = 3    # Số lượng kết quả cuối cùng sau khi xếp hạng lại

# Cấu hình Short-Term Memory
SHORT_TERM_MEMORY_MAX_MESSAGES = 10 # Giữ lại 10 tin nhắn gần nhất

MCP_TOOLS={
    "playwright": {
      "url": "http://localhost:8931/mcp"
    }
}

PLAYWRIGHT_MCP_URL = MCP_TOOLS["playwright"]["url"]

# --- Initialized Clients ---

# JIRA HTTP Session
jira_session = requests.Session()
jira_session.auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN)

# OpenAI-compatible LLM Client configuration removed
# We now use direct requests in the agents for better gateway compatibility.

