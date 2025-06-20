#
# query.py
#
# Purpose: Contains functionality to query the Neo4j database.
# Imports.
from json import load
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts.prompt import PromptTemplate
from dsllm import DeepSeekLLM
import os

api_key = os.environ.get("SILICONCLOUD_API_KEY")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE")

# 加载模型
# model_name = 'llama3.2:latest'
# llm = OllamaLLM(model=model_name)

# deepseek模型
llm = DeepSeekLLM(api_key = api_key)

def query_database(query):

    # 从neo4j.json加载数据库凭据（URI/用户名/密码）
    with open('pinterest_kgrag/backend/sources/neo4j.json') as fp:
        credentials = load(fp)
    assert credentials['NEO4J_URI'].startswith("neo4j://")

    graph = Neo4jGraph(
        url      = credentials['NEO4J_URI'],
        username = NEO4J_USERNAME,
        password = NEO4J_PASSWORD,
        database = NEO4J_DATABASE
    )

    # 通过Prompt模板生成Cypher语句并执行查询
    prompt_template = ' '.join([
        "任务: 你是一个水稻知识图谱查询助手，需根据用户问题生成Cypher查询语句，并根据生成的Cypher语句查询知识图谱，查询到的数据不允许截断。\n"
        "约束条件：\n"
        "- 禁止解释或添加注释，只返回Cypher语句\n"
        "- 禁止在查询中添加 LIMIT 子句\n\n" 
        " 输出要求：\n"
        "   - 仅返回Cypher语句，不要任何解释\n"
        "   - 确保查询语法正确\n\n"
        "知识图谱结构：\n{schema}\n\n"
        "用户问题：{question}"
    ])

    prompt = PromptTemplate(
        input_variables=["schema", "question"], template=prompt_template
    )

    chain = GraphCypherQAChain.from_llm(
        llm,
        graph=graph,
        verbose=True,
        cypher_prompt=prompt,
        return_direct=True,
        validate_cypher=True,
        # return_intermediate_steps=True, # 返回中间步骤
        top_k = 20,
        allow_dangerous_requests = True
    )
    # cypher_data = llm.invoke(prompt_template)
    # print('cypher_data:', cypher_data)

    # result = graph.query(cypher_data)
    # print('result:', result)

    # return ('[]', graph.get_schema)
    try:
        return (chain.invoke(query), graph.get_schema)
    except:
        return ('[]', graph.get_schema)
    
# 接收query_database返回的图谱数据（context）和schema，并调用find_answer函数生成回答
def find_answer(query, context):

    # 如果数据库返回空数据，直接让 LLM 回答
    if context['db_response'] == '[]' and not query['open_graph']:
        return llm.invoke(' '.join([
            "你是一名农业专家，需要回答关于水稻的问题。\n"
            "由于没有知识图谱数据，请基于你的知识直接回答。\n"
            "回答要求：\n"
            "- 使用中文回答\n"
            "- 使用markdown格式进行答案的排版，不要使用h1-h4标签\n"
            "- 如果有图片链接，则将图片链接嵌入到答案中展示出来\n"
            "- 将答案中多个连续的换行符合并成一个换行符\n\n"
            f"问题：{query}"
        ]))
    else:
        # 原有逻辑（如果有知识图谱数据）
        return llm.invoke(' '.join([
            "你是一名农业专家，需要根据知识图谱数据回答关于水稻的问题。\n"
            f"数据来源：\n{context['db_response']}\n\n"
            "回答要求：\n"
            "- 使用中文回答\n"
            "- 不要将数据库中结点信息显示出来，例如ID、label等"
            "- 将答案中多个连续的换行符合并成一个换行符\n"
            "- 使用markdown格式进行答案的排版，不要使用h1-h4标签\n"
            "- 如果有图片链接，则将图片链接嵌入到答案中展示出来\n"
            "- 若知识图谱中没查找到相关数据，不用自动生成答案，而是直接回答“抱歉，根据知识图谱内容并未找到相关数据。”\n\n"
            f"问题：{query}"
        ]))

# 整合前两个函数，实现端到端的问答流程
def query(query):
    print("is open graph?", query['open_graph'])
    if query['open_graph'] == True:
        db_response, schema = query_database(query['question'])
    else:
        db_response = '[]'
        schema      = '不使用知识图谱回答问题'

    return find_answer(
        query,
        context={
            'schema'      : schema,
            'db_response' : db_response
        }
    )


if __name__ == '__main__':
    query               = input("> ")
    print(f"query:{query}\n")
    if query['open_graph'] == True:
        db_response, schema = query_database(query['question'])
    else:
        db_response = '[]'
        schema      = '不使用知识图谱回答问题'
    print(db_response, end='\n\n')

    response            = find_answer(
        query,
        context={
            'schema'      : schema,
            'db_response' : db_response
        }
    )
    print(response)