import requests
import json
import config

def send_markdown_summary(total: int, passed: int, failed: int, jira_link: str = ""):
    """
    Gửi tin nhắn Markdown tóm tắt: 'Tổng số test: 50 | Pass: 48 | Fail: 2 (Link Jira: ...)'
    """
    message = f"**Báo cáo Fast Track MVP**\n\nTổng số test: {total} | Pass: {passed} | Fail: {failed}"
    if jira_link:
        message += f"\n(Link Jira: {jira_link})"
        
    print(f"💬 [Comms Agent] Sending notification:\n{message}")
    
    # Giả định gửi qua Webhook MS Teams/Telegram
    teams_webhook = getattr(config, 'TEAMS_WEBHOOK_URL', None)
    if teams_webhook:
        try:
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "0076D7",
                "summary": "Báo cáo Kiểm thử",
                "sections": [{
                    "activityTitle": "Fast Track Testing Status",
                    "text": message
                }]
            }
            requests.post(teams_webhook, json=payload)
            print("✅ Alert sent to MS Teams.")
        except Exception as e:
            print(f"❌ Failed to send MS Teams alert: {e}")
            
    telegram_token = getattr(config, 'TELEGRAM_BOT_TOKEN', None)
    telegram_chat = getattr(config, 'TELEGRAM_CHAT_ID', None)
    if telegram_token and telegram_chat:
        try:
            url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            payload = {
                "chat_id": telegram_chat,
                "text": message,
                "parse_mode": "Markdown"
            }
            requests.post(url, json=payload)
            print("✅ Alert sent to Telegram.")
        except Exception as e:
            print(f"❌ Failed to send Telegram alert: {e}")
