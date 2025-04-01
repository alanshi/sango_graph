import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, call
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.people_service import PeopleService

@pytest.mark.asyncio
async def test_get_person_relationships_success():
    # 重构模拟数据
    mock_nodes = [
        {"name": "刘备", "properties": {"age": 40}},
        {"name": "关羽", "properties": {"age": 38}}
    ]

    mock_rel = MagicMock(
        id=1,
        type="younger_sworn_brother",
        start_node=mock_nodes[0],
        end_node=mock_nodes[1],
        nodes=MagicMock(return_value=[mock_nodes[0], mock_nodes[1]]),
        __getitem__=lambda self, key: getattr(self, key)
    )

    # 修正异步调用链
    mock_db = AsyncMock()
    mock_result = AsyncMock()
    mock_result.values = AsyncMock(return_value=[
        [  # records
            [mock_nodes, [mock_rel]]  # 修正数据结构
        ]
    ])
    mock_db.run.return_value = mock_result

    service = PeopleService(mock_db)
    result = await service.get_person_relationships("刘备", "all", 1)

    # 验证结果
    assert len(result["nodes"]) == 2
    assert result["links"][0]["source"] == "刘备"

    # 验证异步调用
    mock_db.run.assert_awaited_once_with(
        "MATCH path = (p:Person {name: $name})-[*1..1]-(related) "
        "WHERE $relation_type = 'all' OR ANY(r IN RELATIONSHIPS(path) WHERE type(r) = $relation_type) "
        "UNWIND NODES(path) as node "
        "UNWIND RELATIONSHIPS(path) as rel "
        "WITH "
        "  COLLECT(DISTINCT node) as all_nodes, "
        "  COLLECT(DISTINCT rel) as all_rels "
        "RETURN all_nodes, all_rels",
        name="刘备",
        relation_type="all",
        depth=1
    )

@pytest.mark.asyncio
async def test_get_person_relationships_no_results():
    mock_db = AsyncMock()
    mock_result = AsyncMock()
    mock_result.values = AsyncMock(return_value=[])
    mock_db.run.return_value = mock_result

    service = PeopleService(mock_db)
    result = await service.get_person_relationships("曹操", "all", 1)

    assert result is None
    mock_db.run.assert_awaited_once()

@pytest.mark.asyncio
async def test_relationship_filtering():
    # 修正mock关系对象
    mock_rel = MagicMock(
        id=1,
        type="younger_sworn_brother",
        start_node={"name": "刘备"},
        end_node={"name": "张飞"},
        __getitem__=lambda self, key: getattr(self, key)
    )

    mock_db = AsyncMock()
    mock_result = AsyncMock()
    mock_result.values = AsyncMock(return_value=[
        [  # records
            [
                [{"name": "刘备"}, {"name": "张飞"}],
                [mock_rel]
            ]
        ]
    ])
    mock_db.run.return_value = mock_result

    service = PeopleService(mock_db)
    result = await service.get_person_relationships("刘备", "younger_sworn_brother", 1)

    assert len(result["links"]) == 1
    assert result["links"][0]["type"] == "younger_sworn_brother"

@pytest.mark.asyncio
async def test_get_full_graph():
    # 重构全图测试
    mock_rel = MagicMock(
        type="son",
        start_node={"name": "关羽"},
        end_node={"name": "关平"},
        __getitem__=lambda self, key: getattr(self, key)
    )

    mock_db = AsyncMock()
    mock_result = AsyncMock()
    mock_result.values = AsyncMock(return_value=[
        [  # records
            (
                {"name": "关羽", "properties": {}},
                mock_rel,
                {"name": "关平", "properties": {}}
            )
        ]
    ])
    mock_db.run.return_value = mock_result

    service = PeopleService(mock_db)
    result = await service.get_full_graph("all", 1)

    assert len(result["nodes"]) == 2
    assert result["links"][0]["source"] == "关羽"

    mock_db.run.assert_awaited_once_with(
        "MATCH (p:Person)-[r]->(related:Person) "
        "WHERE $relation_type = 'all' OR r.type = $relation_type "
        "WITH p, r, related LIMIT $limit "
        "RETURN p, r, related",
        relation_type="all",
        limit=1000
    )

# 同步测试保持不变
def test_degree_calculation():
    service = PeopleService(None)

    rel = MagicMock(
        start_node={"name": "刘备"},
        nodes=MagicMock(return_value=["刘备", "关羽"])
    )
    assert service._calculate_degree(rel, "刘备") == 1

    rel = MagicMock(
        start_node={"name": "关羽"},
        nodes=MagicMock(return_value=["关羽", "关平", "刘备"])
    )
    assert service._calculate_degree(rel, "刘备") == 1

def test_relation_label_mapping():
    service = PeopleService(None)

    rel = MagicMock(type="younger_sworn_brother")
    assert service._get_relation_label(rel, True) == "义弟"
    assert service._get_relation_label(rel, False) == "义兄"

    rel = MagicMock(type="unknown_type")
    assert service._get_relation_label(rel, True) == "unknown_type"

if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])