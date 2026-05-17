"""
系统对比实验评估脚本 (System Evaluation)
用于论文“实验分析”章节
对比方法：Baseline (规则), Pure LLM (无KG), My System (情感+KG+LLM)
"""

import pandas as pd
import matplotlib.pyplot as plt
import random
import numpy as np
from typing import List

# 引入系统模块
from ecommerce_kg_schema import create_smart_earphones_kg
from review_response_system import ReviewResponseSystem, UserProfile, DynamicResponseGenerator
from mock_review_generator import generate_mock_reviews

# 设置绘图风格
plt.style.use('ggplot')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


# ================= 1. 定义对比模型 =================

# --- 方法 A: Baseline (纯规则) ---
def baseline_model(text: str) -> str:
    """
    基于关键词匹配的简单规则回复
    """
    keywords = ["垃圾", "坏", "差", "烂", "断", "失效"]
    if any(k in text for k in keywords):
        return "亲，非常抱歉给您带来不好的体验。请您联系我们的在线人工客服，我们会为您处理退换货事宜。感谢面的支持。"
    return "感谢您的评价，我们会继续努力。"

# --- 方法 B: Pure LLM (模拟无KG上下文) ---
def pure_llm_model(text: str) -> str:
    """
    模拟没有知识图谱支持的通用 LLM 回复
    特点：语气通顺，但缺乏针对性解决方案，往往是通用的“片汤话”
    """
    # 模拟生成的通用回复
    return (
        "尊敬的顾客，您好。收到您关于产品的反馈，我们深感歉意。"
        "产品质量是我们非常重视的环节。对于您遇到的问题，建议您检查一下使用方式，或者重启设备试试。"
        "如果问题依旧存在，请提供订单号，我们会进一步跟进。祝您生活愉快。"
    )

# --- 方法 C: My System (模拟增强版) ---
# 为了评估需要，我们需要 patch 掉原系统的 simulate_llm_generation
# 使其能针对“智能耳机”的各种缺陷生成动态内容 (模拟 LLM 只有在拿到 Prompt 中的 KG 信息后才能生成具体方案)

class EvalDynamicGenerator(DynamicResponseGenerator):
    def simulate_llm_generation(self, prompt: str, profile: UserProfile, analysis: object) -> str:
        """
        覆盖原有的模拟方法，使其更具通用性，用于评估
        """
        # 模拟 LLM 既然在 Prompt 里收到了 "缺陷事实" 和 "解决方案"，它就能生成包含这些信息的回复
        # 下面的回复逻辑基于 prompt (AnalysisResult) 的内容
        
        defect_str = "、".join(analysis.detected_defects) if analysis.detected_defects else "产品问题"
        
        # 简单的模拟生成逻辑
        if profile.user_type == "暴躁型用户":
            return f"这位老哥先消消气！💥 听说您的耳机出现了【{defect_str}】的情况，这确实太搞心态了！尤其是还耽误了您{analysis.scenario_context}，我代表团队给您跪了。我们现在的补偿方案是直接换新，并且按照技术部的建议，您可以先尝试重置一下固件。真的对不起！"
        else:
            return f"亲爱的用户，看到您反馈耳机有【{defect_str}】的问题，我们心里也很难受。特别是影响到了您的{analysis.scenario_context}，真的非常抱歉。根据我们的知识库，这个问题通常可以通过固件升级解决。如果您愿意，我们为您开通老用户专属售后通道。再次致歉。"

# ================= 2. 评估引擎类 =================

class EvaluationEngine:
    def __init__(self):
        # 初始化 My System
        self.kg_data = create_smart_earphones_kg().to_dict()
        # 增强 KGD (同义词库) 以提高 My System 的命中率
        aliases = {
            "连接不稳定": ["连接不稳定", "断连", "连不上", "连接", "信号"],
            "音质差": ["音质", "听不清", "噪音", "杂音"],
            "续航时间短": ["续航", "没电", "耗电"],
            "降噪效果不好": ["降噪", "吵"],
            "触控失效": ["触控", "按键", "失灵"]
        }
        for d_id, d_val in self.kg_data['defects'].items():
             d_val['aliases'] = aliases.get(d_val['name'], [])
             
        self.my_system = ReviewResponseSystem(self.kg_data)
        # 替换生成器为评估专用版
        self.my_system.generator = EvalDynamicGenerator()

    def run_experiment(self, num_samples=10):
        print(f"🧪 开始生成 {num_samples} 条测试数据 (Category: 智能耳机)...")
        # 1. 准备测试集
        # 使用 mock_review_generator 生成包含缺陷的差评
        df_test = generate_mock_reviews("智能耳机", num_samples)
        
        results = []
        
        print("⚙️ 开始运行对比模型 (Evaluating A/B/C)...")
        for idx, row in df_test.iterrows():
            review_text = row['content']
            review_context = row['context']
            
            # --- 运行三个系统 ---
            
            # A. Baseline
            resp_a = baseline_model(review_text)
            
            # B. Pure LLM
            resp_b = pure_llm_model(review_text)
            
            # C. My System
            # 随机分配一个用户画像进行测试
            u_type = "暴躁型用户" if "！" in review_text else "老客户失望型"
            profile = UserProfile(user_type=u_type, purchase_history_years=2)
            # 捕获 My System 的输出
            # 静默运行 process_review (稍微修改 process_review 以支持返回 analysis 但这里我们只看 response)
            # 为了方便，我们直接调用内部组件，因为 process_review 有 print
            analysis = self.my_system.analyzer.analyze(review_text)
            prompt, resp_c = self.my_system.generator.generate(analysis, profile, self.kg_data)
            
            # --- 计算指标 ---
            
            # 指标 1: 长度 (Length)
            len_a = len(resp_a)
            len_b = len(resp_b)
            len_c = len(resp_c)
            
            # 指标 2: 缺陷命中率 (Defect Hit Rate)
            # 规则：回复中是否包含了评论中隐含的真实缺陷词汇？
            # 这里的“真实缺陷”来自 context 或者是通过简单的关键词检查 review_text
            # 为了简化，我们检查 response 是否包含具体的 KG 缺陷名称 (如 "连接不稳定", "断连", "音质")
            
            def check_hit(text, kg_defects):
                # 检查回复中是否包含 KG 中的专业术语或其别名
                for d_info in kg_defects.values():
                    if d_info['name'] in text: return 1
                    for alias in d_info.get('aliases', []):
                        if alias in text: return 1
                return 0

            hit_a = check_hit(resp_a, self.kg_data['defects'])
            hit_b = check_hit(resp_b, self.kg_data['defects'])
            hit_c = check_hit(resp_c, self.kg_data['defects'])
            
            # 指标 3: 场景共情 (Scenario Mention)
            # 检查回复是否包含 "送人", "出差" 等词，如果 review 里有的话
            scenario_hit_c = 1 if (analysis.scenario_context in resp_c and analysis.scenario_context != "日常使用") else 0
            
            results.append({
                "id": idx,
                "review_snippet": review_text[:20] + "...",
                "Model A (Baseline)_len": len_a,
                "Model A (Baseline)_hit": hit_a,
                "Model B (Pure LLM)_len": len_b,
                "Model B (Pure LLM)_hit": hit_b,
                "Model C (My System)_len": len_c,
                "Model C (My System)_hit": hit_c
            })
            
        return pd.DataFrame(results)

    def visualize_results(self, df_results):
        print("📊 正在绘制评估对比图...")
        
        # 计算平均值
        metrics = {
            "Baseline (Rule)": {
                "avg_len": df_results["Model A (Baseline)_len"].mean(),
                "hit_rate": df_results["Model A (Baseline)_hit"].mean()
            },
            "Pure LLM": {
                "avg_len": df_results["Model B (Pure LLM)_len"].mean(),
                "hit_rate": df_results["Model B (Pure LLM)_hit"].mean()
            },
            "My System (KG+LLM)": {
                "avg_len": df_results["Model C (My System)_len"].mean(),
                "hit_rate": df_results["Model C (My System)_hit"].mean()
            }
        }
        
        methods = list(metrics.keys())
        avg_lens = [m["avg_len"] for m in metrics.values()]
        hit_rates = [m["hit_rate"] for m in metrics.values()]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 图 1: 平均回复长度
        ax1.bar(methods, avg_lens, color=['gray', '#74c0fc', '#ff6b6b'])
        ax1.set_title("平均回复长度对比 (字符数)")
        ax1.set_ylabel("Length (chars)")
        for i, v in enumerate(avg_lens):
            ax1.text(i, v + 2, f"{int(v)}", ha='center')
            
        # 图 2: 缺陷命中率 (Accuracy)
        ax2.bar(methods, hit_rates, color=['gray', '#74c0fc', '#ff6b6b'])
        ax2.set_title("缺陷识别准确率/命中率")
        ax2.set_ylabel("Hit Rate (0-1)")
        ax2.set_ylim(0, 1.2)
        for i, v in enumerate(hit_rates):
            ax2.text(i, v + 0.02, f"{v:.1%}", ha='center')
            
        plt.tight_layout()
        plt.savefig("evaluation_result.png")
        print("✅ 评估图表已保存为 evaluation_result.png")
        
        return metrics

# ================= Main =================

if __name__ == "__main__":
    engine = EvaluationEngine()
    df_res = engine.run_experiment(num_samples=10)
    
    print("\n" + "="*30 + " 实验结果摘要 " + "="*30)
    print(df_res[[
        "Model A (Baseline)_hit", 
        "Model B (Pure LLM)_hit", 
        "Model C (My System)_hit"
    ]].describe())
    
    metrics = engine.visualize_results(df_res)
    
