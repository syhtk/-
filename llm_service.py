"""
大语言模型服务封装 (LLM Service)
解决系统原有的“规则硬编码(Fake NER)”和“假大模型生成”的技术硬伤。
使用真正的 OpenAI API 进行：
1. 信息抽取 (Information Extraction / NER)
2. 动态回复生成 (Dynamic Generation)
"""

import os
import json
import threading
import time
import requests
import multiprocessing
from collections import OrderedDict
from typing import Dict, Any, List

# 忽略系统代理，防止本地请求 127.0.0.1 被代理软件拦截导致 502 Bad Gateway
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from openai import OpenAI
from pydantic import BaseModel, Field

# 用于 Pydantic 结构化输出保证抽取稳定
class ReviewExtractionOutput(BaseModel):
    detected_defects: List[str] = Field(description="从评论中提取出的产品缺陷名词列表，如['降噪效果差', '断连']")
    user_emotion: str = Field(description="推断的消费者情绪，如'Angry', 'Disappointed', 'Rational'")
    scenario_context: str = Field(description="评论中提到的特定使用场景，如'送礼场景', '通勤场景'，未提及则填'日常使用'")
    severity: str = Field(description="情绪严重程度：'high', 'medium', 'low'")

class LLMService:
    def __init__(self, api_key: str = None, base_url: str = None, model: str = "gpt-4o-mini"):
        # 默认尝试从环境变量拉取 API Key，如果没有则回退到 mock 模式
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model
        self.client = None
        
        if self.base_url:
            # 本地 OpenAI 兼容服务通常不校验 key，但 SDK 仍要求传入一个非空值
            effective_api_key = self.api_key or "local-api-key"
            self.client = OpenAI(api_key=effective_api_key, base_url=self.base_url)
        elif self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        # 简单内存缓存，减少重复相同 prompt 的调用延迟
        self._response_cache = OrderedDict()
        self._cache_max = 128
            
    def is_active(self) -> bool:
        """检查是否配置了真实的大语言模型"""
        return self.client is not None

    def extract_information(self, comment_text: str, category_name: str, allowed_defects: List[str] = None) -> Dict[str, Any]:
        """
        核心升级：使用真实 LLM 进行结构化信息抽取 (NER/IE)
        彻底替换以前的 if-else 关键字匹配。
        """
        if not self.is_active():
            # 回退到模拟逻辑 (在 review_response_system 中处理)
            return None

        # 如果传入了知识图谱中的规范缺陷列表，作为提示词约束大模型
        defect_hint = ""
        if allowed_defects:
            defect_hint = f"\n作为参考，该品类的已知常见缺陷库为：{', '.join(allowed_defects)}。\n请尽量从上述已知缺陷中挑选匹配项。如果是不在列表中的新问题（如包装、物流等），也可自行精简概括。"

        prompt = f"""
你是一个电商数据分析专家。请仔细并【仅根据】给出的买家评论内容，抽取出商品缺陷、用户情绪级别和涉及的使用场景。如果评论中明确提到了场景（比如跑步、通勤、送给长辈等），请提取出来；如果未明确提及任何场景，请务必返回 "无"。{defect_hint}

要求必须返回以下严格的JSON格式（不要输出任何除JSON以外的内容）：
{{
    "detected_defects": ["缺陷1", "缺陷2"],
    "user_emotion": "Angry / Disappointed / Rational 等",
    "scenario_context": "此处填入具体的场景原词或简练概括（如：跑步、通勤、送长辈等，如果没有则填'无'）",
    "severity": "high / medium / low"
}}

评论文本：
"{comment_text}"
"""
        try:
            # 较新的 OpenAI API 可以使用 response_format 要求返回 JSON
            # 但为了兼容本地开源大模型 (例如通过 LLaMA-Factory 部署的), 我们移除强制的 response_format
            # 改为在 Prompt 中强烈要求返回 JSON 并手写解析
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个严谨的信息提取机器人。无论任何情况，请始终仅输出合法的JSON格式字符串，不要输出任何其他多余文本、注释或Markdown标记(如```json)。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            raw_content = response.choices[0].message.content.strip()
            
            # 尝试清理可能携带的 markdown code block 标记
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:]
            if raw_content.startswith("```"):
                raw_content = raw_content[3:]
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3]
                
            return json.loads(raw_content.strip())
        except Exception as e:
            print(f"LLM 抽取失败，将回退降级处理: {e}")
            return None

    def generate_response_stream(self, system_prompt: str, comment_text: str):
        if not self.is_active():
            yield '模型服务未激活'
            return

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"用户评论：\n{comment_text}\n请根据以上评论，按照系统指令生成回复："}
                ],
                temperature=0.7,
                max_tokens=250,
                stream=True
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f'生成失败: {e}'

    def generate_response(self, system_prompt: str, comment_text: str, max_tokens: int = 120) -> str:
        """
        核心升级：使用真实 LLM 进行回复生成，使用系统给出的严格 SOP和图谱逻辑，防止 AI 越狱。
        """
        if not self.is_active():
            return None
        # cache key
        cache_key = (system_prompt, comment_text, max_tokens)
        if cache_key in self._response_cache:
            # move to end
            val = self._response_cache.pop(cache_key)
            self._response_cache[cache_key] = val
            return val

        # 使用简单重试策略以应对短暂的连接错误
        attempts = 3
        delay = 0.8
        for i in range(attempts):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"用户评论：\n{comment_text}\n请根据以上评论，按照系统指令生成回复：\n字数要求：控制在100字以内，简明扼要."}
                    ],
                    temperature=0.7,
                    max_tokens=max_tokens
                )
                result = response.choices[0].message.content
                try:
                    # store in cache
                    self._response_cache[cache_key] = result
                    if len(self._response_cache) > self._cache_max:
                        self._response_cache.popitem(last=False)
                except Exception:
                    pass
                return result
            except Exception as e:
                print(f"LLM 生成失败，尝试重试 {i+1}/{attempts}: {e}")
                time.sleep(delay * (2 ** i))
                last_exc = e
        print(f"LLM 生成失败，将回退降级处理: {last_exc}")
        return None

    def warm_up(self):
        """向模型发送一次轻量级请求以预热模型（异步调用）。"""
        if not self.is_active():
            return
        # 使用独立进程执行预热与健康检查，避免在 Streamlit 的 ScriptRunContext 中产生警告
        def _warm_proc(base_url, model, api_key):
            session = requests.Session()
            session.headers.update({"Content-Type": "application/json"})
            # 如果服务需要 api_key 放入 Authorization（一般本地不需要）
            if api_key:
                session.headers.update({"Authorization": f"Bearer {api_key}"})

            # 先做短轮询的 /v1/models 健康检测
            try:
                for _ in range(8):
                    try:
                        r = session.get(f"{base_url.rstrip('/')}/models", timeout=3)
                        if r.status_code == 200:
                            break
                    except Exception:
                        pass
                    time.sleep(0.8)

                # 尝试一次轻量级的 chat 请求以保证模型加载完成
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "预热检查"},
                        {"role": "user", "content": "你好，预热用短句。"}
                    ],
                    "max_tokens": 16,
                    "temperature": 0.1
                }
                try:
                    session.post(f"{base_url.rstrip('/')}/chat/completions", json=payload, timeout=6)
                except Exception:
                    pass
            except Exception:
                pass

        p = multiprocessing.Process(target=_warm_proc, args=(self.base_url, self.model, self.api_key), daemon=True)
        p.start()

    def health_check(self, timeout_seconds: int = 5) -> bool:
        """使用 HTTP 直接检查本地 OpenAI 兼容服务是否可用。"""
        if not self.base_url:
            return False
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        if self.api_key:
            session.headers.update({"Authorization": f"Bearer {self.api_key}"})

        try:
            r = session.get(f"{self.base_url.rstrip('/')}/models", timeout=timeout_seconds)
            return r.status_code == 200
        except Exception:
            return False
