# 预定义提示模板，避免每次查询都重新拼接
CYPHER_PROMPT_TEMPLATE = """你是一个专业的Neo4j Cypher查询生成器，需要根据用户问题和知识图谱结构生成准确、可执行的Cypher查询语句。

### 知识图谱结构：
{schema}

### 用户问题：
{question}

### 生成要求：
1. 严格遵循Cypher语法规范
2. 只使用知识图谱中定义的关系和节点类型
3. 确保查询逻辑与问题意图完全匹配
4. 只返回Cypher语句，不要任何解释或注释

### 示例查询：
问题1："水稻病害都有哪些？"
查询：MATCH (n:水稻病害) RETURN n

问题2："给一张水稻条纹叶枯病的图片"
查询：MATCH (i:图像)-[:imageOf]->(d:水稻病害) WHERE d.name = '水稻条纹叶枯病' RETURN i.name, i.imageURL

"""

# 优化后的回答生成函数
ANSWER_PROMPT_TEMPLATE = {
    'no_data': """你是一名农业专家，需要回答关于水稻的问题。
由于没有知识图谱数据，请基于你的知识直接回答。
回答要求：
- 使用markdown格式，如果有图片(图像)链接，必须访问链接将图片展示出来

问题：{query}""",
    
    'with_data': """你是一名农业专家，需要根据知识图谱数据回答关于水稻的问题。
数据来源：{db_response}

回答要求：
- 将查到的内容直接展示，不用另作判断
- 使用markdown格式，如果有图片(图像)imageURL，必须将图片展示出来
- 若数据为空，直接回答"抱歉，根据知识图谱内容并未找到相关数据。"

问题：{query}"""
}

examples = [
    {
        "question": "水稻病害都有哪些？",
        "cypher": "MATCH (n:水稻病害) WHERE n.label = '水稻病害' RETURN n"
    },
    {
        "question": "水稻病害",
        "cypher": "MATCH (n:水稻病害) RETURN n"
    },
    {
        "question": "给一张水稻条纹叶枯病的图片",
        "cypher": "MATCH (i:图像)-[:imageOf]->(d:水稻病害) WHERE d.name = '水稻条纹叶枯病' RETURN i.name, i.imageURL"
    }
]