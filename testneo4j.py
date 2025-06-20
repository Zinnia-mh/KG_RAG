from neo4j import GraphDatabase
import os

auth_token = os.getenv("NEO4J_PASSWORD")
DB = os.getenv("NEO4J_DB")

uri = "neo4j://localhost:7687"
driver = GraphDatabase.driver(
    uri, 
    auth=("neo4j", auth_token),
    database=DB)  # 使用元组

try:
    with driver.session() as session:
        result = session.run("RETURN 1 AS x")  # 缩进修复
        print("连接成功:", result.single()["x"])  # 括号补全
except Exception as e:
    print("连接失败:", e)
finally:
    driver.close()