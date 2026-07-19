from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field,ConfigDict
from sqlalchemy.orm import Session
import models
from database import Base,engine,get_db
from sqlalchemy import select,func
from datetime import date
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

class ExpenseCreate(BaseModel ):
    model_config = ConfigDict(str_strip_whitespace=True)
    merchant: str = Field(min_length=1)
    amount: float = Field(gt=0)
    category: str = Field(min_length=1)
    expense_date: date = Field(default_factory=date.today)

class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id :int
    merchant: str
    amount: float
    category: str
    expense_date: date
    

class MessageResponse(BaseModel):
     message: str

class TotalResponse(BaseModel):
    total: float

   
app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db), category: str | None = None, expense_date: date | None = None):
    statement = select(models.Expense)
    if expense_date is not None:
        statement = statement.where(models.Expense.expense_date == expense_date)
        
    if category is not None:
        statement = statement.where(func.lower(models.Expense.category) == category.lower())
    expense_records = db.scalars(statement).all()
    return expense_records


@app.post("/expenses", status_code=201, response_model = ExpenseResponse)
def create_expenses(expense: ExpenseCreate, db: Session = Depends(get_db)):
    new_expense = models.Expense(
        merchant=expense.merchant,
        amount=expense.amount,
        category=expense.category,
        expense_date=expense.expense_date
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    expense_data = expense.model_dump()
    return new_expense

@app.get("/expenses/total", response_model=TotalResponse)
def get_expense_total(db: Session = Depends(get_db), category: str | None = None, expense_date: date | None = None ):
    statement = select(func.sum(models.Expense.amount))
    if expense_date is not None:
        statement = statement.where(models.Expense.expense_date == expense_date)
    if category is not None:
        statement = statement.where(func.lower(models.Expense.category) == category.lower())
    total = db.scalar(statement)
    if total is None:
        total = 0
    return {"total": total}


@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(models.Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@app.delete("/expenses/{expense_id}", response_model=MessageResponse)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(models.Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted"}
    

@app.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    updated_expense: ExpenseCreate,
    db: Session = Depends(get_db),
):
    expense = db.get(models.Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    expense.merchant = updated_expense.merchant
    expense.amount = updated_expense.amount
    expense.category = updated_expense.category
    expense.expense_date = updated_expense.expense_date
    db.commit()
    db.refresh(expense)
    return expense
    

    


        

    
 
        
        




