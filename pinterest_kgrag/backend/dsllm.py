from typing import Optional, List, Dict, Any
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks import CallbackManagerForLLMRun
import requests
import json

class DeepSeekLLM(LLM):
    api_key: str
    # model_name: str = "Qwen/Qwen2.5-VL-32B-Instruct"
    # model_name: str = "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B" # 垃圾模型
    model_name: str = "Qwen/Qwen3-8B"
    api_base: str = "https://api.siliconflow.cn/v1/chat/completions"
    temperature: float = 0.7
    
    @property
    def _llm_type(self) -> str:
        return "deepseek"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.api_base}",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()  # 检查HTTP错误
            result = response.json()
            
            # 调试：打印完整API响应
            print(f"DeepSeek API Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 兼容不同可能的响应结构
            if "choices" in result:
                return result["choices"][0]["message"]["content"]
            elif "output" in result:
                return result["output"]
            else:
                raise ValueError(f"未知API响应格式: {result}")
                
        except Exception as e:
            error_msg = f"DeepSeek API调用失败: {str(e)}"
            print(error_msg)
            return error_msg  # 返回错误信息避免崩溃