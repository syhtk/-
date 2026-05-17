import re

with open('review_response_system.py', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('    def construct_prompt(self')
end_idx = text.find('    def simulate_llm_generation')

if start_idx != -1 and end_idx != -1:
    new_prompt = '''    def construct_prompt(self, analysis: AnalysisResult, profile: UserProfile, solution_info: Dict, category_name: str) -> str:
        issue_str = "、".join(analysis.detected_defects) if analysis.detected_defects else "体验不佳"
        loyalty_context = f"老粉丝 ({profile.purchase_history_years}年)" if "老" in profile.user_type else "新客"
        
        prompt = f"""你是一个金牌高级售后主管。你绝对不能像个AI或是死板的客服机器人。
现在的接警信息：
- 商品：{category_name}
- 客人的情况：{loyalty_context} ({profile.user_type}，当时是用于 {analysis.scenario_context})
- 具体的严重问题（不能改口！）：{issue_str}
- 后台指示的退换指令：{solution_info.get('description', '极速处理退换全款')}
- 你的唯一目标：安抚客人情绪 ({analysis.user_emotion})

请你生成一段发给该客人的完整消息（直接开始称呼，不要有任何前言）：
1. 必须切合这个 {category_name} 确实发生 {issue_str} 这个情况，感同身受地表达深切自责。绝对不要用死板的官方套话，要非常人情味。
2. 告诉客人，你已立刻破例为他申请了：{solution_info.get('description', '全额极速退款并让快递马上上门')}。
3. 为了平息他的怨气，并且保住咱们品牌的声誉，你在最后【必须】附送这一句：“为了弥补对您造成的麻烦，我已经给您的账户补发了一张【50元平台无门槛道歉专属券】，恳请您收下。”

【绝不可触碰的高压线，一旦触碰你就会被开除】：
1. 绝对不要自己填模板占位符比如“[具体原因]”或者“[补偿方案]”！你要根据上面的具体问题写出具体文字。
2. 绝对不可让客人去检查设置、提供图片或者联系专员！你已经全权搞定了售后。
3. 绝对不能使用官腔（如“抱歉给您带来不便，敬请谅解”）。"""
        return prompt

'''
    
    text = text[:start_idx] + new_prompt + text[end_idx:]

with open('review_response_system.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("done")
