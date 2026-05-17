import json
import time
import os
import pandas as pd
from typing import List, Dict
from openai import OpenAI

# ================= 配置区 =================
# 配置您的 DeepSeek 或者 OpenAI API
API_KEY = "sk-248e2f2317bb4311ab359d893366d312"  # 替换为您的真实API Key
BASE_URL = "https://api.deepseek.com" # 以 DeepSeek 为例
MODEL_NAME = "deepseek-chat"

# 输入和输出路径
INPUT_CSV = "raw_comments.csv"  # 新增：从 CSV 文件读取数据
OUTPUT_JSONL = "qwen_finetune_dataset.jsonl"

# 固定的微调指令 (Instruction)
SYSTEM_INSTRUCTION = "作为电商评论分析专家，请抽取以下评论中的核心属性：情绪(emotion)、意图(intent)、缺陷实体(entities/defects)和场景(scenario)，并以严格的JSON格式输出。"

MAX_RETRIES = 3
# ==========================================

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def get_teacher_annotation(review_text: str) -> str:
    """
    使用大模型（Teacher）对数据进行打标
    """
    prompt = f"""
请分析以下电商评论，并严格按照 JSON 格式输出抽取结果。
要求字段如下：
- emotion: 情绪分类标签（枚举：Angry, Disappointed, Rational, Satisfied, Neutral）
- intent: 用户的诉求意图（枚举：Complaint(抱怨/投诉), Refund(要求退款/退货), Consult(咨询), Praise(表扬), Suggestion(建议), None(无明确诉求)）
- entities: 评论中提到的具体产品组件或实体名称（如：包装，屏幕，面料，蓝牙），若无则为 []
- defects: 评论中描述的具体缺陷（如：破损，碎裂，掉色，断连），若无则为 []
- scenario: 购买或使用场景（如：送礼，日常，出差），若无则为 "无"

评论内容：“{review_text}”

只输出合法的 JSON 字符串，不要包含任何 markdown 符号（如 ```json）或额外的解释文本。
"""
    
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "你是一个严谨的数据标注机器，只输出JSON。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1, # 低温度保证稳定性
            )
            # 清理可能的 markdown 标记
            result = response.choices[0].message.content.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            
            # 验证 JSON
            json.loads(result) 
            return result.strip()
        
        except Exception as e:
            print(f"[警告] 处理评论 '{review_text}' 时出错 ({attempt+1}/{MAX_RETRIES}): {e}")
            time.sleep(2)  # 防封禁缓冲

    return None

def build_dataset():
    print(f"🚀 开始使用 {MODEL_NAME} 进行蒸馏打标...")
    valid_count = 0
    
    # 模拟从 CSV/DB 里读取海量数据
    try:
        df = pd.read_csv(INPUT_CSV)
        # 提取 "content" 这一列作为要打标的评论
        raw_reviews = df["content"].tolist()
        print(f"已成功加载 {len(raw_reviews)} 条原始电商评论数据！")
    except Exception as e:
        print(f"读取CSV出错：{e}。请确保存在 {INPUT_CSV} 文件！")
        return
    
    with open(OUTPUT_JSONL, 'w', encoding='utf-8') as f:
        for idx, review in enumerate(raw_reviews):
            print(f"\n正在处理 [{idx+1}/{len(raw_reviews)}]: {review}")
            
            annotation_json_str = get_teacher_annotation(review)
            
            if annotation_json_str:
                # 组装符合 LLaMA-Factory / Qwen 微调要求的 JSONL 格式
                dataset_item = {
                    "instruction": SYSTEM_INSTRUCTION,
                    "input": review,
                    "output": annotation_json_str
                }
                
                # 写入 JSONL (单行呈现)
                f.write(json.dumps(dataset_item, ensure_ascii=False) + "\n")
                valid_count += 1
            
            # API 频率限制缓冲 (可选)
            time.sleep(0.5)

    print(f"✅ 打标完成！成功生成 {valid_count} 条微调数据，保存至 {OUTPUT_JSONL}")

if __name__ == "__main__":
    # 如果没有填入真实的 API Key，可以在此处加一层拦截，防止直接运行报错
    if API_KEY == "your_api_key_here":
        print("💡 请先在脚本顶部配置您的 API_KEY")
    else:
        build_dataset()

