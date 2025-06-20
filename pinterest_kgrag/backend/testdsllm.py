import requests

url = "https://api.siliconflow.cn/v1/chat/completions"

payload = {
    "model": "deepseek-ai/DeepSeek-R1",
    "messages": [
        {
            "role": "user",
            "content": "用一段话简述2025年中国大模型行业的机遇与挑战。"
        }
    ],
    "tools": []
}
headers = {
    "Authorization": "Bearer your-api-token",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.json()["choices"][0]["message"]["content"])
