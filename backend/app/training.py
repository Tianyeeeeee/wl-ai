# app/training.py
from fastapi import APIRouter
from pydantic import BaseModel
from .vector_store import VectorStore
from .db import DBManager

router = APIRouter()
vs = VectorStore()
db = DBManager()


class TrainRequest(BaseModel):
    training_type: str
    content: dict


@router.post("/api/rag/train")
def train(req: TrainRequest):
    try:
        vs.add_training_data(req.training_type, req.content)
        return {"status": "success", "message": "Training data added."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def auto_train():
    """后台任务调用的函数"""
    try:
        tables = db.get_all_tables_metadata()
        if not tables:
            return {"status": "warning", "message": "No tables found."}

        count = 0
        for t in tables:
            vs.add_training_data('ddl', t)
            count += 1
            if count % 20 == 0:
                print(f"  ...Indexed {count} tables")

        return {"status": "success", "message": f"Indexed {count} tables."}
    except Exception as e:
        return {"status": "error", "message": str(e)}