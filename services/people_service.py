class PeopleService:

    def __init__(self, db):
        self.db = db  # 存储数据库会话引用
    async def get_person_relationships(self, name: str, relation_type: str, depth: int) -> dict:
        # query = (
        #     "MATCH path = (p:Person {name: $name})-[*1..$depth]-(related) "
        #     "WHERE $relation_type = 'all' OR ANY(r IN RELATIONSHIPS(path) WHERE r.type = $relation_type) "
        #     "UNWIND NODES(path) as node "
        #     "UNWIND RELATIONSHIPS(path) as rel "
        #     "WITH COLLECT(DISTINCT node) as nodes, COLLECT(DISTINCT rel) as rels "
        #     "RETURN nodes, rels"
        # )
        # """使用原生Cypher查询N度关系"""

        query = (
            "MATCH path = (p:Person {name: $name})-[*1..%d]-(related) "
            # "WHERE $relation_type = 'all' OR ANY(r IN RELATIONSHIPS(path) WHERE r.type = $relation_type) "
            "WHERE $relation_type = 'all' OR ANY(r IN RELATIONSHIPS(path) WHERE type(r) = $relation_type) "
            "UNWIND NODES(path) as node "  # 展开路径中的所有节点
            "UNWIND RELATIONSHIPS(path) as rel "  # 展开路径中的所有关系
            "WITH "
            "  COLLECT(DISTINCT node) as all_nodes, "  # 去重节点
            "  COLLECT(DISTINCT rel) as all_rels "     # 去重关系
            "RETURN all_nodes, all_rels"
        ) % depth

        result = await self.db.run(
            query,
            name=name,
            relation_type=relation_type,
            depth=depth)
        records = await result.values()

        if not records or not records[0]:
            return None

        # 解析结果结构
        all_nodes = records[0][0]  # 节点列表
        if not records or not records[0]:
            return None

        # 解析结果结构
        all_nodes = records[0][0]  # 节点列表
        all_rels = records[0][1]    # 关系列表

        # 处理节点
        seen_nodes = set()
        nodes = []
        for node in all_nodes:
            if node["name"] not in seen_nodes:
                nodes.append({
                    "name": node["name"],
                    "properties": dict(node)
                })
                seen_nodes.add(node["name"])

        # 处理关系
        seen_rels = set()
        links = []
        for rel in all_rels:
            if rel.id not in seen_rels:
                # 获取关系端点
                start_node = rel.start_node["name"]
                end_node = rel.end_node["name"]
                is_outgoing = start_node == name

                links.append({
                    "source": start_node if is_outgoing else end_node,
                    "target": end_node if is_outgoing else start_node,
                    "type": rel.type,
                    "label": self._get_relation_label(rel, is_outgoing),
                    "properties": dict(rel),
                    "degree": self._calculate_degree(rel, name)
                })
                seen_rels.add(rel.id)

        return {"nodes": nodes, "links": links}

    def _calculate_degree(self, rel, center_name: str) -> int:
        """计算关系度数（从中心节点出发的层级）"""
        if rel.start_node["name"] == center_name:
            return 1  # 直接关系
        elif rel.end_node["name"] == center_name:
            return 1  # 反向直接关系
        else:
            # 通过路径长度计算间接关系度数
            return min(
                len(rel.nodes) // 2 + 1,
                5  # 最大显示5度
            )

    def _get_relation_label(self, rel, is_outgoing: bool) -> str:
        """根据关系方向生成显示标签"""
        # 示例映射逻辑，根据实际业务需求调整
        label_map = {
            "younger_sworn_brother": {
                True: "义弟",
                False: "义兄"
            },
            "elder_sworn_brother": {
                True: "义兄",
                False: "义弟"
            },
            "son": {
                True: "儿子",
                False: "父亲"
            }
        }
        return label_map.get(rel.type, {}).get(is_outgoing, rel.type)

    async def get_full_graph(self, relation_type: str, depth: int) -> dict:
        # 原始查询保持不变
        query = (
            "MATCH (p:Person)-[r]->(related:Person) "
            "WHERE $relation_type = 'all' OR r.type = $relation_type "  # 动态过滤
            "WITH p, r, related LIMIT $limit "
            "RETURN p, r, related"
        )
        result = await self.db.run(
            query,
            relation_type=relation_type,
            limit=1000)  # 示例限制)
        records = await result.values()

        nodes = []
        links = []
        seen = set()

        for record in records:
            source = record[0]
            rel = record[1]
            target = record[2]

            # 处理source节点
            if source["name"] not in seen:
                nodes.append({
                    "name": source["name"],
                    "properties": dict(source)
                })
                seen.add(source["name"])

            # 处理target节点
            if target["name"] not in seen:
                nodes.append({
                    "name": target["name"],
                    "properties": dict(target)
                })
                seen.add(target["name"])

            # 处理关系
            links.append({
                "source": source["name"],
                "target": target["name"],
                "type": rel.type,
                "label": rel.get("label", ""),  # 假设关系有label属性
                "properties": dict(rel)
            })

        return {
            "nodes": nodes,
            "links": links
        }