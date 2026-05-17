"""
智能客服回复生成系统 (ReviewResponseSystem)
包含：
1. 缺陷与情绪识别模块 (Analyzer)
2. 动态回复生成模块 (Dynamic Generator)
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import re
import random

# 引入之前的 KnowledgeGraphSchema 类定义
try:
    from graph_engine import KnowledgeGraphEngine
except ImportError:
    KnowledgeGraphEngine = None

try:
    from llm_service import LLMService
except ImportError:
    LLMService = None

@dataclass
class AnalysisResult:
    detected_defects: List[str]  # 识别出的缺陷ID或名称
    user_emotion: str            # 识别出的情绪 (Angry, Disappointed, Rational, etc.)
    scenario_context: str        # 提取的场景关键词 (送礼, 出差, 考试)
    severity: str                # 严重程度

@dataclass
class UserProfile:
    user_type: str               # 用户类型 (暴躁型, 老客户, 理性型)
    purchase_history_years: int  # 客户年限

class ReviewAnalyzer:
    """
    模块 1：缺陷与情绪识别 (Analyzer)
    """
    def __init__(self, knowledge_graph: Dict, llm_service=None):
        self.kg = knowledge_graph
        self.llm = llm_service

    def analyze(self, comment_text: str) -> AnalysisResult:
        """
        分析评论文本，结合大语言模型结构化抽取及词典匹配提取关键信息
        """
        category_name = self.kg.get("category", {}).get("name", "商品")

        # 【核心升级】1. 尝试使用真正的 LLM 进行信息抽取 (代替传统的 if-else 规则)
        if self.llm and self.llm.is_active():
            print("   [LLM 引擎] 启动大模型进行 NER 及结构化信息抽取...")
            
            # 提取图谱中的标准缺陷名称，提供给 LLM 参考
            allowed_defects = [info["name"] for info in self.kg.get("defects", {}).values()]
            extracted = self.llm.extract_information(comment_text, category_name, allowed_defects)
            
            if extracted:
                return AnalysisResult(
                    detected_defects=extracted.get("detected_defects", []),
                    user_emotion=extracted.get("user_emotion", "Neutral"),
                    scenario_context=extracted.get("scenario_context", "日常使用"),
                    severity=extracted.get("severity", "medium")
                )
            print("   [LLM 引擎] 抽取失败，降级使用词典基线提取。")

        # 【备用方案】2. 本地知识图谱词性匹配及硬编码规则降级 (原来的模拟方式)
        detected_defects = []
        severity = "low"
        
        # 假设 self.kg 是之前 schema 的字典格式
        defects_map = self.kg.get("defects", {})
        
        for defect_id, defect_info in defects_map.items():
            if defect_info["name"] in comment_text or \
               any(keyword in comment_text for keyword in defect_info.get("aliases", [])):
                detected_defects.append(defect_info["name"])
                # 取最严重的等级
                if defect_info["severity"] == "critical":
                    severity = "critical"
                elif defect_info["severity"] == "high" and severity != "critical":
                    severity = "high"

        # 2. 情绪识别 (简单关键词规则模拟 NLP 模型)
        emotion = "Neutral"
        if any(w in comment_text for w in ["垃圾", "滚", "气死", "脑残", "只有一次", "甚至", "简直"]):
            emotion = "Angry"
        elif any(w in comment_text for w in ["失望", "老粉", "再也不", "叹气", "可惜"]):
            emotion = "Disappointed"
        elif any(w in comment_text for w in ["分析", "参数", "对比", "虽然", "但是"]):
            emotion = "Rational"
            
        # 3. 场景提取 (由规则模拟 NER 实体识别)
        scenario = "无"
        if any(w in comment_text for w in ["送人", "女朋友", "男朋友", "送长辈", "礼物", "生日"]):
            scenario = "送礼"
        elif any(w in comment_text for w in ["出差", "旅行", "飞机", "高铁"]):
            scenario = "差旅"
        elif any(w in comment_text for w in ["跑步", "健身", "锻炼", "运动"]):
            scenario = "运动"
        elif any(w in comment_text for w in ["上班", "通勤", "地铁", "公交"]):
            scenario = "通勤"
            
        return AnalysisResult(
            detected_defects=detected_defects,
            user_emotion=emotion,
            scenario_context=scenario,
            severity=severity
        )


class DynamicResponseGenerator:
    """
    模块 2：动态回复生成 (Dynamic Generator)
    """

    def __init__(self, llm_service=None):
        self.llm = llm_service

    def construct_prompt(self, analysis: AnalysisResult, profile: UserProfile, solution_info: Dict, category_name: str) -> str:
        """
        构建高级 Prompt 模板
        """
        prompt_template = f"""
[系统指令]
你是一个高级电商客服专家，负责 [{category_name}] 品类的售后。请根据以下信息生成一条回复。
要求：
1. 语气(Tone)调整：针对{profile.user_type}用户，必须采用符合其心理预期的语调。
2. 场景共情：如果提到特定场景(非"无")，必须针对该场景共情和致歉；如果为"无"则不提场景。
3. 解决方案：用通俗易懂的语言解释解决方案。

[输入数据]
- 产品品类: {category_name}
- 缺陷事实: 用户遇到了 {analysis.detected_defects} 问题 (严重程度: {analysis.severity})。
- 用户情绪: {analysis.user_emotion}。
- 用户画像: {profile.user_type} (老客年限: {profile.purchase_history_years}年)。
- 场景细节: {analysis.scenario_context}。
- 标准方案: {solution_info.get('description', '联系客服')}。

[生成策略]
- 如果是暴躁用户 -> 先高强度道歉，直接给赔偿，不要解释太多原理。
- 如果是老客户 -> 强调对其忠诚度的感激，表达愧疚，提供专属补偿。
- 如果是场景破坏(如送礼) -> 必须针对搞砸的场景单独致歉。

[回复内容生成]
"""
        return prompt_template.strip()

    def simulate_llm_generation(self, prompt: str, profile: UserProfile, analysis: AnalysisResult, category_name: str) -> str:
        """
        模拟 LLM 根据 Prompt 生成回复 (通用版，适配所有品类)
        """
        defects_str = "、".join(analysis.detected_defects) if analysis.detected_defects else "体验不佳"
        
        scenario_str = f"提到{analysis.scenario_context}" if analysis.scenario_context and analysis.scenario_context not in ["无", "日常使用"] else "遇到这个问题"
        scenario_str2 = f"在{analysis.scenario_context}时" if analysis.scenario_context and analysis.scenario_context not in ["无", "日常使用"] else "在使用时"
        
        # 1. 暴躁型用户 (Angry)
        if "暴躁" in profile.user_type:
            return (
                f"【模拟回复 - 暴躁型 - {category_name}版】\n"
                f"这位朋友先消消气！💥 收到这样的{category_name}换谁都得炸，真的是太对不起了！\n"
                f"特别是看到您的评论{scenario_str}，这简直是我们的重大失职，把您的安排都搞砸了！😭\n"
                f"关于您反馈的【{defects_str}】问题，技术部门已经介入调查。我不跟您解释什么借口，这就是我们品控不到位！\n"
                "咱们直接处理：我这边刚给您申请了【极速全额退款】，钱马上到账！\n"
                f"另外，为了表达歉意，我私人申请了一份【{category_name}专属赔偿礼包】(含无门槛券)，求您给个补救的机会！🙏"
            )

        # 2. 老客户失望型 (Disappointed)
        elif "老客户" in profile.user_type:
            intro = f"亲爱的老朋友，看到您的评论我心里真的咯噔一下...💔\n关注了我们 {profile.purchase_history_years} 年，"
            return intro + (
                f"却{scenario_str2}遇到【{defects_str}】问题，让您失望了，我真的非常愧疚。\n"
                f"这批次{category_name}虽然经过了多轮测试，但看来在特定环境下还是有瑕疵。\n"
                "您是我们的至尊老粉，这种体验绝不能容忍。我已经为您开启了【老客专属绿色通道】。\n"
                f"除了现有的问题商品我们安排顺丰上门收回外，我也为您准备了最新款的{category_name}作为置换(附带我的手写致歉信)。\n"
                "希望您能再给我们一次机会，守护好您的这份喜爱。"
            )

        # 3. 理性型/标准型 (Rational)
        elif "理性" in profile.user_type or "标准" in profile.user_type:
             return (
                f"【模拟回复 - 理性/标准型 - {category_name}版】\n"
                f"尊敬的用户，您好。非常抱歉给您带来了不好的体验。\n"
                f"关于您反馈的{category_name}【{defects_str}】问题，我们已记录并反馈给产品/品控部门。\n"
                f"针对您提到的{analysis.scenario_context}情况，根据我们的售后政策，建议方案是：\n"
                "1. 请查看私信，我们已为您发送了自助售后/换货链接。\n"
                f"2. 根据知识库显示，对于{defects_str}的情况，通常可以通过我们的标准流程快速解决。\n"
                "如果您需要进一步协助，请随时联系我们。感谢您的客观反馈，这能帮助我们做得更好。"
             )

        return "感谢您的反馈，我们会尽快处理。"

    def generate(self, analysis: AnalysisResult, profile: UserProfile, kg: Dict, comment_text: str = '') -> tuple:
        category_name = kg.get("category", {}).get("name", "商品")
        solution_info = {"description": "联系人工客服处理"}
        if KnowledgeGraphEngine and analysis.detected_defects:
            engine = KnowledgeGraphEngine(kg)
            for defect in analysis.detected_defects:
                graph_sol = engine.infer_solution_for_defect(defect)
                if graph_sol:
                    solution_info["description"] = f"【图谱系统指令下发】针对[{defect}]，启动SOP: {graph_sol['description']}。执行步骤: {' -> '.join(graph_sol['steps'])}。"
                    break
        prompt = self.construct_prompt(analysis, profile, solution_info, category_name)
        
        if self.llm and self.llm.is_active():
            return prompt, self.llm.generate_response(prompt, comment_text)
            
        return prompt, "【配置错误】大模型服务未激活"



class ReviewResponseSystem:
    def __init__(self, kg: Dict, use_real_llm: bool = False, api_key: Optional[str] = None, base_url: Optional[str] = None, model: str = ""):
        self.kg = kg
        self.llm_service = None
        if use_real_llm and LLMService:
            self.llm_service = LLMService(api_key=api_key, base_url=base_url, model=model)
            
        self.analyzer = ReviewAnalyzer(kg, llm_service=self.llm_service)
        self.generator = DynamicResponseGenerator(llm_service=self.llm_service)

    def process_review(self, comment_text: str, profile: UserProfile) -> tuple:
        analysis_result = self.analyzer.analyze(comment_text)
        prompt, final_response = self.generator.generate(analysis_result, profile, self.kg, comment_text=comment_text)
        return analysis_result, prompt, final_response
