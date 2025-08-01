from openai import AsyncOpenAI

class LLMClient:
    def __init__(self, model: str) -> None:
        self.model: str = model
    
    def chat_completions(self, message:str, temperature: float = None):
        raise NotImplementedError


class OpenAIClient(LLMClient):
    def __init__(self, base_url:str, api_key: str, model:str) -> None:
        super().__init__(model)
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)

    
    async def chat_completions(self, message, temperature: float = None, **kwargs):
        try:
            response = await  self.client.chat.completions.create(
                model=self.model,
                stream=False,
                messages=message,
                temperature=temperature,
                **kwargs
            )
            return response.choices[0].message or "",  response.usage
        except Exception as e:
            print(f"OpenAI API 调用错误: {e}")
            raise
def create_llm_client(config:dict):
    return OpenAIClient(config.get("base_url"),config.get("api_key"), config.get("model"))

