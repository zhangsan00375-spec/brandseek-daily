#!/usr/bin/env python3
import json, os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def generate_html_email(data: dict) -> str:
    assets = data.get("assets", []); news = data.get("news", [])
    date_str = datetime.now().strftime("%Y年%m月%d日")
    assets_html = ""
    if assets:
        for asset in assets:
            c = {"即将开拍": "#5A8BC4", "法拍中": "#D4553A", "已成交": "#4A9B6B", "招标中": "#D4943A", "公告": "#8C9DB5"}.get(asset.get("status", ""), "#8C9DB5")
            assets_html += f'<tr style="border-bottom:1px solid #e8edf214;"><td style="padding:12px 8px;"><span style="color:{c};font-size:11px;font-weight:600;">{asset.get("status", "-")}</span></td><td style="padding:12px 8px;"><a href="{asset.get("url", "#")}" style="color:#E8EDF2;text-decoration:none;font-weight:500;font-size:14px;">{asset.get("title", "")}</a><br/><span style="color:#8C9DB5;font-size:12px;">{asset.get("description", "")[:80]}</span></td><td style="padding:12px 8px;text-align:right;"><span style="color:#D4943A;font-weight:600;font-size:14px;">{asset.get("price", "-")}</span></td><td style="padding:12px 8px;text-align:center;"><span style="color:#8C9DB5;font-size:12px;">{asset.get("source", "-")}</span></td></tr>'
    else:
        assets_html = '<tr><td colspan="4" style="padding:20px;text-align:center;color:#8C9DB5;">今日暂无新标的</td></tr>'
    news_html = ""
    if news:
        for item in news:
            news_html += f'<tr style="border-bottom:1px solid #e8edf214;"><td style="padding:12px 8px;"><span style="background:rgba(212,148,58,0.15);color:#D4943A;font-size:10px;padding:2px 8px;border-radius:4px;">{item.get("category", "资讯")}</span></td><td style="padding:12px 8px;"><a href="{item.get("url", "#")}" style="color:#E8EDF2;text-decoration:none;font-weight:500;font-size:14px;">{item.get("title", "")}</a><br/><span style="color:#8C9DB5;font-size:12px;">{item.get("summary", "")[:100]}</span></td><td style="padding:12px 8px;text-align:center;"><span style="color:#8C9DB5;font-size:11px;">{item.get("source", "-")}</span></td></tr>'
    else:
        news_html = '<tr><td colspan="3" style="padding:20px;text-align:center;color:#8C9DB5;">今日暂无新资讯</td></tr>'
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body style="margin:0;padding:0;background-color:#0F1B33;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;"><table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0F1B33;"><tr><td align="center" style="padding:20px 10px;"><table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;"><tr><td style="padding:30px 20px;text-align:center;background-color:#111D36;border-radius:12px 12px 0 0;"><h1 style="color:#E8EDF2;font-size:24px;margin:0;font-weight:600;">BrandSeek 品牌资产日报</h1><p style="color:#8C9DB5;font-size:14px;margin:8px 0 0 0;">{date_str} · 自动采集自京东拍卖、阿里拍卖、法院公告等权威渠道</p></td></tr><tr><td style="padding:15px 20px;background-color:#1A2D4A;text-align:center;"><table width="100%" cellpadding="0" cellspacing="0"><tr><td style="text-align:center;padding:10px;"><span style="color:#D4943A;font-size:22px;font-weight:600;">{len(assets)}</span><br/><span style="color:#8C9DB5;font-size:12px;">新标的数据</span></td><td style="text-align:center;padding:10px;border-left:1px solid rgba(232,237,242,0.08);"><span style="color:#D4943A;font-size:22px;font-weight:600;">{len(news)}</span><br/><span style="color:#8C9DB5;font-size:12px;">行业资讯</span></td><td style="text-align:center;padding:10px;border-left:1px solid rgba(232,237,242,0.08);"><span style="color:#D4943A;font-size:22px;font-weight:600;">{len(assets) + len(news)}</span><br/><span style="color:#8C9DB5;font-size:12px;">总计</span></td></tr></table></td></tr><tr><td style="padding:20px;background-color:#1A2D4A;"><h2 style="color:#E8EDF2;font-size:18px;margin:0 0 15px 0;"><span style="color:#D4943A;margin-right:8px;">●</span>品牌资产标的</h2><table width="100%" cellpadding="0" cellspacing="0" style="font-size:13px;"><thead><tr style="border-bottom:2px solid rgba(232,237,242,0.15);"><th style="padding:8px;text-align:left;color:#8C9DB5;font-weight:500;width:60px;">状态</th><th style="padding:8px;text-align:left;color:#8C9DB5;font-weight:500;">标的名称</th><th style="padding:8px;text-align:right;color:#8C9DB5;font-weight:500;width:100px;">价格</th><th style="padding:8px;text-align:center;color:#8C9DB5;font-weight:500;width:80px;">来源</th></tr></thead><tbody>{assets_html}</tbody></table></td></tr><tr><td style="height:10px;"></td></tr><tr><td style="padding:20px;background-color:#1A2D4A;border-radius:0 0 12px 12px;"><h2 style="color:#E8EDF2;font-size:18px;margin:0 0 15px 0;"><span style="color:#D4943A;margin-right:8px;">●</span>行业资讯</h2><table width="100%" cellpadding="0" cellspacing="0" style="font-size:13px;"><thead><tr style="border-bottom:2px solid rgba(232,237,242,0.15);"><th style="padding:8px;text-align:left;color:#8C9DB5;font-weight:500;width:80px;">类别</th><th style="padding:8px;text-align:left;color:#8C9DB5;font-weight:500;">标题</th><th style="padding:8px;text-align:center;color:#8C9DB5;font-weight:500;width:80px;">来源</th></tr></thead><tbody>{news_html}</tbody></table></td></tr><tr><td style="padding:20px;text-align:center;"><p style="color:#5A6B82;font-size:11px;margin:0;">BrandSeek 品牌资产追踪 · 数据采集时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}<br/>数据来源: 京东拍卖、阿里拍卖、法院公告、Google News</p></td></tr></table></td></tr></table></body></html>"""

def send_via_smtp(to_email, html_content):
    host = os.environ.get("SMTP_HOST", "")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASSWORD", "")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"【BrandSeek日报】{datetime.now().strftime('%Y-%m-%d')} 品牌资产动态"
    msg["From"] = f"BrandSeek <{user}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    server = smtplib.SMTP(host, port)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()
    print(f"[SMTP] Sent to {to_email}")

def main():
    if not os.path.exists("crawl_result.json"):
        print("Error: crawl_result.json not found"); return
    with open("crawl_result.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    html = generate_html_email(data)
    with open("email_preview.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Preview saved to email_preview.html")
    to_email = os.environ.get("TO_EMAIL", "")
    if not to_email:
        print("Info: TO_EMAIL not set"); return
    try:
        send_via_smtp(to_email, html)
        print(f"Sent to {to_email}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    main()
