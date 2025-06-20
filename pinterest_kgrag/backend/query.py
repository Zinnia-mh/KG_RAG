from json import load
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_core.prompts.prompt import PromptTemplate
from dsllm import DeepSeekLLM
import os
from functools import lru_cache
import time
# from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from sources.prompt_cypher import CYPHER_PROMPT_TEMPLATE, ANSWER_PROMPT_TEMPLATE, examples

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

@lru_cache(maxsize=100)  # 最多缓存100个不同查询
def cached_answer(prompt):
    # 只有参数组合未缓存过才会执行这里
    llm = get_llm_instance()
    return llm.invoke(prompt)

# 优化后的查询函数
def query_database(query):
    
    try:
        startime = time.time()
        graph = get_graph_connection()
        llm = get_llm_instance()

        # 脱离langchain查询
        # cypherdata = llm.invoke(prompt)
        # print(f"Database query data: {cypherdata}")
        # # 清洗输出（移除可能的额外解释）
        # cypher = cypherdata.strip()
        # if "```" in cypher:  # 处理可能存在的代码块标记
        #     cypher = cypher.split("```")[1].replace("cypher", "").strip()
        # print(f"Database query cypher: {cypher}")
        # result = graph.query(cypher)
        # print(f"Database query result: {result}")
        # endtime = time.time()
        # print(f"Database query time: {endtime - startime}s")
        # return (result, graph.get_schema)
        cypher_prompt = PromptTemplate(
            input_variables=["schema", "question"], 
            template=CYPHER_PROMPT_TEMPLATE
        )

        chain = GraphCypherQAChain.from_llm(
            llm,
            graph=graph,
            verbose=False,  # 关闭详细日志以提升性能
            cypher_prompt=cypher_prompt,
            return_direct=True,
            validate_cypher=True,
            top_k=20,  # 减少返回结果数量
            allow_dangerous_requests=True,
            return_intermediate_steps=True
        )
        
        response = chain.invoke(query)
        result = response['result']
        print(f"Database query data: {result}")
        endtime = time.time()
        print(f"Database query time: {endtime - startime}s")
        return (result, graph.get_schema)
    except Exception as e:
        print(f"Database query error: {str(e)}")
        return ('[]', "[]")

def find_answer(query, context):
    llm = get_llm_instance()

    if query['open_graph'] == True:
        if isinstance(context['db_response'], list) and len(context['db_response']) == 0:
            print("db_response is empty")
            return "抱歉，根据知识图谱内容并未找到相关数据。"
        elif not isinstance(context['db_response'], list) and context['db_response'].strip() == '[]':
            print("db_response is '[]'")
            return "抱歉，根据知识图谱内容并未找到相关数据。"
        else:
            prompt = ANSWER_PROMPT_TEMPLATE['with_data'].format(
                db_response=context['db_response'],
                query=query['question']
            )
            print("kg prompt")
    else:
        prompt = ANSWER_PROMPT_TEMPLATE['no_data'].format(query=query['question'])
        print("llm prompt")
    
    print("is open graph: ", query['open_graph'])
    # 若查到的内容相同，则直接从缓存中调用
    return cached_answer(prompt)
    return llm.invoke(prompt)

# 主查询函数
def query(query_dict):
    time_start = time.time()
    if query_dict['open_graph'] == True:
        db_response, schema = query_database(query_dict['question'])
    else:
        db_response = '[]'
        schema = '不使用知识图谱回答问题'

    result = find_answer(
        query_dict,
        context={
            'schema': schema,
            'db_response': db_response
        }
    )

    time_end = time.time()
    print(f"Query time: {time_end - time_start}s")
    return result

if __name__ == '__main__':
    user_query = input("> ")
    query_dict = {
        'question': user_query,
        'open_graph': True  # 默认使用知识图谱
    }
    
    response = query(query_dict)
    print(response)