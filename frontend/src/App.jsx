import './App.css'
import { useEffect, useState } from 'react'


function App() {
  const [expenses, setExpenses] = useState([])

  useEffect(() => {
    fetch('http://127.0.0.1:8000/expenses')
    .then((response) => response.json())
    .then((data) => setExpenses(data))
  }, [])

  console.log(expenses)
  return (
    <main>
      <h1>Expense Tracker</h1>
      <p>Track and understand your spending.</p>

      <section className="expense-card">

        <div className="expense-card-header">
          <h2 className="expense-card-title">Recent Expenses</h2>
        </div>
        <ul>
          {expenses.map((expense) => (
            <li className="expense-item" key={expense.id}>
              <div className="expense-details">
                <div className="expense-merchant">{expense.merchant}</div>
                 <div className="expense-info">
                <div className="expense-category">{expense.category}</div>
                <p>•</p>
                <div className="expense-date">{new Date(`${expense.expense_date}T00:00:00`).toLocaleDateString(
                  "en-US",
                  {
                    month: "long",
                    day: "numeric",
                    year: "numeric",
                  }
                )}</div>
                </div>
              </div>
              <div className="expense-amount">${expense.amount.toFixed(2)}</div>
              </li>
          ))}

        </ul>

        <button className="expense-card-button">View All</button>
      </section>

    </main>
  )
}

export default App
