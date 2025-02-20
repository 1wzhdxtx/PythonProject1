import pymysql
import json
import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch, helpers
from datetime import datetime


# 把这个换成主机ip
MYSQL_HOST = "192.168.1.10"
ES_HOST = "http://192.168.1.10:9200"

# MySQL 连接信息
user = input("请输入你的 MySQL 用户名 (默认: root): ") or "root"
pw = input("请输入你的 MySQL 密码: ")
db = input("请输入你想使用的数据库: ")


# Elasticsearch 配置（就是给索引起名）
INDEX_NAME = "web_scraped_data"

# 连接 Elasticsearch
es = Elasticsearch([ES_HOST])

# 创建 Elasticsearch 索引
def create_index():
    mapping = {
        "mappings": {
            "properties": {
                "url": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "standard"},
                "html": {"type": "text"},
                "timestamp": {"type": "date"}
            }
        }
    }
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body=mapping)
        print(f"[✔] Elasticsearch 索引 '{INDEX_NAME}' 已创建")
    else:
        print(f"[✔] Elasticsearch 索引 '{INDEX_NAME}' 已存在")

# 获取 HTML 内容，这有一个url变量需要衔接一下
def get_html(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"[✘] 获取 {url} 失败: {e}")
        return None

# 提取网页标题，这也有个变量
def extract_title(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.title.string if soup.title else "无标题"

# 连接 MySQL
try:
    connection = pymysql.connect(
        host=MYSQL_HOST,
        port=3306,
        user=user,
        password=pw,
        database=db,
        charset='utf8mb4',
        autocommit=True
    )
    print("[✔] 成功连接到 MySQL 数据库:", db)

    # 获取待爬取的 URL 列表
    with connection.cursor() as cursor:
        cursor.execute("SELECT url FROM web_scraped_urls")  # 读取待爬取的 URL
        url_list = [row[0] for row in cursor.fetchall()]

    # 存储数据
    data = []
    for url in url_list:
        html_content = get_html(url)
        if html_content:
            title = extract_title(html_content)
            extracted_data = json.dumps({"title": title})
            data.append((url, html_content, extracted_data))

    # 插入数据到 MySQL
    if data:
        with connection.cursor() as cursor:
            sql = "INSERT INTO web_scraped_data (url, html, extracted_data) VALUES (%s, %s, %s)"
            cursor.executemany(sql, data)
        print("[✔] 数据成功插入 MySQL")

        # 索引到 Elasticsearch
        es_data = [
            {
                "_index": INDEX_NAME,
                "_source": {
                    "url": url,
                    "title": json.loads(extracted_data)["title"],
                    "html": html_content,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            for url, html, extracted_data in data
        ]
        helpers.bulk(es, es_data)
        print(f"[✔] {len(es_data)} 条数据已索引到 Elasticsearch")

except pymysql.MySQLError as e:
    print("[✘] MySQL 错误:", e)

except Exception as e:
    print("[✘] 发生未知错误:", e)

finally:
    if 'connection' in locals() and connection.open:
        connection.close()
        print("[✔] 数据库连接已关闭")
# 搜索数据部分
keyword = input("请输入要搜索的关键字: ")
query = {"query": {"match": {"title": keyword}}}

try:
    results = es.search(index=INDEX_NAME, body=query, size=5)
    hits = results.get("hits", {}).get("hits", [])

    if hits:
        print("\n🔍 搜索结果:")
        for hit in hits:
            print(f"URL: {hit['_source']['url']}, 标题: {hit['_source']['title']}")
    else:
        print("⚠️ 未找到匹配的结果")
except Exception as e:
    print(f"[✘] Elasticsearch 查询失败: {e}")