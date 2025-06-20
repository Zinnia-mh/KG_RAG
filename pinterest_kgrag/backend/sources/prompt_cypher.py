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
回答要求：
- 使用markdown格式，如果有图片(图像)链接，必须访问链接将图片展示出来

问题：{query}""",

    'with_data': """你是一名农业专家，需要根据知识图谱数据提取主要文字信息，不用给出任何其他说明。
数据来源：{db_response}

回答要求：
1. 数据展示：
- 给出文字即可，禁止使用Markdown语法渲染
- 多条数据之间用换行符分隔
2. 图片处理：
- 若存在图片链接（image/img_url/imageURL等字段），转换为纯文本格式：[图片](图片URL)
- 禁止渲染为Markdown图片语法（即不要用![]()）
""",    
    
    'with_data_response': """你是一名农业专家，需要根据知识图谱数据回答关于水稻的问题。
数据来源：{db_response}

回答要求
1. 数据展示：
- 使用Markdown语法渲染
- 忽略辅助性字段（如id/timestamp等）
2. 图片处理：
- 如果数据包含图片URL（字段名为 image/imageURL/img_url 等），必须用Markdown图片语法显示
- 示例：![水稻条纹叶枯病图1](/static/images/I0001.jpg)
- 多个图片需换行显示
3. 格式规范：
- 病害信息使用无序列表呈现
- 关键数据加粗显示（如发病率、防治方法）
- 不同数据类别用##二级标题分隔
4. 空数据处理：
- 如果输入数据是空列表/空数组，直接返回："抱歉，根据知识图谱内容并未找到相关数据。"

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