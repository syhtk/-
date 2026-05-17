"""
基于 LLM 的通用电商评论数据生成器 (模拟版)
LLM-based Universal E-commerce Comment Data Generator (Simulation)

此脚本模拟了一个基于大语言模型(LLM)的评论生成器。
在实际生产环境中，`_call_llm_api` 函数会连接到 OpenAI/DeepSeek 等 API。
为了演示目的，本脚本内置了针对“洗面奶”和“显卡”的预定义高质量生成模板，
能够生成带情绪、带细节的仿真数据。
"""

import pandas as pd
import random
import uuid
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# ============= 模拟 LLM 行为的生成器类 =============

class LLMReviewGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        # 预定义的用户画像库
        self.user_profiles = [
            {"type": "暴躁老哥", "mood": "Angry", "style": "简短有力，用词激烈，全是感叹号"},
            {"type": "忠实粉", "mood": "Disappointed", "style": "曾经很喜欢，这次很失望，带点惋惜"},
            {"type": "急用党", "mood": "Anxious", "style": "强调时间紧迫，物流或质量耽误了事"},
            {"type": "成分党/技术宅", "mood": "Critical", "style": "分析具体参数、成分，逻辑严密"},
            {"type": "吃瓜群众", "mood": "Neutral/Sarcastic", "style": "阴阳怪气，看热闹不嫌事大"},
            {"type": "敏感肌/小白", "mood": "Sad", "style": "描述具体的身体受损体验，感到委屈"}
        ]
        
        # 预定义的上下文场景库
        self.contexts = [
            "明天要送人，结果包装烂了",
            "用了三天就坏了/过敏了",
            "和宣传完全不符",
            "物流卡了一周才到",
            "客服态度极差，不给退款",
            "刚打开就发现是二手的",
            "价格比别家贵，质量还不行"
        ]

    def _generate_mock_content(self, category: str, profile: Dict, context: str) -> str:
        """
        模拟 LLM 根据 Prompt 生成文本的过程。
        这里使用模板替换技术来模拟 LLM 的输出。
        """
        
        # 针对“洗面奶”的专门生成逻辑
        if category == "洗面奶":
            templates = [
                "{context}！这{category}简直就是工业垃圾！洗完脸烂脸了！避雷避雷！！",
                "一直用你家的{category}，这次真的太失望了。{context}，老粉转黑了，再见。",
                "本来{context}，结果发过来是个漏的！我现在拿什么洗脸？差评！",
                "看成分表本来以为不错，结果{context}。这就是你们所谓的氨基酸{category}？PH值明显偏碱性！",
                "我是大干皮敏感肌，{context}，现在脸上红一大片，又痒又痛，太难受了呜呜呜。"
            ]
            template = random.choice(templates)
            return template.format(category=category, context=context)

        # 针对智能手机
        elif category == "智能手机":
            templates = [
                "{context}。这手机发个微信都烫手卡成PPT，打游戏直接给我满帧掉到个位数！",
                "服了，{context}。屏幕颜色看着极其生硬，而且电池根本撑不到半天就没电了。",
                "刚收到货，{context}。指纹解锁跟瞎了一样死活解不开！",
                "{context}，这是什么诡异的系统BUG？经常莫名其妙重启或者黑屏！",
                "冲着拍照买的，结果{context}。夜景拍出来全是噪点，宣传跟实际严重不符。"
            ]
            template = random.choice(templates)
            return template.format(category=category, context=context)
            
        # 针对女士连衣裙
        elif category == "女装连衣裙":
            templates = [
                "{context}。洗了一次直接缩水成童装，关键还掉色脱色严重，把别的东西都染坏了！",
                "收到货了，{context}。版型特别难看，肩膀那里缝线都裂开了，线头满天飞。",
                "这质量真的绝了！{context}。布料薄得透光，穿上去还特别扎肉，一点都不亲肤。",
                "本来想穿去参加聚会，结果{context}。这裙摆设计真是太雷人了，跟图片完全两码事。",
                "{context}，这是我买过最差的裙子，拉链一拉就卡死，做工极其粗糙。"
            ]
            template = random.choice(templates)
            return template.format(category=category, context=context)

        # 针对零食大礼包
        elif category == "零食大礼包":
            templates = [
                "{context}！里面好几包薯片不仅漏气，而且饼干全碎成了渣，怎么下口啊？",
                "买来给小孩子吃的，结果{context}！仔细一看日期居然是临期产品，太缺德了！",
                "{context}。说是大礼包，其实全是用便宜的难吃的凑数，关键味道还发苦发馊。",
                "这家的零食不敢买了，{context}。巧克力包装被压扁瘪了不说，有一包居然爬出一条虫！！",
                "本来高高兴兴拆快递，{context}。肉脯吃了一口口感特别奇怪像坏了一样。"
            ]
            template = random.choice(templates)
            return template.format(category=category, context=context)

        # 针对智能耳机
        elif category == "智能耳机":
            templates = [
                "{context}，但这智能耳机蓝牙经常断连，听歌一卡一卡的，心态崩了！",
                "用了几天发现续航时间短得离谱，{context}，这也就是听个响？",
                "降噪效果不好，{context}，戴上和没戴一样，电流杂音还很大。",
                "佩戴耳朵痛，{context}，这设计完全不符合人体工学，触控失效更是常有的事。",
                "音质差到爆炸，{context}，简直就是地摊货水平，再也不会买了。"
            ]
            template = random.choice(templates)
            return template.format(category=category, context=context)

        # 通用兜底
        else:
            return f"作为一名{profile['type']}，遇到{context}的情况，我对这个{category}非常不满意，甚至让我感到很{profile['mood']}。"

    def generate_reviews(self, product_category: str, number_of_reviews: int, sentiment: str = "negative") -> pd.DataFrame:
        """
        生成指定数量的模拟评论数据
        
        Args:
            product_category: 品类名称
            number_of_reviews: 生成数量
            sentiment: 情感倾向 (positive/negative/mixed) - 本演示主要侧重差评生成
            
        Returns:
            DataFrame: 包含 user_id, content, rating, user_mood
        """
        data = []
        
        print(f"🤖 正在调用模拟 LLM 生成 {number_of_reviews} 条 '{product_category}' 的评论...")
        
        for _ in range(number_of_reviews):
            # 1. 随机抽取用户画像和上下文
            profile = random.choice(self.user_profiles)
            context = random.choice(self.contexts)
            
            # 2. 生成评论内容 (模拟 LLM 输出)
            content = self._generate_mock_content(product_category, profile, context)
            
            # 3. 确定评分 (根据 sentiment)
            if sentiment == "negative":
                rating = random.randint(1, 2)
            elif sentiment == "positive":
                rating = random.randint(4, 5)
            else:
                rating = random.randint(1, 5)
            
            # 4. 构建数据行
            row = {
                "user_id": f"u_{uuid.uuid4().hex[:8]}",
                "product_category": product_category,
                "user_profile": profile["type"],
                "context": context,
                "content": content,
                "rating": rating,
                "user_mood": profile["mood"],
                "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
            }
            data.append(row)
            
        return pd.DataFrame(data)

# ============= 功能函数封装 =============

def generate_mock_reviews(product_category: str, number_of_reviews: int) -> pd.DataFrame:
    """
    符合用户要求的入口函数
    """
    generator = LLMReviewGenerator()
    # 默认为生成带有具体细节的负面评论，以便于测试“电商评论分析系统”的缺陷识别能力
    return generator.generate_reviews(product_category, number_of_reviews, sentiment="negative")


# ============= 演示代码 =============

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 50)
    
    print("="*60)
    print("基于 LLM 的通用电商评论数据生成器 - 演示")
    print("="*60)
    
    # 演示：生成 5 条‘洗面奶’差评
    category = "洗面奶"
    count = 5
    
    df_reviews = generate_mock_reviews(category, count)
    
    print(f"\n✅ 生成完成！以下是 {category} 的 {count} 条模拟差评数据：\n")
    print(df_reviews[["user_id", "user_profile", "user_mood", "rating", "content"]])
    
    print("\n" + "="*60)
    print("数据多样性验证 (Context & Profile)")
    print("="*60)
    for index, row in df_reviews.iterrows():
        print(f"\n[评论 {index+1}]")
        print(f"用户画像: {row['user_profile']} ({row['user_mood']})")
        print(f"场景背景: {row['context']}")
        print(f"评论内容: {row['content']}")

    # 简要演示另一种品类，证明通用性
    print("\n" + "="*60)
    print("通用性验证 - 显卡")
    print("="*60)
    df_gpu = generate_mock_reviews("显卡", 2)
    print(df_gpu[["user_profile", "content"]])
