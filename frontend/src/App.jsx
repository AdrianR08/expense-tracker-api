import './App.css'
import { useEffect, useState } from 'react'
import { House, Coins, BookCopy, Scroll, Settings, Wallet } from 'lucide-react';
import {
  PieChart,
  Pie,
  ResponsiveContainer,
  Tooltip,
  Legend,
  Cell,
  Label
} from 'recharts'




function App() {
  const [expenses, setExpenses] = useState([])

  const [merchant, setMerchant] = useState([])

  const [category, setCategory] = useState([])

  const [amount, setAmount] = useState([])

  const localDate = new Date()

  const todayDate = new Intl.DateTimeFormat('sv-SE').format(localDate)

  const [expense_date, setDate] = useState(todayDate);

  const [overviewPeriod, setOverviewPeriod] = useState('thisMonth')

  let filteredExpenses = expenses

  if (overviewPeriod === 'thisMonth') {
    filteredExpenses = expenses.filter((expense) => {
      const expenseDate = new Date(`${expense.expense_date}T00:00:00`)

      return (
        expenseDate.getMonth() === localDate.getMonth() &&
        expenseDate.getFullYear() === localDate.getFullYear()
      )
    })
  }

  if (overviewPeriod === 'lastMonth') {
    const lastMonthDate = new Date(localDate)
    lastMonthDate.setMonth(localDate.getMonth() - 1)

    filteredExpenses = expenses.filter((expense) => {
      const expenseDate = new Date(`${expense.expense_date}T00:00:00`)
      return (
        expenseDate.getMonth() === lastMonthDate.getMonth() &&
        expenseDate <= localDate
      )
    }
    )
  }

  if (overviewPeriod === 'lastThreeMonth') {

    const lastThreeMonthDate = new Date(localDate)
    lastThreeMonthDate.setMonth(localDate.getMonth() - 3)

    filteredExpenses = expenses.filter((expense) => {
      const expenseDate = new Date(`${expense.expense_date}T00:00:00`)
      return (
        expenseDate >= lastThreeMonthDate &&
        expenseDate <= localDate
      )
    }
    )
  }

  if (overviewPeriod === 'lastSixMonth') {

    const lastSixMonthDate = new Date(localDate)
    lastSixMonthDate.setMonth(localDate.getMonth() - 6)

    filteredExpenses = expenses.filter((expense) => {
      const expenseDate = new Date(`${expense.expense_date}T00:00:00`)
      return (
        expenseDate >= lastSixMonthDate &&
        expenseDate <= localDate
      )
    }
    )
  }

  if (overviewPeriod === 'thisYear') {
    filteredExpenses = expenses.filter((expense) => {
      const expenseDate = new Date(`${expense.expense_date}T00:00:00`)
      return (
        expenseDate.getFullYear() === localDate.getFullYear()
      )
    }
    )
  }

  const testitems = () => {
    {
      return filteredExpenses.length === 0 ? (
        <div className="no-items">
          No expenses during this period
        </div>
      ) : (
        <div className="overview-content">
          <div className='donut-container'>
            <ResponsiveContainer width={'100%'} height={250}>
              <PieChart>
                <Tooltip formatter={(amount) => {
                  return '$' + amount.toFixed(2)
                }}></Tooltip>

                <Pie stroke='none' innerRadius={65} data={chartData} outerRadius={125}
                  dataKey={'amount'} nameKey={'category'} labelLine={false} label={({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {

                    const radius = innerRadius + (outerRadius - innerRadius) / 2
                    const RADIAN = Math.PI / 180
                    const x = cx + radius * Math.cos(-midAngle * RADIAN)
                    const y = cy + radius * Math.sin(-midAngle * RADIAN)
                    return <text className='text-chart'
                      x={x}
                      y={y}
                      textAnchor="middle"
                      dominantBaseline="central"
                      fill='white'
                      fontWeight='bold'
                    >
                      {(percent * 100).toFixed(0)}%
                    </text>
                  }}
                >{chartData.map((entry) => (
                  <Cell fill={categoryColors[entry.category]} key={entry.category}></Cell>
                ))}
                  <Label
                    value="Total"
                    position="center"
                    dy={12}
                    fill="white"
                    opacity='75%'
                  />
                  <Label
                    value={`$${totalAmount.toFixed(2)}`}
                    position="center"
                    dy={-10}
                    fill="white"
                    fontWeight='bold'
                  />
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className='legend-box'>
            <CustomLegend />
          </div>
        </div>

      )
    }
  }


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

    if (response.ok) {
      setMerchant('')
      setCategory('')
      setAmount('')
      setDate(todayDate)
    }

    const createdExpenses = await response.json()

    setExpenses([createdExpenses, ...expenses])
  }

  useEffect(() => {
    fetch('http://127.0.0.1:8000/expenses')
      .then((response) => response.json())
      .then((data) => setExpenses(data))
  }, [])

  const categoryTotals = {}


  filteredExpenses.forEach((expense) => {
    if (categoryTotals[expense.category]) {
      categoryTotals[expense.category] += Number(expense.amount)
    } else {
      categoryTotals[expense.category] = Number(expense.amount)
    }
  })

  let totalAmount = 0

  filteredExpenses.forEach((expense) => {
    totalAmount += Number(expense.amount)
  })


  let allExpenses = expenses

  allExpenses = expenses.filter((expense) => {
    const expenseDate = new Date(`${expense.expense_date}T00:00:00`)
    return (
      expenseDate.getFullYear() === localDate.getFullYear()
    )
  }
  )

  let sumAmount = 0

  allExpenses.forEach((expense) => {
    sumAmount += expense.amount
  }
  )


  const chartData = Object.entries(categoryTotals).map((entry) => {
    const categoryAmount = {
      'category': entry[0],
      'amount': entry[1],
      'percentage': ((entry[1] / totalAmount) * 100).toFixed(2)
    }
    return categoryAmount
  })


  const categoryColors = {
    Housing: '#4F8CFF',
    Transportation: '#FFB347',
    Food: '#35D07F',
    Utilities: '#38C6E8',
    Clothing: '#D46BFF',
    'Medical/Healthcare': '#FF6262',
    Insurance: '#3BA7E8',
    'Household Items/Supplies': '#A6D94A',
    Personal: '#FF6FAE',
    Debt: '#FF8A3D',
    Retirement: '#25C28A',
    Education: '#737BFF',
    Savings: '#2ECDB3',
    'Gifts/Donations': '#FF6685',
    Entertainment: '#9B6BFF',
    Other: '#8293AA'
  }



  const CustomLegend = (props) => {
    return (
      <div>
        {chartData.map((item, index) => (
          <div key={index} className="legend-row">
            <span className='color-category' style={{ backgroundColor: categoryColors[chartData[index].category]
            }}></span>
            <span>{chartData[index].category}</span>
            <span>${chartData[index].amount.toFixed(2)}</span>
          </div>
          
        ))}
      </div>
    )
   
  }


  return (
    <main>
      <div className='background'>
        <div className='first-column'>

          <button className='button-nav'> <House className='nav-icon' />
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

          <section className='summary-section'>
            <div className='expense-card total-expenses'>
              <div className='wallet-icon'>
                <Wallet stroke='lightgreen' size={30} />
              </div>
              <text>Total Expenses</text>
              <text className='text-main-card'>${sumAmount.toFixed(2)}</text>
              <text>This month</text>
            </div>

            <div className='expense-card average-day'>

            </div>

            <div className='expense-card top-category'>

            </div>

            <div className='expense-card transctions'>

            </div>


          </section>


          <section className='chart-card'>
            <div className='overview'>
              <div className='overview-top'>
                <h2 className="expense-overview-header">Overview</h2>
                <select className='select-menu-overview' value={overviewPeriod}
                  onChange={(e) => setOverviewPeriod(e.target.value)}>
                  <option value='thisMonth'>This Month</option>
                  <option value='lastMonth'>Last Month</option>
                  <option value='lastThreeMonth'>Last 3 Months</option>
                  <option value='lastSixMonth'>Last 6 Months</option>
                  <option value='thisYear'>This Year</option>
                  <option value='allTime'>All Time</option>
                </select>
              </div>
              {testitems()}
            </div>

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
      </div >
    </main >
  )
}

export default App
