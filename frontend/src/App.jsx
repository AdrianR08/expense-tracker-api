import './App.css'
import { useEffect, useState } from 'react'
import { House, Coins, BookCopy , Scroll, Settings} from 'lucide-react';
import {
  PieChart,
  Pie,
  ResponsiveContainer,
  Tooltip
} from 'recharts'


function App() {
  const [expenses, setExpenses] = useState([])

  const [merchant, setMerchant] = useState([])

  const [category, setCategory] = useState([])

  const [amount, setAmount] = useState([])

  const localDate = new Date()

  const todayDate = new Intl.DateTimeFormat('sv-SE').format(localDate)

  const [expense_date, setDate] = useState(todayDate);

  async function handleSubmit(event) {
    event.preventDefault()

    const newExpense = {
      merchant,
      category,
      amount,
      expense_date,
    }

    const response = await fetch('http://127.0.0.1:8000/expenses', {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(newExpense)
    })

    const createdExpenses = await response.json()

    setExpenses([createdExpenses, ...expenses])
  }

  useEffect(() => {
    fetch('http://127.0.0.1:8000/expenses')
      .then((response) => response.json())
      .then((data) => setExpenses(data))
  }, [])



  return (
    <main>
      <div className='background'>
        <div className='first-column'>

          <button className='button-nav'> <House className='nav-icon'/>
            Dashboard</button>

          <button className='button-nav'> <Coins className='nav-icon' />Expenses</button>

          <button className='button-nav'><BookCopy className='nav-icon' />Categories</button>

          <button className='button-nav'><Scroll className='nav-icon' />Summary</button>

          <button className='button-nav'><Settings />Settings</button>

        </div>

        <div className='second-column'>
          <div className='header'>
            <h1>Expenses</h1>
            <p>Track and understand your spending.</p>
          </div>

          <section className='overview'>
            

          </section>
          <div className='expenses-lists'>
            <section className="expense-card">
              <div className="expense-card-header">
                <h2>Recent Expenses</h2>
              </div>

              <div className='list-items'>
                <ul>
                  {[...expenses].sort((a, b) => new Date(b.expense_date) - new Date(a.expense_date)).slice(0, 4).map((expense) => (
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
                          )}
                          </div>
                        </div>
                      </div>
                      <div className="expense-amount">
                        ${expense.amount.toFixed(2)}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
              <button className="expense-card-button">View All Expenses</button>

            </section>

            <section className='add-expense-card'>
              <div className='expense-card-header'>
                <h2>Add Expense</h2>
              </div>
              <form className='form-style' onSubmit={handleSubmit}>

                <div className='add-merchant-item'>

                  <h2 className='sub-header'>Merchant *</h2>

                  <input type='text' className='input-merchant' placeholder='eg. Starbucks' required value={merchant}
                    onChange={(e) => setMerchant(e.target.value)}></input>
                </div>

                <div>

                  <h2 className='sub-header'>Category *</h2>

                  <select className='select-menu' required value={category} onChange={(e) => setCategory(e.target.value)}>
                    <option value='' disabled>
                      Select a category
                    </option>
                    <option className='menu-options'>Housing</option>
                    <option className='menu-options'>Transportation</option>
                    <option className='menu-options'>Food</option>
                    <option className='menu-options'>Utilities</option>
                    <option className='menu-options'>Clothing</option>
                    <option className='menu-options'>Medical/Healthcare</option>
                    <option className='menu-options'>Insurance</option>
                    <option className='menu-options'>Household Items/Supplies</option>
                    <option className='menu-options'>Personal</option>
                    <option className='menu-options'>Debt</option>
                    <option className='menu-options'>Retirement</option>
                    <option className='menu-options'>Education</option>
                    <option className='menu-options'>Savings</option>
                    <option className='menu-options'>Gifts/Donations</option>
                    <option className='menu-options'>Entertainment</option>
                    <option className='menu-options'>Other</option>
                  </select>
                </div>

                <div>
                  <h2 className='sub-header'>Amount *</h2>
                  <div className='add-amount-item'>
                    <div className='text-symbol'>
                      <p className='dollar-symbol'>$</p>
                    </div>
                    <input className='input-amount' placeholder='0.00' type='number' required value={amount}
                      onChange={(e) => setAmount(e.target.value)}></input>
                  </div>
                </div>

                <div>
                  <h2 className='sub-header'>Date *</h2>
                  <div className='add-date-item'>
                    <input className='date-input' type='date' value={expense_date} required onChange={(e) => setDate(e.target.value)}>
                    </input>
                  </div>
                </div>

                <button className='add-expense-button' value='Submit' >Add Expense</button>

              </form>
            </section>
          </div>
        </div>
      </div>
    </main >
  )
}

export default App
