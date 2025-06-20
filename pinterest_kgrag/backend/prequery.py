from json import load
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_core.prompts.prompt import PromptTemplate
from dsllm import DeepSeekLLM
import os
from functools import lru_cache

# 全局变量初始化
api_key = os.environ.get("SILICONCLOUD_API_KEY")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE")

# 缓存数据库连接和模型实例
@lru_cache(maxsize=1)
def get_graph_connection():
    """缓存Neo4j连接，避免每次查询都重新连接"""
    with open('pinterest_kgrag/backend/sources/neo4j.json') as fp:
        credentials = load(fp)
    assert credentials['NEO4J_URI'].startswith("neo4j://")
    
    return Neo4jGraph(
        url=credentials['NEO4J_URI'],
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        database=NEO4J_DATABASE
    )

# 缓存LLM实例
@lru_cache(maxsize=1)
def get_llm_instance():
    """缓存LLM实例，避免重复初始化"""
    return DeepSeekLLM(api_key=api_key)

# 预定义提示模板，避免每次查询都重新拼接
CYPHER_PROMPT_TEMPLATE = """任务: 你是一个水稻知识图谱查询助手，需根据用户问题生成Cypher查询语句，并根据生成的Cypher语句查询知识图谱，查询到的数据不允许截断。
约束条件：
- 禁止解释或添加注释，只返回Cypher语句
- 禁止在查询中添加 LIMIT 子句

输出要求：
   - 仅返回Cypher语句，不要任何解释
   - 确保查询语法正确

知识图谱结构：{schema}

用户问题：{question}"""

# 优化后的查询函数
def query_database(query):
    try:
        graph = get_graph_connection()
        llm = get_llm_instance()
        
        prompt = PromptTemplate(
            input_variables=["schema", "question"], 
            template=CYPHER_PROMPT_TEMPLATE
        )

        chain = GraphCypherQAChain.from_llm(
            llm,
            graph=graph,
            verbose=False,  # 关闭详细日志以提升性能
            cypher_prompt=prompt,
            return_direct=True,
            validate_cypher=True,
            top_k=50,  # 减少返回结果数量
            allow_dangerous_requests=True
        )
        
        return (chain.invoke(query), graph.get_schema)
    except Exception as e:
        print(f"Database query error: {str(e)}")
        return ('[]', "[]")

# 优化后的回答生成函数
ANSWER_PROMPT_TEMPLATE = {
    'no_data': """你是一名农业专家，需要回答关于水稻的问题。
由于没有知识图谱数据，请基于你的知识直接回答。
回答要求：
- 使用中文回答
- 使用markdown格式进行答案的排版，不要使用h1-h4标签
- 如果有图片链接，则将图片链接嵌入到答案中展示出来
- 将答案中多个连续的换行符合并成一个换行符

问题：{query}""",
    
    'with_data': """你是一名农业专家，需要根据知识图谱数据回答关于水稻的问题。
数据来源：{db_response}

回答要求：
- 使用中文回答
- 不要将数据库中结点信息显示出来，例如ID、label等
- 将答案中多个连续的换行符合并成一个换行符
- 使用markdown格式进行答案的排版，不要使用h1-h4标签
- 如果有图片链接，则将图片链接嵌入到答案中展示出来
- 若知识图谱中没查找到相关数据，不用自动生成答案，而是直接回答"抱歉，根据知识图谱内容并未找到相关数据。"

问题：{query}"""
}

def find_answer(query, context):
    llm = get_llm_instance()
    
    if context['db_response'] == '[]' and query.get('open_graph', False) == False:
        prompt = ANSWER_PROMPT_TEMPLATE['no_data'].format(query=query['question'])
    else:
        prompt = ANSWER_PROMPT_TEMPLATE['with_data'].format(
            db_response=context['db_response'],
            query=query['question']
        )
    
    return llm.invoke(prompt)

# 主查询函数
def query(query_dict):
    if query_dict['open_graph'] == False:
        db_response, schema = query_database(query_dict['question'])
    else:
        db_response = '[]'
        schema = '不使用知识图谱回答问题'

    return find_answer(
        query_dict,
        context={
            'schema': schema,
            'db_response': db_response
        }
    )

if __name__ == '__main__':
    user_query = input("> ")
    query_dict = {
        'question': user_query,
        'open_graph': True  # 默认使用知识图谱
    }
    
    response = query(query_dict)
    print(response)