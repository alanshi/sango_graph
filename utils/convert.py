import pandas as pd
from neo4j import GraphDatabase


def insert_data_to_neo4j(uri, user, password, csv_data):
    driver = GraphDatabase.driver(uri, auth=(user, password))

    def create_nodes_and_relationships(tx):
        for index, row in csv_data.iterrows():
            head = row['head']
            tail = row['tail']
            relation = row['relation']

            # 创建头节点
            tx.run("MERGE (h:Person {name: $head})", head=head)
            # 创建尾节点
            tx.run("MERGE (t:Person {name: $tail})", tail=tail)
            # 创建关系
            tx.run("MATCH (h:Person {name: $head}), (t:Person {name: $tail}) "
                   "MERGE (h)-[r:" + relation.upper().replace(" ", "_") + "]->(t)",
                   head=head, tail=tail)

    with driver.session() as session:
        session.write_transaction(create_nodes_and_relationships)

    driver.close()


df = pd.read_csv("/Users/alan/mywork/sango_graph/relationships.csv")

# Neo4j 连接信息，需要根据实际情况修改
uri = "bolt://localhost:7687"
user = "neo4j"
password = "admin123"

# 插入数据到 Neo4j
insert_data_to_neo4j(uri, user, password, df)