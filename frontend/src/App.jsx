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

      <section>
        <h2>Expenses</h2>
        <ul>
          {expenses.map((expense) => (
            <li className="expense-item" key={expense.id}>
              <div className="expense-details">
                <div className="expense-merchant">{expense.merchant}</div>
                <div className="expense-category">{expense.category}</div>
                <div className="expense-date">{expense.expense_date}</div>
              </div>
              <div className="expense-amount">${expense.amount.toFixed(2)}</div>
              </li>
          ))}

        </ul>
      </section>

    </main>
  )
}

export default App
