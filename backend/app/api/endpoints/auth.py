from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    return {"message": "auth login endpoint"}


@router.get("/me")
async def get_current_user():
    return {"message": "current user details"}
