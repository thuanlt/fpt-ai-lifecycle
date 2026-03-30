try:
    import sys
    import os
    sys.path.append('web_ui')
    sys.path.append('src')
    import server
    print("✅ server.py imported successfully!")
except Exception as e:
    import traceback
    traceback.print_exc()
