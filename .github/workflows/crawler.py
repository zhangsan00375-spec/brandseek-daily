#!/usr/bin/env python3
"""BrandSeek 品牌资产采集器"""
import json, re, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class AssetItem:
    title: str
    source: str
    status: str
    price: str
    url: str
    date: str
    description: str = ""
    industry: str = ""
    region: str = ""


@dataclass
class NewsItem:
    title: str
    source: str
    date: str
    summary: str
    url: str
    category: str = ""


class JdAuctionCrawler:
    KEYWORDS = ["商标", "品牌", "股权", "老字号", "特许经营", "加盟权"]

    def crawl(self):
        items = []
        for kw in self.KEYWORDS:
            try:
                url = f"https://auction-api.jd.com/auction/list?page=1&pageSize=20&keyword={urllib.parse.quote(kw)}"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://auction.jd.com/"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                for item in data.get("data", {}).get("list", []):
                    title = item.get("title", "")
                    if any(k in title for k in ["商标", "品牌", "字号", "专利", "加盟", "特许", "股权", "老字号"]):
                        items.append(AssetItem(
                            title=title,
                            source="京东拍卖",
                            status={"1": "即将开拍", "2": "法拍中", "3": "已成交", "4": "流拍"}.get(item.get("status", ""), "拍卖中"),
                            price=f"¥{item.get('startPrice', '0'):,.0f}",
                            url=f"https://auction.jd.com/{item.get('id', '')}",
                            date=item.get("startTime", "")[:10],
                            description=item.get("description", "")[:200],
                            region=item.get("region", ""),
                        ))
            except Exception as e:
                print(f"[JD] '{kw}' failed: {e}")
        return items[:10]


class AliAuctionCrawler:
    KEYWORDS = ["商标", "品牌", "股权", "老字号"]

    def crawl(self):
        items = []
        for kw in self.KEYWORDS:
            try:
                url = f"https://zc-paimai.taobao.com/zc/zc_item_list.htm?q={urllib.parse.quote(kw)}"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    content = resp.read().decode("utf-8", errors="ignore")
                matches = re.findall(r'"id":"(\d+)".*?"title":"([^"]*商标[^"]*)".*?"startPrice":"?([\d.]+)"?.*?"status":"?(\d)"?.*?"startTime":"([^"]*)"', content, re.DOTALL)
                for item_id, title, price, status, start_time in matches:
                    items.append(AssetItem(
                        title=title,
                        source="阿里拍卖",
                        status={"0": "即将开拍", "1": "法拍中", "2": "已成交"}.get(status, "拍卖中"),
                        price=f"¥{float(price):,.0f}",
                        url=f"https://zc-paimai.taobao.com/zc/zc_item.htm?id={item_id}",
                        date=start_time[:10] if start_time else "",
                    ))
            except Exception as e:
                print(f"[ALI] '{kw}' failed: {e}")
        return items[:10]


class GoogleNewsCrawler:
    KEYWORDS = ["商标拍卖", "品牌转让", "破产拍卖 商标", "老字号商标", "消费品牌 股权"]

    def crawl(self):
        items = []
        for kw in self.KEYWORDS:
            try:
                url = f"https://news.google.com/rss/search?q={urllib.parse.quote(kw)}&hl=zh-CN&gl=CN&ceid=CN:zh"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    content = resp.read()
                root = ET.fromstring(content)
                for item in root.findall(".//item")[:5]:
                    title_el = item.find("title")
                    link_el = item.find("link")
                    pub_date = item.find("pubDate")
                    desc_el = item.find("description")
                    src_el = item.find("source")
                    if title_el is not None and link_el is not None:
                        date_str = ""
                        if pub_date is not None and pub_date.text:
                            try:
                                date = datetime.strptime(pub_date.text, "%a, %d %b %Y %H:%M:%S %Z")
                                if datetime.now() - date > timedelta(days=7):
                                    continue
                                date_str = date.strftime("%Y-%m-%d")
                            except:
                                date_str = pub_date.text[:10]
                        summary = ""
                        if desc_el is not None and desc_el.text:
                            summary = re.sub(r'<[^>]+>', '', desc_el.text)[:200]
                        cat = "行业动态"
                        t = title_el.text or ""
                        if "成交" in t or "拍出" in t:
                            cat = "拍卖成交"
                        elif "破产" in t:
                            cat = "破产拍卖"
                        elif "转让" in t:
                            cat = "品牌转让"
                        items.append(NewsItem(
                            title=t,
                            source=src_el.text if src_el is not None else "Google News",
                            date=date_str,
                            summary=summary,
                            url=link_el.text or "",
                            category=cat,
                        ))
            except Exception as e:
                print(f"[NEWS] '{kw}' failed: {e}")
        seen = set()
        result = []
        for item in items:
            key = item.title[:30]
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result[:15]


class CourtAnnouncementCrawler:
    def crawl(self):
        items = []
        for kw in ["商标", "品牌", "拍卖"]:
            try:
                url = f"https://rmfygg.court.gov.cn/web/rmfyportal/noticleInfo?keyword={urllib.parse.quote(kw)}&columnId=6"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    content = resp.read().decode("utf-8", errors="ignore")
                matches = re.findall(r'<a[^>]*href="(/web/rmfyportal/noticleInfo\?[^"]*id=([^"&]+)[^"]*)"[^>]*>([^<]*(?:商标|品牌|拍卖)[^<]*)</a>', content, re.IGNORECASE)
                for href, notice_id, title in matches[:5]:
                    items.append(AssetItem(
                        title=title.strip(),
                        source="法院公告",
                        status="公告",
                        price="-",
                        url=f"https://rmfygg.court.gov.cn{href}",
                        date=datetime.now().strftime("%Y-%m-%d"),
                        description="法院破产拍卖公告",
                    ))
            except Exception as e:
                print(f"[COURT] '{kw}' failed: {e}")
        return items[:8]


class BrandSeekCrawler:
    def __init__(self):
        self.crawlers = {
            "jd": JdAuctionCrawler(),
            "ali": AliAuctionCrawler(),
            "news": GoogleNewsCrawler(),
            "court": CourtAnnouncementCrawler(),
        }

    def run(self):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}\nBrandSeek Crawl - {ts}\n{'='*60}\n")
        all_assets = []
        all_news = []
        stats = {}

        for name in ["jd", "ali"]:
            print(f"[Crawl] {name}...")
            try:
                items = self.crawlers[name].crawl()
                all_assets.extend(items)
                stats[name] = len(items)
                print(f"  -> {len(items)} items")
            except Exception as e:
                print(f"  -> failed: {e}")
                stats[name] = 0

        print("[Crawl] court...")
        try:
            court_items = self.crawlers["court"].crawl()
            all_assets.extend(court_items)
            stats["court"] = len(court_items)
            print(f"  -> {len(court_items)} items")
        except Exception as e:
            print(f"  -> failed: {e}")
            stats["court"] = 0

        print("[Crawl] news...")
        try:
            news_items = self.crawlers["news"].crawl()
            all_news.extend(news_items)
            stats["news"] = len(news_items)
            print(f"  -> {len(news_items)} items")
        except Exception as e:
            print(f"  -> failed: {e}")
            stats["news"] = 0

        seen_a = set()
        result_a = []
        for item in all_assets:
            key = item.title[:20]
            if key not in seen_a:
                seen_a.add(key)
                result_a.append(item)

        seen_n = set()
        result_n = []
        for item in all_news:
            key = item.title[:25]
            if key not in seen_n:
                seen_n.add(key)
                result_n.append(item)

        total = len(result_a) + len(result_n)
        print(f"\nDone: {len(result_a)} assets + {len(result_n)} news = {total} total\n")

        return {
            "assets": [asdict(a) for a in result_a],
            "news": [asdict(n) for n in result_n],
            "stats": stats,
            "timestamp": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    result = BrandSeekCrawler().run()
    with open("crawl_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("Saved to crawl_result.json")
