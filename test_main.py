from fastapi.testclient import TestClient
from main import app
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base, get_db

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)

Base.metadata.create_all(bind=test_engine)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

def test_health_check():
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_expense():
    expense_data = expense_data = {
    "merchant": "Walmart",
    "amount": 200.00,
    "category": "Groceries"
}
    response = client.post("/expenses", json=expense_data)
    assert response.status_code == 200
    created_expense = response.json()
    assert created_expense["merchant"] == expense_data["merchant"]
    assert created_expense["amount"] == expense_data["amount"]
    assert created_expense["category"] == expense_data["category"]
    assert "id" in created_expense

def test_create_expense_with_negative_amount():
    expense_data = {
    "merchant": "Wendys",
    "amount": -20.00,
    "category": "Fast Food"
    }
    response = client.post("/expenses", json=expense_data)
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data

def test_get_expenses():
    expense_data = {
    "merchant": "Burger King",
    "amount": 25.00,
    "category": "Fast Food"
    }
     
    post_response = client.post("/expenses",json=expense_data )
    get_response = client.get("/expenses")
    assert get_response.status_code == 200
    returned_expenses = get_response.json()
    assert len(returned_expenses) == 1

def test_get_one_expense():
    response = client