from flask import Flask, Response
from flask_cors import CORS
import requests
from datetime import datetime
import json
import urllib.parse
import os

app = Flask(__name__)
CORS(app)  # 允许所有跨域

# ------------------ 各平台爬虫函数 ------------------

def fetch_douyin_hotwords():
    url = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15",
        "Referer": "https://www.douyin.com/"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        active_time_fmt = ""
        if data.get("active_time"):
            active_time = datetime.strptime(data["active_time"], "%Y-%m-%d %H:%M:%S")
            active_time_fmt = active_time.strftime("%H:%M")
        hot_words = []
        for item in data.get("word_list", [])[:10]:
            word = item.get("word", "")
            hot_value = item.get("hot_value", 0)
            link = f"https://www.douyin.com/search/{urllib.parse.quote(word)}"
            hot_words.append({
                "word": word,
                "hot_value": hot_value,
                "time": active_time_fmt,
                "link": link
            })
        return hot_words
    except:
        return []

def fetch_bilibili_hotwords():
    url = "https://api.bilibili.com/x/web-interface/search/square?limit=10&platform=web"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15"
    }
    try:
        resp = requests.get(url, timeout=10, headers=headers)
        data = resp.json()
        hot_words = []
        now_time = datetime.now().strftime("%H:%M")
        for item in data.get("data", {}).get("trending", {}).get("list", [])[:10]:
            word = item.get("show_name", "")
            link = f"https://search.bilibili.com/all?keyword={urllib.parse.quote(word)}"
            hot_words.append({
                "word": word,
                "hot_value": None,
                "time": now_time,
                "link": link
            })
        return hot_words
    except:
        return []

def fetch_weibo_hotwords():
    url = "https://v2.xxapi.cn/api/weibohot"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        now_time = datetime.now().strftime("%H:%M")
        hot_words = []
        if data.get("code") == 200:
            for item in data.get("data", [])[:10]:
                word = item.get("title", "")
                hot_value = item.get("hot", "")
                link = item.get("url", f"https://s.weibo.com/weibo?q={urllib.parse.quote(word)}")
                hot_words.append({
                    "word": word,
                    "hot_value": hot_value,
                    "time": now_time,
                    "link": link
                })
        return hot_words
    except Exception as e:
        print(f"微博热搜抓取异常: {e}")
        return []

def fetch_baidu_hotwords():
    url = "https://top.baidu.com/api/board?platform=wise&tab=realtime"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        now_time = datetime.now().strftime("%H:%M")
        hot_words = []
        for item in data.get("data", {}).get("cards", [])[0].get("content", [])[:10]:
            word = item.get("query", "")
            hot_value = item.get("hotScore", 0)
            link = f"https://www.baidu.com/s?wd={urllib.parse.quote(word)}"
            hot_words.append({
                "word": word,
                "hot_value": hot_value,
                "time": now_time,
                "link": link
            })
        return hot_words
    except:
        return []

def fetch_toutiao_hotwords():
    url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        now_time = datetime.now().strftime("%H:%M")
        hot_words = []
        for item in data.get("data", [])[:10]:
            word = item.get("Title", "")
            link = item.get("Url", "")
            hot_words.append({
                "word": word,
                "hot_value": None,
                "time": now_time,
                "link": link
            })
        return hot_words
    except:
        return []

def fetch_csdn_hotwords():
    url = "https://blog.csdn.net/phoenix/web/blog/hotRank?&pageSize=100"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        now_time = datetime.now().strftime("%H:%M")
        hot_words = []
        if data.get("code") == 200 and "data" in data:
            for item in data["data"][:10]:
                word = item.get("articleTitle", "")
                hot_value = item.get("hotRankScore", 0)
                link = item.get("articleDetailUrl", "")
                hot_words.append({
                    "word": word,
                    "hot_value": hot_value,
                    "time": now_time,
                    "link": link
                })
        return hot_words
    except Exception as e:
        print(f"CSDN热搜抓取异常: {e}")
        return []

# ------------------ 聚合接口 ------------------

@app.route("/", methods=["GET"])
def hotwords_all():
    result = {
        "code": 0,
        "message": "success",
        "data": {
            "douyin": fetch_douyin_hotwords(),
            "bilibili": fetch_bilibili_hotwords(),
            "weibo": fetch_weibo_hotwords(),
            "baidu": fetch_baidu_hotwords(),
            "toutiao": fetch_toutiao_hotwords(),
            "csdn": fetch_csdn_hotwords()
        }
    }
    json_str = json.dumps(result, ensure_ascii=False)
    return Response(json_str, content_type="application/json; charset=utf-8")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"多平台热搜接口启动：http://0.0.0.0:{port}/")
    app.run(host="0.0.0.0", port=port, debug=True)
