from fastapi import APIRouter, Depends, HTTPException, Query
from database.driver import get_db
from services.people_service import PeopleService


from models.schemas import GraphResponse


router = APIRouter(prefix="/api/v1/people")

@router.get("/relationships/{name}", response_model=GraphResponse)
async def get_relationships(
    name: str,
    relation_type: str = Query("all", description="关系类型过滤条件"),
    depth: int = Query(1, ge=1, le=3, description="关系度数（1-3）"),
    db=Depends(get_db)
):
    return await PeopleService(db).get_person_relationships(
        name=name,
        relation_type=relation_type,
        depth=depth
    )


@router.get("/graph", response_model=GraphResponse)
async def get_graph_data(
    relation_type: str = Query("all", description="关系类型过滤条件"),
    depth: int = Query(1, ge=1, le=3, description="关系度数（1-3）"),
    db=Depends(get_db)
):
    return await PeopleService(db).get_full_graph(
        relation_type=relation_type,
        depth=depth
    )