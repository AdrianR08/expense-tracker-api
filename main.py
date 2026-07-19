from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field,ConfigDict
from sqlalchemy.orm import Session
import models
from database import Base,engine,get_db
from sqlalchemy import select,func

Base.metadata.create_all(bind=engine)

class Expense(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    merchant: str = Field(min_length=1)
    amount: float = Field(gt=0)
    category: str = Field(min_length=1)
   
app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/expenses")
def get_expenses(db: Session = Depends(get_db), category: str | None = None):
    statement = select(models.Expense)
    if category is not None:
        statement = statement.where(func.lower(models.Expense.category) == category.lower())
    expense_records = db.scalars(statement).all()
    return expense_records


@app.post("/expenses")
def create_expenses(expense: Expense, db: Session = Depends(get_db)):
    new_expense = models.Expense(
        merchant=expense.merchant,
        amount=expense.amount,
        category=expense.category
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    expense_data = expense.model_dump()
    return new_expense

@app.get("/expenses/total")
def get_expense_total(db: Session = Depends(get_db), category: str | None = None):
    statement = select(func.sum(models.Expense.amount))
    if category is not None:
        statement = statement.where(func.lower(models.Expense.category) == category.lower())
    total = db.scalar(statement)
    if total is None:
        total = 0
    return {"total": total}


@app.get("/expenses/{expense_id}")
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(models.Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(models.Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted"}
    

@app.put("/expenses/{expense_id}")
def update_expense(
    expense_id: int,
    updated_expense: Expense,
    db: Session = Depends(get_db)
):
    expense = db.get(models.Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    expense.merchant = updated_expense.merchant
    expense.amount = updated_expense.amount
    expense.category = updated_expense.category
    db.commit()
    db.refresh(expense)
    return expense
    

    


        

    
 
        
        




