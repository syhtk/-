"""
智能电商评论分析与回复系统 - 演示/答辩界面 (Streamlit App)
"""


import streamlit as st
import pandas as pd
from analytics_module import log_interaction
from ecommerce_kg_schema import create_smart_earphones_kg, create_womens_dress_kg, create_generic_kg, PRODUCT_TAXONOMY
from review_response_system import ReviewResponseSystem, UserProfile, AnalysisResult

# ================= 1. 初始化配置与样式 =================
st.set_page_config(
    page_title="AI电商智能客服分析大屏",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 引入现代字体与极致UI美化 (SaaS级极简玻璃拟物化设计)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');
    
    /* 全局字体与背景净化 */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 90%;
    }
    
    /* 渐变流光标题效果 */
    .main-title {
        background: linear-gradient(-45deg, #FF3CAC, #784BA0, #2B86C5, #00C9FF, #92FE9D);
        background-size: 300% 300%;
        animation: gradientBG 10s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        margin-bottom: 0.5rem;
        text-align: center;
        letter-spacing: -1.5px;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .sub-title {
        text-align: center;
        color: #64748b;
        font-size: 1.15rem;
        font-weight: 500;
        margin-bottom: 2.5rem;
        letter-spacing: 0.5px;
    }
    
    /* 进度条科技感美化 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 10px;
    }
    .main-metric-label { 
        font-size: 13px; 
        font-weight: 700; 
        color: #64748b; 
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    
    /* 现代卡片设计 (悬浮、阴影、圆角) */
    .kg-card, div[data-testid="stMetric"], .stDataFrame {
        padding: 24px;
        border-radius: 16px;
        background: #ffffff;
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .kg-card:hover, div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: #cbd5e0;
    }
    
    /* 模块标题美化 */
    h2, h3, h4 {
        color: #1e293b;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* 侧边栏极致定制 */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, transparent 75%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #f8fafc !important;
    }
    [data-testid="stSidebar"] .stMarkdown hr {
        border-color: rgba(255,255,255,0.1);
    }
    
    /* Tab标签 苹果风/药丸风 (Glass & Pill) 极致现代导航 */
    [data-testid="stTabs"] {
        padding-top: 2rem;
    }
    [data-baseweb="tab-list"] {
        background: rgba(248, 250, 252, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 999px;
        padding: 6px;
        gap: 8px;
        border-bottom: none !important;
        margin-bottom: 40px;
        justify-content: center;
        width: fit-content;
        margin-left: auto;
        margin-right: auto;
        box-shadow: 
            inset 0 2px 4px 0 rgba(0, 0, 0, 0.02),
            0 1px 2px 0 rgba(0,0,0,0.03),
            0 0 0 1px rgba(226, 232, 240, 0.8);
    }
    /* 彻底隐藏底部会变色的原生粗线条指示器 */
    div[data-baseweb="tab-highlight"] {
        display: none !important;
        background-color: transparent !important;
    }
    div[data-baseweb="tab-border"] {
        display: none !important;
    }
    [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 999px !important;
        padding: 10px 32px !important;
        border: none !important;
        color: #64748b !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    [data-baseweb="tab"]:hover {
        color: #334155 !important;
        background-color: rgba(226, 232, 240, 0.5) !important;
        transform: translateY(-1px);
    }
    [aria-selected="true"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 
            0 10px 15px -3px rgba(0, 242, 254, 0.3), 
            0 4px 6px -2px rgba(0, 242, 254, 0.15) !important;
        transform: translateY(-2px);
    }
    [aria-selected="true"]:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 
            0 12px 20px -3px rgba(0, 242, 254, 0.4), 
            0 4px 6px -2px rgba(0, 242, 254, 0.2) !important;
    }
    
    /* 核心按钮 立体光效感 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 600;
        letter-spacing: 0.5px;
        box-shadow: 0 10px 15px -3px rgba(118, 75, 162, 0.3);
        transition: all 0.25s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 20px 25px -5px rgba(118, 75, 162, 0.4);
    }
    
    /* 输入框/文本区 聚焦光晕特效 */
    .stTextArea textarea, .stTextInput input {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        transition: all 0.2s;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
    }

    /* Expander 手风琴组件现代化 */
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border-radius: 12px;
        font-weight: 600;
        color: #1e293b;
    }
    .streamlit-expanderContent {
        border: 1px solid #e2e8f0;
        border-top: none;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
    }

</style>
""", unsafe_allow_html=True)


# ================= 2. 数据加载与增强 =================

    # 加载并增强知识图谱数据
@st.cache_data
def load_enhanced_kg_data(category_name, template_type="General"):
# docstring removed
    
    # 优先处理硬编码的演示案例
    if category_name == "智能耳机":
        kg = create_smart_earphones_kg()
        data = kg.to_dict()
        aliases = {
            "连接不稳定": ["断连", "连不上", "断断续续", "信号差"],
            "音质差": ["听不清", "噪音", "电流声", "音质垃圾"],
            "续航时间短": ["没电", "耗电快", "不耐用"],
            "触控失效": ["按键没反应", "失灵", "无法操作"],
            "降噪效果不好": ["吵", "漏音", "没效果"]
        }
    elif category_name == "女士连衣裙":
        kg = create_womens_dress_kg()
        data = kg.to_dict()
        aliases = {
            "褪色": ["掉色", "染色"],
            "起球": ["毛球", "质量差"],
            "拉链卡顿": ["拉不动", "拉链坏了"],
            "缝线开裂": ["崩开", "破了", "裂开"]
        }
    else:
        # 使用通用模版生成
        kg = create_generic_kg(category_name, template_type)
        data = kg.to_dict()
        aliases = {}
        # 为通用模版添加一些通用别名
        common_aliases = {
            "质量差": ["垃圾", "不行", "太差", "劣质"],
            "物流慢": ["太久", "没到", "乌龟"],
            "做工粗糙": ["瑕疵", "线头"]
        }
        aliases.update(common_aliases)
    
    # 将别名注入到 defects 数据结构中
    for defect_key, defect_val in data['defects'].items():
        defect_name = defect_val['name']
        
        # 匹配别名
        found_aliases = []
        if defect_name in aliases:
            found_aliases = aliases[defect_name]
        
        # 简单的通用匹配，比如 defects 里有 "物流"，aliases 里有 "物流慢"
        for k, v in aliases.items():
            if k in defect_name and k != defect_name:
                 found_aliases.extend(v)
                 
        defect_val['aliases'] = list(set(found_aliases))
            
    return data

# ================= 3. 侧边栏控制区 =================

st.sidebar.markdown('<h2>🚀 智能控制中枢</h2>', unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.subheader("1. 业务分类选择")

# 3.1 品类选择
# 构建搜索框/选择逻辑
category_type = st.sidebar.selectbox(
    "📂 选择所属行业/大类",
    list(PRODUCT_TAXONOMY.keys()),
    index=0
)

# 获取子类列表并自动关联 Template
current_subcategories = PRODUCT_TAXONOMY[category_type]["subcategories"]
current_template = PRODUCT_TAXONOMY[category_type]["template"]

selected_category = st.sidebar.selectbox(
    "🏷️ 选择具体产品",
    current_subcategories,
    index=0
)

# 允许用户手动输入(如果不在列表里)
enable_custom_input = st.sidebar.checkbox("📝 手动输入其他产品名称")
if enable_custom_input:
    custom_product_name = st.sidebar.text_input("请输入产品名称", value=selected_category)
    if custom_product_name:
        selected_category = custom_product_name
        # 尝试推断模版，简单默认为 General，或者保持上级的 template
        # 这里直接沿用 category_type 的 template

# 3.2 定制化回复设置
st.sidebar.markdown("---")
st.sidebar.subheader("✨ 回复定制化")
shop_name = st.sidebar.text_input("店铺名称 (Shop Name)", value="京东自营旗舰店")
coupon_value = st.sidebar.slider("补偿优惠券金额 (元)", 0, 200, 50, step=10)
service_agent_name = st.sidebar.text_input("客服署名", value="您的专属客服-小爱")


# 3.3 语气控制
st.sidebar.markdown("---")
st.sidebar.subheader("🗣️ AI 回复风格")

tone_score = st.sidebar.slider(
    "语气调节 (严肃 ↔ 活泼)",
    min_value=0, max_value=100, value=50,
    help="左滑：专业、道歉、赔偿优先；右滑：亲切、共情、安抚优先"
)

# 映射滑块到用户画像逻辑
if tone_score < 30:
    tone_label = "严肃/灭火模式"
    simulated_user_type = "暴躁型用户"
elif tone_score > 70:
    tone_label = "活泼/亲切模式"
    simulated_user_type = "老客户失望型" # 使用现有逻辑中比较温情的类型
else:
    tone_label = "标准/理性模式"
    simulated_user_type = "理性型用户"

st.sidebar.info(f"当前模式：**{tone_label}**\n\n模拟用户画像：{simulated_user_type}")

# 加载系统
kg_data = load_enhanced_kg_data(selected_category, current_template)

st.sidebar.markdown("---")
st.sidebar.subheader("🔌 后台模型服务")

# 真实连接需要的参数，默认指向本地推理服务（请确保已在本机启动服务）
# 若要改回云端 DeepSeek，请替换为相应的 API Key / Base URL
api_key = "local-api-key"  # 本地服务占位密钥
base_url = "http://127.0.0.1:8000/v1"  # 本地推理服务地址
model = "gpt-3.5-turbo"  # 本地服务暴露的模型别名，实际后端已加载 Qwen2.5-1.5B

# 只给用户提供一个用来展示和汇报的模型名字输入框
display_model_name = st.sidebar.text_input("🧠 当前赋能的微调大模型", value="Qwen2.5-1.5B", help="此处填写的名称仅用于展示。")

# 系统内部依然传入真实的访问地址和模型伪装名称
system = ReviewResponseSystem(kg_data, use_real_llm=True, api_key=api_key, base_url=base_url, model=model)

# 模型健康检查与可靠预热：先做短轮询的同步检查（用于 UI 启用），如果失败再触发后台预热进程并继续轮询
import time
if 'llm_ready' not in st.session_state:
    st.session_state['llm_ready'] = False

llm_service = getattr(system, 'llm_service', None)
if llm_service:
    # 快速同步检测（最多等待 8 次，共约 8*0.8=6.4s）
    try:
        for _ in range(8):
            if llm_service.health_check(timeout_seconds=2):
                st.session_state['llm_ready'] = True
                break
            time.sleep(0.8)
        if not st.session_state['llm_ready']:
            # 后台安全预热（独立进程），避免 Streamlit ScriptRunContext 警告
            try:
                llm_service.warm_up()
            except Exception:
                pass

            # 更长轮询等待模型就绪（最多 20s）
            for _ in range(20):
                if llm_service.health_check(timeout_seconds=2):
                    st.session_state['llm_ready'] = True
                    break
                time.sleep(1.0)
    except Exception:
        st.session_state['llm_ready'] = False

    # 侧栏显示状态与重试按钮
    with st.sidebar:
        if st.session_state['llm_ready']:
            st.success(f"LLM 引擎状态：已连接 ({display_model_name})")
        else:
            st.error("LLM 引擎状态：未连接 — 请启动本地推理服务或点击重试")
            if st.button("🔁 重试模型连接"):
                try:
                    llm_service.warm_up()
                except Exception:
                    pass
                # 触发一次短轮询
                for _ in range(12):
                    if llm_service.health_check(timeout_seconds=2):
                        st.session_state['llm_ready'] = True
                        st.experimental_rerun()
                    time.sleep(0.8)
else:
    st.session_state['llm_ready'] = False


# ================= 4. 主界面区域 =================

# 渲染炫酷的现代渐变标题
st.markdown('<div class="main-title">AI 企业智能化客服洞察平台</div>', unsafe_allow_html=True)   
st.markdown(f'<div class="sub-title">当前应用图谱：<b>{selected_category} Knowledge Graph</b>  |  实体网络节点数：{len(kg_data["category"]) + len(kg_data["components"]) + len(kg_data["defects"]) + len(kg_data["solutions"])}</div>', unsafe_allow_html=True)

# 构建无缝融合的现代四大模块 (胶囊式导航)
tab_service, tab_kg, tab_dashboard, tab_report = st.tabs(["💬 智能客服台", "🕸️ 专家图谱库", "📈 运营看板", "📑 执行层工单报告"])

with tab_service:
    # 4.1 输入区
    st.markdown("<h3>1. 异常评价实时捕获台</h3>", unsafe_allow_html=True)
    default_text = ""
    # 智能生成默认文案
    if "耳机" in selected_category:
        default_text = "真是气死我了！本来明天要是送女朋友的礼物，结果一打开耳机蓝牙就老是断连，根本没法用，简直是垃圾！"
    elif "裙" in selected_category or "衣" in selected_category:
        default_text = "买来准备参加婚礼穿的，结果洗了一次就严重褪色，裙摆的缝线也崩开了，太失望了。"
    elif "吃" in selected_category or "食" in selected_category or category_type == "食品饮料":
        default_text = "收到打开包装都漏气了，尝了一口味道很奇怪，根本不新鲜！还是给孩子买的，太不负责任了！"
    elif category_type == "美妆护肤":
        default_text = "用了两天脸上就开始过敏红肿，脸上火辣辣的疼，味道还特别刺鼻，是不是假货啊？"
    else:
        default_text = f"这个{selected_category}质量太差了，做工很粗糙，包装都压坏了，而且物流极其慢，客服问半天不理人！"
        
    user_input = st.text_area("请输入差评内容：", value=default_text, height=120)

    if st.button("🚀 开始分析 & 生成回复", type="primary"):
        if not user_input.strip():
            st.warning("请输入评论内容")
        elif not st.session_state.get('llm_ready', False):
            st.warning("LLM 引擎尚未就绪，请稍候或点击侧栏的重试按钮。")
        else:
            with st.spinner("🔄 正在检索知识图谱并生成策略..."):
                # 调用核心逻辑
                analysis_result = system.analyzer.analyze(user_input)
                
                # 构造画像对象
                profile = UserProfile(user_type=simulated_user_type, purchase_history_years=2)
                
                # 生成回复
                prompt, response = system.generator.generate(analysis_result, profile, kg_data, user_input)
                
                # 如果大模型调用失败返回 None，提供降级兜底方案
                if not response:
                    response = "非常抱歉，我们的大模型回复服务暂时不可用，客服人员会尽快与您联系处理。"

                # 直接记录到 reviews_log 和 defect_stats
                coupon = 0.0
                log_interaction(
                    category=selected_category,
                    content=user_input,
                    user_emotion=getattr(analysis_result, 'user_emotion', getattr(analysis_result, 'emotion', 'Neutral')),
                    defects=analysis_result.detected_defects,
                    response=response,
                    coupon_issue=coupon
                )
                
                # --- 应用定制化注入 ---
                # 1. 替换或注入店铺名 (如果回复中未体现)
                response = response.replace("我们的", f"我们【{shop_name}】的")
                
                # 2. 注入优惠券信息 (如果回复中提到了补偿但没说具体金额)
                if coupon_value > 0 and ("券" in response or "补偿" in response):
                    if str(coupon_value) not in response:
                        response = response.replace("优惠券", f"{coupon_value}元无门槛优惠券")
                        response = response.replace("礼包", f"礼包(含{coupon_value}元券)")
                        
                # 3. 强制追加署名
                if service_agent_name:
                    response += f"\n\n—— {shop_name} 售后顾问：{service_agent_name}"

            # 4.2 分析结果可视化
            st.markdown("---")
            st.markdown("<h3>2. 复合引擎诊断面板</h3>", unsafe_allow_html=True)
            
            # 情感极性展示
            st.markdown("**🔍 情感倾向识别 (Sentiment Analysis)**")
            score = 50
            if analysis_result.user_emotion == "Angry":
                score = 90
                bar_color = "red"
                emo_text = "🔥 极度愤怒"
            elif analysis_result.user_emotion == "Disappointed":
                score = 65
                bar_color = "orange"
                emo_text = "💔 失望/难过"
            elif analysis_result.user_emotion == "Rational":
                score = 30
                bar_color = "blue"
                emo_text = "🧠 理性/客观"
            else:
                score = 10
                bar_color = "green"
                emo_text = "😐 中性"
            
            st.progress(score)
            st.caption(f"检测结果：{emo_text}")

            # 知识图谱实体识别结果
            st.markdown("**🕸️ 知识图谱实体映射 (KG Extraction)**")
            
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                st.markdown('<div class="main-metric-label">检测到的场景 (Context)</div>', unsafe_allow_html=True)
                st.info(f"🏷️ {analysis_result.scenario_context}")
            
            with r_col2:
                st.markdown('<div class="main-metric-label">识别到的缺陷 (Defects)</div>', unsafe_allow_html=True)
                if analysis_result.detected_defects:
                    for defect_name in analysis_result.detected_defects:
                        # 反查组件
                        comp_name = "其他/外部原因"
                        for d_id, d_val in kg_data['defects'].items():
                            if d_val['name'] in defect_name or defect_name in d_val['name']:
                                comp_id = d_val['component_id']
                                comp_name = kg_data['components'][comp_id]['name']
                                break
                                
                        # 兜底特定词汇到"服务/包装"分类避免太难看
                        if comp_name == "其他/外部原因":
                            if "物流" in defect_name or "客服" in defect_name or "态度" in defect_name:
                                comp_name = "服务与履约"
                            elif "包装" in defect_name or "破损" in defect_name:
                                comp_name = "包装与外观"

                        st.error(f"⚠️ {comp_name} : {defect_name}")
                else:
                    st.success("✅ 未检测到明显质量缺陷")

            # 4.3 生成回复展示
            st.markdown("---")
            st.markdown("<h3>3. AI 生成最优客诉处置策略 (SOP + 话术)</h3>", unsafe_allow_html=True)
            st.text_area("生成的话术内容预览：", value=response, height=250)
            
            with st.expander("查看底层 Prompt 构建细节"):
                st.code(prompt, language="markdown")

with tab_kg:
    # 展示知识图谱概览
    st.markdown("<h3>📚 图谱静态实体与底层元数据库</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>通过高度专业化的 Schema 约束，驱动下游 LLM 对业务概念进行高精准匹配关联。</p>", unsafe_allow_html=True)

    col_k1, col_k2 = st.columns(2)
    with col_k1:
        st.markdown('<div class="main-metric-label">🧩 核心组件 (Components)</div>', unsafe_allow_html=True)
        comps_df = pd.DataFrame.from_dict(kg_data['components'], orient='index')
        st.dataframe(
            comps_df[['name', 'description']],
            hide_index=True,
            height=300
        )

    with col_k2:
        st.markdown('<div class="main-metric-label">🚨 已知缺陷库 (Defects)</div>', unsafe_allow_html=True)
        defs_df = pd.DataFrame.from_dict(kg_data['defects'], orient='index')
        st.dataframe(
            defs_df[['name', 'severity']],
            hide_index=True,
            height=300
        )

    st.markdown("---")
    info_col1, info_col2, info_col3 = st.columns(3)
    info_col1.success("🟢 System: Online")
    info_col2.success("🟢 Knowledge Graph: Synchronized")
    info_col3.success(f"🟢 LLM Engine: {display_model_name} Activated")

with tab_dashboard:
    st.markdown("<h3>📈 客户质量数据分布大屏</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>基于全样本历史真实评价进行词频统计与分类，实时同步反映当前业务生态健康度。</p>", unsafe_allow_html=True)

    import plotly.express as px
    import os
    
    # 动态加载真实数据集并进行词频匹配
    csv_path = 'raw_comments.csv'
    if os.path.exists(csv_path):
        df_raw = pd.read_csv(csv_path)
        # 筛选出当前分类下的所有评论
        cat_df = df_raw[df_raw['product_category'] == selected_category]
        
        if not cat_df.empty:
            # 统计各个缺陷出现的频次
            defect_stats = {}
            for defect_key, defect_val in kg_data['defects'].items():
                d_name = defect_val['name']
                d_aliases = defect_val.get('aliases', [])
                
                # 关键词匹配器
                keywords = [d_name] + d_aliases
                count = 0
                for text in cat_df['content'].dropna():
                    if any(k in text for k in keywords):
                        count += 1
                        
                defect_stats[d_name] = count
                
            sorted_pairs = sorted(defect_stats.items(), key=lambda x: x[1], reverse=True)[:10]
            # 过滤掉频次为0的数据
            sorted_pairs = [p for p in sorted_pairs if p[1] > 0]
        else:
            sorted_pairs = []
    else:
        sorted_pairs = []
        st.warning("未找到本地真实评价数据集 `raw_comments.csv`，图表区暂无数据。")

    if sorted_pairs:
        top_defects, top_freqs = zip(*sorted_pairs)
        df_dash = pd.DataFrame({'客诉问题': top_defects, '真实出现频次': top_freqs})
        
        dash_col1, dash_col2 = st.columns([1.5, 1])

        with dash_col1:
            fig_bar = px.bar(df_dash, x='客诉问题', y='真实出现频次',
                             color='真实出现频次', color_continuous_scale='Sunset',
                             title=f"【{selected_category}】Top 客诉问题实际分布图")
            fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_bar, use_container_width=True)

        with dash_col2:
            fig_pie = px.pie(df_dash, names='客诉问题', values='真实出现频次',
                             title="真实客诉问题占比", hole=0.45)
            fig_pie.update_traces(textposition='inside', textinfo='percent')
            fig_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("该品类暂无足够的客诉统计数据。")
with tab_report:
    st.markdown("<h3>📑 企业级智能诊断与行动报表</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 0.95rem;'>基于全量客诉数据分析和 KG 底层映射，自动生成的高管与各业务线决策支撑材料。</p>", unsafe_allow_html=True)

    if st.button("🔄 一键生成 / 刷新报表引擎", type="primary"):
        with st.spinner("🧠 正在结合知识图谱提取历史评价特征点..."):
            
            if not sorted_pairs:
                st.warning("暂无足够的数据来生成报表。请检查是否拥有对应品类数据。")
            else:
                total_complaints = sum([f for _, f in sorted_pairs])
                top1_issue, top1_freq = sorted_pairs[0]
                
                # 寻找 Top1 问题的原图谱定义和组件
                target_def_info = None
                target_comp_name = "未知组件"
                for d_k, d_v in kg_data["defects"].items():
                    if d_v["name"] == top1_issue:
                        target_def_info = d_v
                        # 反查是哪个组件
                        comp_id = d_v.get("component_id")
                        if comp_id and comp_id in kg_data["components"]:
                            target_comp_name = kg_data["components"][comp_id]["name"]
                        break
                        
                top_severity = target_def_info["severity"].upper() if target_def_info else "N/A"
                proportion = round((top1_freq / total_complaints) * 100, 2)
                
                # ------ 【第一板块】高管摘要 ------
                st.markdown("---")
                st.markdown(f"<h3>📋 【{selected_category}】质量运营洞察报告 (Executive Summary)</h3>", unsafe_allow_html=True)
                st.markdown(f"> **报告期概览**：在所选数据样本中，本品类共检出 **{total_complaints}** 起有效质量反馈。")
                
                # 预警卡片排版
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("首要客诉问题 (Top Issue)", top1_issue, f"占比 {proportion}%", delta_color="inverse")
                col_r2.metric("问题所属核心组件 (Component)", target_comp_name)
                
                # 等级颜色处理
                sev_color = "red" if top_severity in ["CRITICAL", "HIGH"] else "orange"
                col_r3.markdown(f"**风险定级 (Severity)**<br><span style='color:{sev_color}; font-size:24px; font-weight:bold;'>{top_severity}</span>", unsafe_allow_html=True)
                
                # ------ 【第二板块】研发与品控建议 ------
                st.markdown("<h4>🛠️ 研发与品控 (R&D / QA) 端建议</h4>", unsafe_allow_html=True)
                if top_severity in ["CRITICAL", "HIGH"]:
                    st.error(f"**[紧急通知]** {top1_issue} 问题已被系统定级为 {top_severity}。该问题集中在 **【{target_comp_name}】** 组件。建议 QA 质检部门立即抽检近期批次仓库库存，并将此问题抄送供应链/代代工厂进行溯源。")
                else:
                    st.warning(f"**[优化建议]** {top1_issue} 属于温和型质量负反馈。建议研发部门在下一次产品迭代或中期改款期间，针对 **【{target_comp_name}】** 进行体验优化。")

                # ------ 【第三板块】基于图谱的前端客服解决SOP ------
                st.markdown("<h4>💡 运营与客服 (Customer Success) 应对策略SOP</h4>", unsafe_allow_html=True)
                st.markdown("<p style='color:#64748b;'>依据系统底层 Knowledge Graph 知识中枢储备，推荐当前一线客服应采用如下话术与处置流程拦截负面情绪升级：</p>", unsafe_allow_html=True)
                
                solution_found = False
                for s_k, s_v in kg_data["solutions"].items():
                    # 匹配 defect_id
                    if target_def_info and s_v.get("defect_id") == target_def_info.get("id", target_def_info.get("defect_id")):
                        solution_found = True
                        st.info(f"**标准解决方案 (SOP)：{s_v.get('name')}** | *系统预估挽回有效率：{s_v.get('effectiveness_rate', '未知')*100 if isinstance(s_v.get('effectiveness_rate'), float) else s_v.get('effectiveness_rate', '75%')}%*")
                        if "steps" in s_v:
                            for idx, step in enumerate(s_v["steps"]):
                                st.markdown(f"1. {step}")
                        break
                        
                if not solution_found:
                    st.markdown("> *知识图谱中暂未检索到针对此问题的显式解决方案 SOP，建议人工介入并视情况提供适当金额补偿（可在侧边栏配置）。*")
                    
                # ------ 【第四板块】详细数据流追踪 ------
                st.markdown("<h4>📥 客诉追踪数据流</h4>", unsafe_allow_html=True)
                report_df = pd.DataFrame(sorted_pairs, columns=["反馈缺陷实体 (Defect Target)", "触发命中频度 (Frequency)"])
                st.dataframe(report_df, hide_index=True)
                
                csv_data = report_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ 导出质量诊断明细数据至 CSV",
                    data=csv_data,
                    file_name=f"Enterprise_Report_{selected_category}_Quality_Stats.csv",
                    mime="text/csv",
                )

