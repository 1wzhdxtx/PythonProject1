import pymysql

# 获取用户输入的数据库信息
ip = input("请输入你的数据库服务器地址 (默认: 127.0.0.1): ") or "127.0.0.1"
user = input("请输入你的用户名 (默认: root): ") or "root"
pw = input("请输入你的密码: ")
db = input("请输入你想进入的数据库: ")

try:
    # 连接 MySQL
    connection = pymysql.connect(
        host=ip,
        port=3306,
        user=user,
        password=pw,
        database=db,
        charset='utf8mb4',
        autocommit=True
    )

    print("[✔] 成功连接到 MySQL 数据库:", db)

    # 创建游标对象
    with connection.cursor() as cursor:
        # 动态数据的插入
        for url in url_list:
            html_content = get_html(url)
            title = extract_title(html_content)
            extracted_data = json.dumps({"title": title})
            data.append((url, html_content, extracted_data))
        # SQL 插入语句
        sql = "INSERT INTO web_scraped_data (url, html, extracted_data) VALUES (%s, %s, %s)"

        # 执行插入
        cursor.executemany(sql, data)

    print("[✔] 数据成功插入到表 web_scraped_data")

except pymysql.MySQLError as e:
    print("[✘] MySQL 错误:", e)

except Exception as e:
    print("[✘] 发生未知错误:", e)

finally:
    # 关闭数据库连接
    if 'connection' in locals() and connection.open:
        connection.close()
        print("[✔] 数据库连接已关闭")