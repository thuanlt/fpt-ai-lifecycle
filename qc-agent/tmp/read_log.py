try:
    with open('tmp/server_stdout.log', 'rb') as f:
        content = f.read().decode('utf-16')
    print(content[-5000:]) # Print the last 5000 characters
except Exception as e:
    print(f"Error: {e}")
