#!/bin/bash

# This script reads the configuration from config/config.py and starts the 
# appropriate vector database server if required.

# --- Configuration ---
# Find the config file relative to the script's location.
# This makes the script runnable from any directory.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
CONFIG_FILE="$SCRIPT_DIR/src/config/config.py"

# --- Main Logic ---

# 1. Check if the config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: Configuration file not found at $CONFIG_FILE"
    exit 1
fi

# 2. Extract the VECTOR_DB_PROVIDER value from the config file
# This command uses grep to find the line and sed to extract the value inside the quotes.
PROVIDER=$(grep "VECTOR_DB_PROVIDER =" "$CONFIG_FILE" | sed -n 's/.*"\(.*\)"/\1/p')

echo "🔎 Detected Vector DB Provider: '$PROVIDER'"

# 3. Start the appropriate database based on the provider
if [ "$PROVIDER" == "qdrant" ]; then
    # Create a directory for persistent storage in the project root
    STORAGE_DIR="$SCRIPT_DIR/qdrant_data"
    mkdir -p "$STORAGE_DIR"
    echo "💾 Qdrant data will be stored persistently in: $STORAGE_DIR"

    echo "🚀 Attempting to start Qdrant via Docker..."
    # Check if a container named qdrant_db is already running
    if [ "$(docker ps -q -f name=qdrant_db)" ]; then
        echo "✅ Qdrant container 'qdrant_db' is already running."
    else
        echo "🐳 Pulling the latest qdrant/qdrant image..."
        docker pull qdrant/qdrant
        
        echo "🔥 Starting a new Qdrant container named 'qdrant_db' on port 6333..."
        # -d: run in detached mode (in the background)
        # --rm: automatically remove the container when it exits
        # -p: map port 6333 on the host to 6333 in the container
        # -v: mount the local storage directory to the container's storage path
        docker run -d --rm -p 6333:6333 \
            -v "$STORAGE_DIR":/qdrant/storage \
            --name qdrant_db qdrant/qdrant
        
        echo "✅ Qdrant container started successfully. It may take a moment to initialize."
    fi

elif [ "$PROVIDER" == "chroma" ]; then
    echo "✅ ChromaDB is configured."
    echo "ℹ️  ChromaDB runs as an embedded database within the Python application."
    echo "   No separate server process is required."

else
    echo "⚠️  Warning: Unsupported or unknown VECTOR_DB_PROVIDER ('$PROVIDER') in config file."
    echo "   No services will be started."
fi

