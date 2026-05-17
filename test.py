from llm_service import LLMService
llm = LLMService()
import logging
logging.basicConfig(level=logging.DEBUG)
print(llm.client.chat.completions.create(model=llm.model, messages=[{'role': 'user', 'content': 'test'}]))
