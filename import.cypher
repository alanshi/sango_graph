:auto BEGIN
// 创建人物节点

// 创建人物关系
COMMIT

CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON p.name;
