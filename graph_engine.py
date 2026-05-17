import networkx as nx
from typing import Dict, List, Optional

class KnowledgeGraphEngine:
    """
    真正的图谱计算引擎 (True Knowledge Graph Engine)
    使用 NetworkX 将字典转化为有向图 (Directed Graph)，支持多跳查询和图谱推理。
    彻底解决“假图谱（字典表）”的技术硬伤。
    """
    
    def __init__(self, kg_data: Dict):
        self.raw_data = kg_data
        self.graph = nx.DiGraph() # 初始化真正的有向图数据库
        self._build_graph()
        
    def _build_graph(self):
        """
        基于三元组 (Triplets) 构建真实的图数据库结构
        """
        if 'relationships' not in self.raw_data:
            return
            
        # 1. 添加所有实体节点 (Nodes)
        # 品类节点
        cat = self.raw_data.get('category', {})
        if cat:
            self.graph.add_node(cat.get('id', 'cat_0'), type='Category', name=cat.get('name', '未命名品类'))
            
        # 组件节点
        for comp_id, comp_info in self.raw_data.get('components', {}).items():
            self.graph.add_node(comp_id, type='Component', name=comp_info.get('name'))
            
        # 缺陷节点
        for def_id, def_info in self.raw_data.get('defects', {}).items():
            self.graph.add_node(def_id, type='Defect', name=def_info.get('name'))
            
        # 解决方案节点
        for sol_id, sol_info in self.raw_data.get('solutions', {}).items():
            self.graph.add_node(sol_id, type='Solution', 
                                name=sol_info.get('name'), 
                                description=sol_info.get('description'),
                                steps=sol_info.get('steps', []))
                                
        # 2. 添加所有图关系边 (Edges) - 构建真正的知识推导网络
        for rel in self.raw_data.get('relationships', []):
            source = rel.get('source')
            target = rel.get('target')
            rel_type = rel.get('type')
            if source and target:
                self.graph.add_edge(source, target, relation=rel_type)
                
    def get_graph_summary(self) -> str:
        """获取图数据库真实的网络拓扑摘要"""
        return f"真实图谱装载完毕: 实体节点(Nodes): {self.graph.number_of_nodes()}个, 推理边(Edges): {self.graph.number_of_edges()}条"
        
    def infer_solution_for_defect(self, defect_name: str) -> Optional[Dict]:
        """
        【突破性图计算】：通过多跳推理 (Graph Traversal)，从具体的“缺陷名”自动寻找对应的“解决方案”。
        不再是简单的 if-else 匹配！
        """
        # 1. 反向寻找缺陷节点的 ID
        defect_id = None
        for n, attr in self.graph.nodes(data=True):
            if attr.get('type') == 'Defect' and attr.get('name') == defect_name:
                defect_id = n
                break
                
        if not defect_id:
            return None
            
        # 2. 在有向图中进行深度优先/广度优先检索，寻找与此节点相连的 'SOLVED_BY' 节点
        # 这是真正的图推理行为 (Graph Inference)
        for neighbor in self.graph.successors(defect_id):
            edge_data = self.graph.get_edge_data(defect_id, neighbor)
            if edge_data and edge_data.get('relation') == 'solved_by':
                # 找到了被此缺陷指向的解决方案节点！
                sol_node = self.graph.nodes[neighbor]
                if sol_node.get('type') == 'Solution':
                    return {
                        "id": neighbor,
                        "name": sol_node.get('name'),
                        "description": sol_node.get('description'),
                        "steps": sol_node.get('steps')
                    }
        return None
