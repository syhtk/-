"""
电商评论分析系统通用知识图谱 Schema
Universal E-commerce Comment Analysis Knowledge Graph Schema
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field
from enum import Enum


# ============= 节点类定义 (Node Classes) =============

@dataclass
class ProductCategory:
    """
    品类节点：代表商品的一级分类
    """
    category_id: str
    category_name: str
    description: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)
    
    def __repr__(self):
        return f"ProductCategory(id={self.category_id}, name={self.category_name})"


@dataclass
class Component:
    """
    组件节点：该品类的主要组成部分或功能模块
    """
    component_id: str
    component_name: str
    description: Optional[str] = None
    category_id: str = ""  # 所属品类
    properties: Dict[str, str] = field(default_factory=dict)
    
    def __repr__(self):
        return f"Component(id={self.component_id}, name={self.component_name})"


@dataclass
class Defect:
    """
    缺陷节点：该组件可能出现的问题
    """
    defect_id: str
    defect_name: str
    severity: str  # 严重程度：critical, high, medium, low
    description: Optional[str] = None
    component_id: str = ""  # 所属组件
    frequency: Optional[int] = None  # 出现频率/数量
    
    def __repr__(self):
        return f"Defect(id={self.defect_id}, name={self.defect_name}, severity={self.severity})"


@dataclass
class Solution:
    """
    解决方案节点：解决特定缺陷的标准策略
    """
    solution_id: str
    solution_name: str
    description: str
    defect_id: str = ""  # 解决的缺陷
    steps: List[str] = field(default_factory=list)  # 解决步骤
    effectiveness_rate: Optional[float] = None  # 有效率 0-1
    
    def __repr__(self):
        return f"Solution(id={self.solution_id}, name={self.solution_name})"


# ============= 关系类定义 (Relationship Classes) =============

class RelationType(Enum):
    """关系类型枚举"""
    HAS_COMPONENT = "has_component"      # 品类有组件
    HAS_DEFECT = "has_defect"            # 组件有缺陷
    SOLVED_BY = "solved_by"              # 缺陷由方案解决
    RELATED_TO = "related_to"            # 通用关联


@dataclass
class Relationship:
    """
    关系节点：连接两个节点
    """
    source_id: str
    target_id: str
    relation_type: RelationType
    properties: Dict[str, any] = field(default_factory=dict)
    
    def __repr__(self):
        return f"{self.source_id} --[{self.relation_type.value}]--> {self.target_id}"


# ============= 知识图谱 Schema 定义 =============

@dataclass
class KnowledgeGraphSchema:
    """
    通用知识图谱Schema
    存储一个品类的完整知识图谱数据结构
    """
    category: ProductCategory
    components: Dict[str, Component] = field(default_factory=dict)
    defects: Dict[str, Defect] = field(default_factory=dict)
    solutions: Dict[str, Solution] = field(default_factory=dict)
    relationships: List[Relationship] = field(default_factory=list)
    
    def add_component(self, component: Component) -> None:
        """添加组件"""
        component.category_id = self.category.category_id
        self.components[component.component_id] = component
    
    def add_defect(self, defect: Defect, component_id: str) -> None:
        """添加缺陷"""
        defect.component_id = component_id
        self.defects[defect.defect_id] = defect
        # 自动建立关系
        rel = Relationship(
            source_id=component_id,
            target_id=defect.defect_id,
            relation_type=RelationType.HAS_DEFECT
        )
        self.relationships.append(rel)
    
    def add_solution(self, solution: Solution, defect_id: str) -> None:
        """添加解决方案"""
        solution.defect_id = defect_id
        self.solutions[solution.solution_id] = solution
        # 自动建立关系
        rel = Relationship(
            source_id=defect_id,
            target_id=solution.solution_id,
            relation_type=RelationType.SOLVED_BY
        )
        self.relationships.append(rel)
    
    def build_category_component_relation(self) -> None:
        """构建品类-组件的has_component关系"""
        for comp_id in self.components.keys():
            rel = Relationship(
                source_id=self.category.category_id,
                target_id=comp_id,
                relation_type=RelationType.HAS_COMPONENT
            )
            self.relationships.append(rel)
    
    def to_dict(self) -> Dict:
        """将知识图谱转换为字典数据结构"""
        return {
            "category": {
                "id": self.category.category_id,
                "name": self.category.category_name,
                "description": self.category.description,
                "attributes": self.category.attributes
            },
            "components": {
                comp_id: {
                    "id": comp.component_id,
                    "name": comp.component_name,
                    "description": comp.description,
                    "properties": comp.properties
                }
                for comp_id, comp in self.components.items()
            },
            "defects": {
                defect_id: {
                    "id": defect.defect_id,
                    "name": defect.defect_name,
                    "severity": defect.severity,
                    "description": defect.description,
                    "component_id": defect.component_id,
                    "frequency": defect.frequency
                }
                for defect_id, defect in self.defects.items()
            },
            "solutions": {
                sol_id: {
                    "id": sol.solution_id,
                    "name": sol.solution_name,
                    "description": sol.description,
                    "defect_id": sol.defect_id,
                    "steps": sol.steps,
                    "effectiveness_rate": sol.effectiveness_rate
                }
                for sol_id, sol in self.solutions.items()
            },
            "relationships": [
                {
                    "source": rel.source_id,
                    "target": rel.target_id,
                    "type": rel.relation_type.value,
                    "properties": rel.properties
                }
                for rel in self.relationships
            ]
        }
    
    def get_summary(self) -> str:
        """获取知识图谱的摘要信息"""
        return f"""
=== {self.category.category_name} 知识图谱 ===
品类ID: {self.category.category_id}
组件数量: {len(self.components)}
缺陷数量: {len(self.defects)}
解决方案数量: {len(self.solutions)}
关系数量: {len(self.relationships)}
"""


# ============= 演示：智能耳机知识图谱 =============

def create_smart_earphones_kg() -> KnowledgeGraphSchema:
    """
    创建智能耳机的知识图谱
    """
    # 创建品类
    category = ProductCategory(
        category_id="CAT001",
        category_name="智能耳机",
        description="无线蓝牙智能耳机"
    )
    
    kg = KnowledgeGraphSchema(category=category)
    
    # 添加组件
    components = [
        Component(
            component_id="COMP001",
            component_name="蓝牙芯片",
            description="无线连接模块",
            properties={"type": "wireless", "version": "5.0"}
        ),
        Component(
            component_id="COMP002",
            component_name="扬声器",
            description="音频播放单元",
            properties={"size": "10mm", "impedance": "32Ω"}
        ),
        Component(
            component_id="COMP003",
            component_name="电池",
            description="续航电源模块",
            properties={"capacity": "50mAh", "type": "Li-Po"}
        ),
        Component(
            component_id="COMP004",
            component_name="麦克风",
            description="语音输入单元",
            properties={"type": "MEMS", "SNR": "60dB"}
        ),
        Component(
            component_id="COMP005",
            component_name="触控按键",
            description="用户交互界面",
            properties={"type": "touch-sensitive", "response_time": "50ms"}
        )
    ]
    
    for comp in components:
        kg.add_component(comp)
    
    # 添加缺陷和解决方案
    defect_data = [
        {
            "component_id": "COMP001",
            "defect": Defect(
                defect_id="DEF001",
                defect_name="连接不稳定",
                severity="high",
                description="蓝牙频繁断连",
                frequency=45
            ),
            "solution": Solution(
                solution_id="SOL001",
                solution_name="固件升级",
                description="更新蓝牙芯片固件版本",
                steps=["1. 连接到APP", "2. 检查固件版本", "3. 点击升级", "4. 等待完成"],
                effectiveness_rate=0.92
            )
        },
        {
            "component_id": "COMP002",
            "defect": Defect(
                defect_id="DEF002",
                defect_name="音质差",
                severity="medium",
                description="声音失真或低沉",
                frequency=38
            ),
            "solution": Solution(
                solution_id="SOL002",
                solution_name="清洁扬声器",
                description="清理扬声器出孔防尘膜",
                steps=["1. 取下耳机", "2. 用软刷清洁", "3. 避免接触液体", "4. 自然干燥"],
                effectiveness_rate=0.78
            )
        },
        {
            "component_id": "COMP003",
            "defect": Defect(
                defect_id="DEF003",
                defect_name="续航时间短",
                severity="high",
                description="电池快速耗尽",
                frequency=52
            ),
            "solution": Solution(
                solution_id="SOL003",
                solution_name="优化充电策略",
                description="调整系统功耗设置",
                steps=["1. 打开设置菜单", "2. 选择省电模式", "3. 关闭不必要功能", "4. 重新配对"],
                effectiveness_rate=0.85
            )
        },
        {
            "component_id": "COMP004",
            "defect": Defect(
                defect_id="DEF004",
                defect_name="降噪效果不好",
                severity="medium",
                description="背景噪音未能有效消除",
                frequency=31
            ),
            "solution": Solution(
                solution_id="SOL004",
                solution_name="重新佩戴调整",
                description="确保耳塞密封性和位置正确",
                steps=["1. 取下耳机", "2. 更换合适尺寸的硅胶套", "3. 重新插入耳道", "4. 测试降噪效果"],
                effectiveness_rate=0.88
            )
        },
        {
            "component_id": "COMP005",
            "defect": Defect(
                defect_id="DEF005",
                defect_name="触控失效",
                severity="critical",
                description="按键无反应",
                frequency=28
            ),
            "solution": Solution(
                solution_id="SOL005",
                solution_name="重置设备",
                description="恢复出厂设置",
                steps=["1. 完全关闭设备", "2. 同时按住两个按键10秒", "3. 等待LED闪烁", "4. 重新配对"],
                effectiveness_rate=0.95
            )
        }
    ]
    
    for item in defect_data:
        kg.add_defect(item["defect"], item["component_id"])
        kg.add_solution(item["solution"], item["defect"].defect_id)
    
    kg.build_category_component_relation()
    return kg


# ============= 演示：女士连衣裙知识图谱 =============

def create_womens_dress_kg() -> KnowledgeGraphSchema:
    """
    创建女士连衣裙的知识图谱
    """
    # 创建品类
    category = ProductCategory(
        category_id="CAT002",
        category_name="女士连衣裙",
        description="日常穿着的女性连衣裙"
    )
    
    kg = KnowledgeGraphSchema(category=category)
    
    # 添加组件
    components = [
        Component(
            component_id="COMP201",
            component_name="面料",
            description="裙子主要材质",
            properties={"material": "棉聚", "weight": "180g/m²"}
        ),
        Component(
            component_id="COMP202",
            component_name="拉链",
            description="前开口拉链",
            properties={"type": "YKK", "length": "35cm"}
        ),
        Component(
            component_id="COMP203",
            component_name="钮扣",
            description="装饰和功能纽扣",
            properties={"material": "树脂", "size": "15mm"}
        ),
        Component(
            component_id="COMP204",
            component_name="腰部弹性带",
            description="腰部舒适支撑",
            properties={"material": "弹力带", "width": "3cm"}
        ),
        Component(
            component_id="COMP205",
            component_name="缝线",
            description="所有缝合接缝",
            properties={"thread_type": "涤纶", "stitch_strength": "high"}
        )
    ]
    
    for comp in components:
        kg.add_component(comp)
    
    # 添加缺陷和解决方案
    defect_data = [
        {
            "component_id": "COMP201",
            "defect": Defect(
                defect_id="DEF201",
                defect_name="褪色",
                severity="medium",
                description="穿着过程中颜色逐渐变浅",
                frequency=67
            ),
            "solution": Solution(
                solution_id="SOL201",
                solution_name="正确洗涤方式",
                description="使用冷水和专业洗涤剂",
                steps=["1. 用冷水洗涤", "2. 使用中性洗涤剂", "3. 避免阳光直晒", "4. 翻面晾干"],
                effectiveness_rate=0.82
            )
        },
        {
            "component_id": "COMP201",
            "defect": Defect(
                defect_id="DEF202",
                defect_name="起球",
                severity="medium",
                description="穿着一段时间后出现球化现象",
                frequency=55
            ),
            "solution": Solution(
                solution_id="SOL202",
                solution_name="使用除球器",
                description="使用专业的衣物除球器处理",
                steps=["1. 准备除球器", "2. 轻轻擦拭起球区域", "3. 不要用力过度", "4. 定期维护"],
                effectiveness_rate=0.90
            )
        },
        {
            "component_id": "COMP202",
            "defect": Defect(
                defect_id="DEF203",
                defect_name="拉链卡顿",
                severity="high",
                description="拉链拉动时卡住或生硬",
                frequency=41
            ),
            "solution": Solution(
                solution_id="SOL203",
                solution_name="润滑拉链",
                description="使用石墨笔或拉链润滑剂",
                steps=["1. 取下连衣裙", "2. 用石墨笔沿拉链涂抹", "3. 反复拉动拉链", "4. 不要使用油脂"],
                effectiveness_rate=0.88
            )
        },
        {
            "component_id": "COMP203",
            "defect": Defect(
                defect_id="DEF204",
                defect_name="纽扣脱落",
                severity="high",
                description="装饰或功能纽扣松动脱落",
                frequency=48
            ),
            "solution": Solution(
                solution_id="SOL204",
                solution_name="重新缝纫纽扣",
                description="用匹配的线重新固定纽扣",
                steps=["1. 准备针和线", "2. 对齐原位置", "3. 交叉缝纫", "4. 打结加固"],
                effectiveness_rate=0.98
            )
        },
        {
            "component_id": "COMP205",
            "defect": Defect(
                defect_id="DEF205",
                defect_name="缝线开裂",
                severity="high",
                description="衣物缝合处出现断裂",
                frequency=36
            ),
            "solution": Solution(
                solution_id="SOL205",
                solution_name="缝线修补",
                description="使用相同颜色的线重新缝合",
                steps=["1. 定位断裂位置", "2. 用针线缝补", "3. 注意走向一致", "4. 加强薄弱处"],
                effectiveness_rate=0.92
            )
        }
    ]
    
    for item in defect_data:
        kg.add_defect(item["defect"], item["component_id"])
        kg.add_solution(item["solution"], item["defect"].defect_id)
    
    kg.build_category_component_relation()
    return kg


def create_generic_kg(category_name: str, template_type: str = "General") -> KnowledgeGraphSchema:
    """
    根据模版类型生成通用的知识图谱
    支持类型: Electronics, Clothing, Food, Beauty, General
    """
    category = ProductCategory(
        category_id=f"CAT_GEN_{hash(category_name) % 10000}",
        category_name=category_name,
        description=f"{category_name} 品类通用图谱"
    )
    kg = KnowledgeGraphSchema(category=category)

    # 1. 定义不同模版的组件配置
    templates = {
        "Electronics": [
            ("电源/电池", "Power/Battery", "续航与充电模块"),
            ("屏幕/显示", "Display", "视觉交互界面"),
            ("按键/触控", "Controls", "物理或触摸输入"),
            ("连接/信号", "Connectivity", "蓝牙/Wi-Fi/网络"),
            ("机身/外壳", "Body", "整体外观与材质")
        ],
        "Clothing": [
            ("面料", "Fabric", "主要材质"),
            ("缝线", "Stitching", "缝合工艺"),
            ("尺码", "Sizing", "版型与大小"),
            ("颜色", "Color", "染色与外观"),
            ("拉链/纽扣", "Accessories", "辅料配件")
        ],
        "Food": [
            ("口味", "Taste", "味道与口感"),
            ("新鲜度", "Freshness", "保质期与变质情况"),
            ("包装", "Packaging", "密封与外观"),
            ("分量", "Quantity", "净含量与数量"),
            ("异物", "Foreign Object", "卫生安全")
        ],
        "Beauty": [
            ("质地", "Texture", "产品触感与吸收度"),
            ("气味", "Smell", "香氛与异味"),
            ("过敏反应", "Allergy", "皮肤适应性"),
            ("包装设计", "Packaging", "瓶身与压泵"),
            ("功效", "Effect", "宣称效果")
        ],
        "General": [ # 缺省模版
            ("产品质量", "Quality", "整体做工与质量"),
            ("物流配送", "Logistics", "快递与包装"),
            ("卖家服务", "Service", "客服态度与响应"),
            ("价格性价比", "Price", "价格与价值匹配度"),
            ("描述相符", "Description", "实物与宣传差距")
        ]
    }

    # 2. 获取组件列表（默认为 General）
    comps_config = templates.get(template_type, templates["General"])
    
    # 3. 添加组件
    comp_ids = []
    for idx, (c_name, c_eng, c_desc) in enumerate(comps_config):
        c_id = f"COMP_{template_type[:3].upper()}_{idx+1:02d}"
        comp = Component(
            component_id=c_id,
            component_name=c_name,
            description=c_desc,
            properties={"english_alias": c_eng}
        )
        kg.add_component(comp)
        comp_ids.append(c_id)

    # 4. 定义不同模版的缺陷配置 (对应上面的组件顺序)
    # 结构: [ (缺陷名, 严重度, 描述, 解决方案名, 方案步骤), ... ]
    # 每个列表对应一个组件
    
    defects_map = {
        "Electronics": [
            [("续航太短", "medium", "耗电异常快", "校准电池/关闭后台", ["充满电再使用", "关闭不必要的功能"]), ("无法充电", "critical", "充不进电", "检查充电器", ["更换线缆尝试", "检查接口异物"])], # 电源
            [("屏幕碎裂", "critical", "物理损坏", "联系售后维修", ["拍照留证", "联系客服寄修"]), ("显示不清", "medium", "模糊/色差", "调节显示设置", ["调整分辨率", "检查贴膜"])], # 屏幕
            [("按键失灵", "high", "无反应", "重启设备", ["长按电源键重启", "检查是否有卡住"]), ("触控不灵", "medium", "断触", "清洁屏幕", ["擦拭屏幕油污", "重启测试"])], # 按键
            [("WiFi断连", "medium", "信号不稳定", "重置网络", ["忽略网络重连", "重启路由器"]), ("蓝牙连不上", "high", "配对失败", "重新配对", ["删除旧配对记录", "重新开启搜索"])], # 连接
            [("外壳划痕", "low", "外观瑕疵", "补偿/退换", ["申请部分退款", "在不影响使用下接受"]), ("掉漆", "low", "涂层脱落", "外观补偿", ["联系客服补偿", "注意保护"])] # 机身
        ],
        "Clothing": [
            [("起球", "medium", "摩擦起球", "修剪毛球", ["使用去毛球机", "注意洗涤方式"]), ("扎人", "high", "材质不适", "退货/柔顺剂", ["使用柔顺剂浸泡", "申请退货"])], # 面料
            [("开线", "high", "缝合断裂", "缝补/退换", ["手工缝补", "严重则退换"]), ("线头多", "low", "做工粗糙", "自行修剪", ["用剪刀修剪", "联系客服补偿"])], # 缝线
            [("偏小", "medium", "尺码不准", "换大一码", ["申请换货", "咨询客服尺码"]), ("偏大", "medium", "版型宽松", "换小一码", ["申请换货", "搭配腰带"])], # 尺码
            [("褪色", "medium", "洗涤掉色", "固色处理", ["盐水浸泡", "分开洗涤"]), ("色差", "low", "与图片不符", "解释光线问题", ["实物拍摄对比", "申请退货"])], # 颜色
            [("拉链卡顿", "medium", "不顺滑", "润滑", ["涂抹蜡或肥皂", "多拉几次"]), ("纽扣掉了", "medium", "配件缺失", "缝补", ["使用备用扣", "自己缝上"])] # 配件
        ],
        "Food": [
            [("难吃", "high", "口味不合", "反馈建议", ["记录用户偏好", "推荐其他口味"]), ("太咸/太甜", "medium", "调味过重", "搭配食用", ["建议搭配主食", "反馈工厂调整"])], # 口味
            [("变质", "critical", "已坏", "全额退款", ["拍照确认", "立即退款并赔偿"]), ("不新鲜", "high", "口感差", "部分退款", ["核实生产日期", "补偿优惠券"])], # 新鲜度
            [("漏气", "high", "密封失效", "退款/补发", ["确认破损情况", "补发新品"]), ("包装挤压", "low", "外观变形", "致歉", ["解释物流原因", "赠送小礼品"])], # 包装
            [("缺斤少两", "high", "分量不足", "补差价", ["称重核实", "补足差价"]), ("空包", "critical", "只有包装", "补发", ["核实重量", "立即补发"])], # 分量
            [("吃出头发", "critical", "卫生问题", "赔偿", ["依规赔偿", "整改生产线"]), ("有虫子", "critical", "严重异物", "高额赔偿", ["安抚用户", "按照食安法赔偿"])] # 异物
        ],
        "Beauty": [
            [("油腻", "medium", "吸收不好", "调整用法", ["减少用量", "按摩促进吸收"]), ("搓泥", "medium", "产品打架", "简化护肤", ["等待前序吸收", "更换搭配"])], # 质地
            [("味道难闻", "high", "香精味重", "解释成分", ["说明原料气味", "建议通风放置"]), ("刺鼻", "medium", "气味不适", "退货", ["不喜欢可退", "推荐无香型"])], # 气味
            [("过敏红肿", "critical", "不良反应", "立即停用/就医", ["指导停用", "承担医药费"]), ("刺痛", "high", "屏障受损", "暂停使用", ["精简护肤", "使用修护类"])], # 过敏
            [("压泵坏了", "critical", "无法挤出", "补发泵头", ["补发配件", "指导疏通"]), ("漏液", "high", "运输破损", "补发", ["拍照确认", "重新发货"])], # 包装
            [("没效果", "medium", "未达预期", "坚持使用", ["说明起效周期", "指导正确手法"]), ("假白", "medium", "妆效不自然", "少量多次", ["控制用量", "做好打底"])] # 功效
        ],
        "General": [
            [("质量差", "high", "易坏", "售后处理", ["核实具体问题", "依据保修处理"]), ("做工粗糙", "medium", "细节不好", "致歉/补偿", ["反馈工厂", "发放优惠券"])],
            [("物流慢", "medium", "配送延迟", "催促物流", ["联系快递公司", "加急派送"]), ("暴力运输", "medium", "外箱破损", "投诉快递", ["向快递索赔", "加强包装"])],
            [("态度差", "high", "回复慢/凶", "改善服务", ["培训客服", "主管致歉"]), ("不理人", "high", "无响应", "快速响应", ["设置自动回复", "增加人手"])],
            [("太贵", "medium", "性价比低", "解释价值", ["强调品质", "推荐活动"]), ("降价了", "medium", "买贵了", "保价", ["退差价", "赠送积分"])],
            [("描述不符", "high", "虚假宣传", "核实修正", ["修改详情页", "退货退款"]), ("发错货", "critical", "款式错误", "免费换货", ["承担运费换货", "赠送补偿"])]
        ]
    }
    
    # 5. 应用缺陷和解决方案
    defect_config_list = defects_map.get(template_type, defects_map["General"])
    
    # 确保 config 列表长度和组件列表长度一致 (取最小值)
    loop_len = min(len(comp_ids), len(defect_config_list))
    
    count_def = 0
    count_sol = 0
    
    for i in range(loop_len):
        c_id = comp_ids[i]
        defects_info = defect_config_list[i] # 这是一个列表，包含该组件的多个缺陷
        
        for d_info in defects_info:
            d_name, d_sev, d_desc, s_name, s_steps = d_info
            
            d_id = f"DEF_{template_type[:3]}_{count_def:03d}"
            count_def += 1
            
            defect_obj = Defect(
                defect_id=d_id,
                defect_name=d_name,
                severity=d_sev,
                description=d_desc,
                frequency=50 # 默认值
            )
            kg.add_defect(defect_obj, c_id)
            
            # 添加解决方案
            s_id = f"SOL_{template_type[:3]}_{count_sol:03d}"
            count_sol += 1
            
            sol_obj = Solution(
                solution_id=s_id,
                solution_name=s_name,
                description=f"针对 {d_name} 的标准处理方案",
                steps=s_steps,
                effectiveness_rate=0.85
            )
            kg.add_solution(sol_obj, d_id)
            
    kg.build_category_component_relation()
    return kg

# ============= 产品分类体系 (Taxonomy) =============

PRODUCT_TAXONOMY = {
    "电子数码": {
        "template": "Electronics",
        "subcategories": ["智能手机", "笔记本电脑", "平板电脑", "智能手表", "智能耳机", "相机", "蓝牙音箱", "充电宝", "数据线", "路由器", "键盘鼠标"]
    },
    "服装服饰": {
        "template": "Clothing",
        "subcategories": ["男士T恤", "女士连衣裙", "牛仔裤", "运动外套", "羽绒服", "衬衫", "卫衣", "休闲裤", "内衣", "袜子"]
    },
    "美妆护肤": {
        "template": "Beauty",
        "subcategories": ["洗面奶", "爽肤水", "乳液面霜", "精华液", "防晒霜", "口红", "粉底液", "眼影", "香水", "面膜"]
    },
    "食品饮料": {
        "template": "Food",
        "subcategories": ["休闲零食", "坚果炒货", "肉干肉脯", "饼干蛋糕", "茶饮冲调", "乳品", "方便速食", "生鲜水果", "粮油米面"]
    },
    "家居生活": {
        "template": "General", 
        "subcategories": ["床上用品", "收纳整理", "厨房用具", "卫浴用品", "灯具照明", "家纺", "装饰摆件"]
    },
    "家用电器": {
        "template": "Electronics",
        "subcategories": ["电饭煲", "微波炉", "吸尘器", "空气净化器", "加湿器", "电吹风", "洗衣机", "冰箱", "空调"]
    },
     "鞋靴箱包": {
        "template": "Clothing", 
        "subcategories": ["运动鞋", "皮鞋", "休闲鞋", "高跟鞋", "行李箱", "双肩包", "手提包"]
    }
}


# ============= 主程序 =============

if __name__ == "__main__":
    print("\n" + "="*60)
    print("电商评论分析系统通用知识图谱 Schema 演示")
    print("="*60)
    
    # 创建两个知识图谱
    earphones_kg = create_smart_earphones_kg()
    dress_kg = create_womens_dress_kg()
    
    # 打印摘要信息
    print(earphones_kg.get_summary())
    print(dress_kg.get_summary())
    
    # 转换为字典并打印
    print("\n" + "="*60)
    print("智能耳机知识图谱 - 字典数据结构")
    print("="*60)
    earphones_dict = earphones_kg.to_dict()
    import json
    print(json.dumps(earphones_dict, ensure_ascii=False, indent=2))
    
    print("\n" + "="*60)
    print("女士连衣裙知识图谱 - 字典数据结构")
    print("="*60)
    dress_dict = dress_kg.to_dict()
    print(json.dumps(dress_dict, ensure_ascii=False, indent=2))
    
    # 演示关系查询
    print("\n" + "="*60)
    print("知识图谱关系演示")
    print("="*60)
    
    print(f"\n【智能耳机】主要关系路径：")
    for rel in earphones_kg.relationships[:5]:
        print(f"  {rel}")
    
    print(f"\n【女士连衣裙】主要关系路径：")
    for rel in dress_kg.relationships[:5]:
        print(f"  {rel}")
    
    print("\n✓ Schema 已成功验证：同一套 Schema 可适配完全不同的品类！")
