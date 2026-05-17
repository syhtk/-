import re

content = open('review_response_system.py', encoding='utf-8').read()

# Add a RAG mock function and replace the generate logic
rag_mock = '''
    def retrieve_knowledge_base(self, category: str, defects: List[str]) -> str:
        \"\"\"
        通过检索本地知识库(RAG模拟)，获取最新的真实售后SOP
        \"\"\"
        kb = {
            "猫粮": {
                "过敏": "SOP: 建议立即停止喂食并就医，凭宠物医院诊断证明可全额退款，并最高报销300元医药费。严禁在未经核实前主动承诺超额赔偿。",
                "临期": "SOP: 核实生产批次。若保质期不足3个月，按发错货处理，直接补发新日期的同款商品，旧商品无需退回。",
                "包装破损": "SOP: 安抚情绪。补偿无门槛运费券或10元代金券，如影响食用支持仅退款。"
            },
            "衣服": {
                "起球": "SOP: 说明面料特性（含羊毛/棉成分易起球）。可赠送除毛器一个，或支持7天无理由退换货（补偿12元运费券）。",
                "褪色": "SOP: 说明深色衣物首次清洗轻微浮色属正常。如严重掉色，安排顺丰上门取件退回全额退款。"
            }
        }
        
        policies = []
        cat_kb = kb.get(category, {})
        for d in defects:
            for k, v in cat_kb.items():
                if k in d or d in k:
                    policies.append(v)
                    
        if not policies:
            return "SOP: 常规售后流程：核实问题图片 -> 安抚用户 -> 根据实际残损情况给出5-20元补偿或走正常退换货流程。"
            
        return " ".join(policies)

    def generate(self, analysis: AnalysisResult, profile: UserProfile, kg: Dict) -> str:
        \"\"\"
        生成流程入口 (已升级 RAG + Tool Calling)
        \"\"\"
        category_name = kg.get("category", {}).get("name", "商品")

        # 1. RAG 知识检索
        retrieved_sop = self.retrieve_knowledge_base(category_name, analysis.detected_defects)
        solution_info = {"description": retrieved_sop}

        # 2. 构建 Prompt
        prompt = self.construct_prompt(analysis, profile, solution_info, category_name)
        
        # 强制要求 LLM 输出工具调用 JSON
        tool_calling_instruction = "\\n\\n【Agent 行动指令】\\n在回复的末尾，你必须按照以下 JSON 格式输出你要执行的系统操作（即使没有操作也要输出空的大括号）：\\n`json\\n{\\"action\\": \\"issue_coupon\\", \\"amount\\": 数字, \\"reason\\": \\"发券原因\\"} 或者 {\\"action\\": \\"create_return_ticket\\", \\"reason\\": \\"退货原因\\"} 或者 {} \\n`"
        prompt += tool_calling_instruction

        # 3. 调用 LLM
        response = None
        if getattr(self, 'api_key', None):
             response = self.call_real_llm(prompt)

        # 如果没有 key 或调用失败，回退到模拟生成
        if not response:
            response = self.simulate_generation(prompt)
            
        return response
'''

# Find the generate function to replace
replace_pattern = r'    def generate\(self, analysis: AnalysisResult.*?(?=    def call_real_llm)'
new_content = re.sub(replace_pattern, rag_mock, content, flags=re.DOTALL)

open('review_response_system.py', 'w', encoding='utf-8').write(new_content)
