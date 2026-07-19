from fastapi.testclient import TestClient
from fastapi import HTTPException
from main import app
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base, get_db
from datetime import date


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
    expense_data = {
    "merchant": "Walmart",
    "amount": 200.00,
    "category": "Groceries"
}
    response = client.post("/expenses", json=expense_data)
    assert response.status_code == 201
    created_expense = response.json()
    assert created_expense["expense_date"] == date.today().isoformat()
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
    expense_data = {
    "merchant": "Chick Fil A",
    "amount": 10.00,
    "category": "Fast Food"
    }
    post_response = client.post("/expenses",json=expense_data)
    created_expense = post_response.json()
    expense_id = created_expense["id"]
    get_response = client.get(f"/expenses/{expense_id}")
    returned_expense = get_response.json()
    assert returned_expense["merchant"] == expense_data["merchant"]
    assert returned_expense["amount"] == expense_data["amount"]
    assert returned_expense["category"] == expense_data["category"]

def test_get_nonexistent_expense():
    expense_id = 999
    get_response = client.get(f"/expenses/{expense_id}")
    error_data = get_response.json()
    assert get_response.status_code == 404
    assert error_data["detail"] == "Expense not found"

def test_update_expense():
    original_data = {
    "merchant": "Taco Bell",
    "amount": 15.00,
    "category": "Fast Food"
    }

    post_response = client.post("/expenses", json=original_data)
    created_expense = post_response.json()
    expense_id = created_expense["id"]
    
    updated_data = {
        "merchant": "KFC",
        "amount": 16.00,
        "category": "Fast Food"
        }
    
    put_response = client.put(
        f"/expenses/{expense_id}",
        json= updated_data
    )

    assert put_response.status_code == 200

    returned_expense = put_response.json()
    assert returned_expense["merchant"] ==  updated_data["merchant"]
    assert returned_expense["amount"] ==  updated_data["amount"]
    assert returned_expense["category"] ==  updated_data["category"]
    assert returned_expense["id"] == expense_id

def test_expense_delete():
    original_data = {
    "merchant": "Popeyes",
    "amount": 21.00,
    "category": "Fast Food"
    }
     
    post_response = client.post("/expenses", json=original_data)
    created_expense = post_response.json()

    created_id = created_expense["id"]

    delete_response = client.delete(f"/expenses/{created_id}")
    assert delete_response.status_code == 200

    delete_data = delete_response.json()
    assert delete_data["message"] == "Expense deleted"

    get_response = client.get(f"/expenses/{created_id}")

    assert get_response.status_code == 404

def test_expense_total():
    expense_one_data = {
    "merchant": "Popeyes",
    "amount": 21.00,
    "category": "Fast Food"
    }

    expense_two_data = {
    "merchant": "KFC",
    "amount": 16.00,
    "category": "Fast Food"
    }

    first_response = client.post("/expenses", json=expense_one_data)
    second_response = client.post("/expenses", json=expense_two_data)

    get_total = client.get("/expenses/total")
    created_total = get_total.json()
    
    assert get_total.status_code == 200
    original_data_total = expense_one_data["amount"]+ expense_two_data["amount"]
    assert  original_data_total == created_total["total"]

def test_expense_total_by_category():
    expense_one_data = {
    "merchant": "Popeyes",
    "amount": 21.00,
    "category": "Fast Food"
    }

    expense_two_data = {
    "merchant": "KFC",
    "amount": 23.00,
    "category" : "Fast Food"
    }

    expense_three_data = {
    "merchant": "Walmart",
    "amount": 100.00,
    "category": "Groceries"
    }

    first_expense_response = client.post("/expenses", json=expense_one_data)
    second_expense_response = client.post("/expenses", json=expense_two_data)
    third_expense_response = client.post("/expenses", json=expense_three_data)

    total_response = client.get("/expenses/total?category=Fast Food")

    assert total_response.status_code == 200
    total_data = total_response.json()



    assert total_data["total"] == expense_one_data["amount"] + expense_two_data["amount"]

def test_get_expenses_by_category():
    expense_one_data = {
    "merchant": "Popeyes",
    "amount": 21.00,
    "category": "Fast Food"
    }

    expense_two_data = {
    "merchant": "KFC",
    "amount": 23.00,
    "category" : "Fast Food"
    }

    expense_three_data = {
    "merchant": "Walmart",
    "amount": 100.00,
    "category": "Groceries"
    }

    first_expense_response = client.post("/expenses", json=expense_one_data)
    second_expense_response = client.post("/expenses", json=expense_two_data)
    third_expense_response = client.post("/expenses", json=expense_three_data)

    filtered_response = client.get("/expenses?category=fast food")

    assert filtered_response.status_code == 200

    filtered_data = filtered_response.json()

    assert len(filtered_data) == 2
    assert all(
        expense["category"].lower() == "fast food"
        for expense in filtered_data
    )

def test_update_nonexistent_expense():
    updated_data = {
        "merchant": "KFC",
        "amount": 16.00,
        "category": "Fast Food"
        }

    put_response = client.put("/expenses/999", json=updated_data)

    error_data = put_response.json()
    assert put_response.status_code == 404
    assert error_data["detail"] == "Expense not found"

def test_delete_nonexistent_expense():
    delete_response = client.delete("/expenses/999")

    error_data = delete_response.json()
    assert delete_response.status_code == 404
    assert error_data["detail"] == "Expense not found"

def test_create_expense_with_data():
    expense_data = {
    "merchant": "Burger King",
    "amount": 25.00,
    "category": "Fast Food",
    "expense_date": "2026-06-15"
    }

    create_response = client.post("/expenses", json=expense_data)
    assert create_response.status_code == 201 
    response_data = create_response.json()
    assert response_data["expense_date"] == "2026-06-15"

def test_create_expense_with_invalid_date():
    expense_data = {
    "merchant": "Burger King",
    "amount": 25.00,
    "category": "Fast Food",
    "expense_date": "2026-13-40"
    }

    post_response = client.post("/expenses",json=expense_data)

    post_data = post_response.json()
    assert post_response.status_code == 422
    assert post_data["detail"] is not None

def test_get_expenses_by_date():
    expense_one_data ={
    "merchant": "Burger King",
    "amount": 25.00,
    "category": "Fast Food",
    "expense_date": "2026-06-15"
    }

    expense_two_data = {
    "merchant": "Popeyes",
    "amount": 21.00,
    "category": "Fast Food",
    "expense_date": "2026-06-15"
    }

    expense_three_data = {
    "merchant": "KFC",
    "amount": 16.00,
    "category": "Fast Food",
    "expense_date": "2026-06-16"
    }

    first_post_response = client.post("/expenses",json=expense_one_data)
    second_post_response = client.post("/expenses",json=expense_two_data)
    second_post_response = client.post("/expenses",json=expense_three_data)

    filtered_response = client.get("/expenses?expense_date=2026-06-15")

    filtered_response_data = filtered_response.json()
    
    assert filtered_response.status_code == 200
    assert len(filtered_response_data) == 2

    assert all(
        expenses["expense_date"] == "2026-06-15"
       for expenses in filtered_response_data
    )

def test_expense_total_by_date():
    expense_one_data ={
    "merchant": "Burger King",
    "amount": 25.00,
    "category": "Fast Food",
    "expense_date": "2026-06-15"
    }

    expense_two_data = {
    "merchant": "Popeyes",
    "amount": 21.00,
    "category": "Fast Food",
    "expense_date": "2026-06-15"
    }

    expense_three_data = {
    "merchant": "KFC",
    "amount": 16.00,
    "category": "Fast Food",
    "expense_date": "2026-06-16"
    }
    
    first_post_response = client.post("/expenses",json=expense_one_data)
    second_post_response = client.post("/expenses",json=expense_two_data)
    third_post_response = client.post("/expenses",json=expense_three_data)

    get_total_filtered = client.get("/expenses/total?expense_date=2026-06-15")

    total_filtered_data = get_total_filtered.json()

    assert get_total_filtered.status_code == 200
    assert total_filtered_data["total"] == expense_one_data["amount"] + expense_two_data["amount"] 

def test_expense_total_by_category_and_date():
    expense_one_data ={
    "merchant": "Burger King",
    "amount": 25.00,
    "category": "Fast Food",
    "expense_date": "2026-06-15"
    }

    expense_two_data = {
    "merchant": "Walmart",
    "amount": 150.00,
    "category": "Groceries",
    "expense_date": "2026-06-16"
    }

    expense_three_data = {
    "merchant": "Popeyes",
    "amount": 21.00,
    "category": "Fast Food",
    "expense_date": "2026-06-15"
    }

    first_post_response = client.post("/expenses",json=expense_one_data)
    second_post_response = client.post("/expenses",json=expense_two_data)
    third_post_response = client.post("/expenses",json=expense_three_data)

    get_total_filtered_category_date = client.get("/expenses/total?category=Fast Food&expense_date=2026-06-15")

    total_filtered_category_date = get_total_filtered_category_date.json()

    assert get_total_filtered_category_date.status_code == 200
    assert total_filtered_category_date["total"] == expense_one_data["amount"] + expense_three_data["amount"]
    
def test_get_expenses_by_category_and_date():
    expense_one_data ={
    "merchant": "Burger King",
    "amount": 25.00,
    "category": "Fast Food",
    "expense_date": "2026-06-15"
    }

    expense_two_data = {
    "merchant": "Chick Fil A",
    "amount": 16.50,
    "category": "Fast Food",
    "expense_date": "2026-06-16"
    }

    expense_three_data = {
    "merchant": "Popeyes",
    "amount": 21.00,
    "category": "Fast Food",
    "expense_date": "2026-06-15"
    }

    expense_four_data = {
    "merchant": "Taco Bell",
    "amount": 15.00,
    "category": "Fast Food",
    "expense_date": "2026-06-15"
    }

    expense_five_data = {
    "merchant": "Walmart",
    "amount": 150.00,
    "category": "Groceries",
    "expense_date": "2026-06-15"
    }

    first_post_response = client.post("/expenses",json=expense_one_data)
    second_post_response = client.post("/expenses",json=expense_two_data)
    third_post_response = client.post("/expenses",json=expense_three_data)
    fourth_post_response = client.post("/expenses",json=expense_four_data)
    fifth_post_response = client.post("/expenses",json=expense_five_data)

    get_response = client.get("/expenses?category=fast food&expense_date=2026-06-15")

    get_filtered_data_by_date_and_category = get_response.json()

    assert get_response.status_code == 200
    assert len(get_filtered_data_by_date_and_category) == 3
    assert all(
        expense["expense_date"] == "2026-06-15" and expense["category"].lower() == "fast food"
        for expense in get_filtered_data_by_date_and_category
    )

    





    











    



    




      


    



    