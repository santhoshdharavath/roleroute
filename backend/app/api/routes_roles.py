from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_demo_user
from app.db.session import get_db
from app.models.learning import Role
from app.models.user import User
from app.schemas.common import RoleOut, RolePathOut
from app.services.scoring import completed_topic_ids, module_progress, next_topic, role_topics, to_role_out, to_topic_out

router = APIRouter(tags=["roles"])


@router.get("/roles", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db)) -> list[RoleOut]:
    roles = db.query(Role).order_by(Role.id).all()
    return [to_role_out(role) for role in roles]


@router.get("/roles/{role_id}/path", response_model=RolePathOut)
def get_role_path(
    role_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user),
) -> RolePathOut:
    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found.")

    completed_ids = completed_topic_ids(db, user.id) if user.selected_role_id == role.id else set()
    modules = module_progress(db, role.id, completed_ids)
    upcoming = next_topic(role_topics(db, role.id), completed_ids)
    return RolePathOut(
        role=to_role_out(role),
        modules=modules,
        next_topic=to_topic_out(upcoming, completed_ids) if upcoming else None,
    )
