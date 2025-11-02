import streamlit as st
import pandas as pd
import json
import datetime
from datetime import datetime, timedelta
import io
import base64
import tempfile
import os
import sqlite3
import uuid
from PIL import Image

# Try to import plotly with fallback
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly not available. Using alternative visualizations.")

# Try to import fpdf with fallback
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    st.warning("FPDF not available. PDF generation disabled.")

# Set page configuration
st.set_page_config(
    page_title="HMD Solutions - Business Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for attractive styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1rem;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border-left: 5px solid #667eea;
        transition: transform 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
    }
    .positive {
        color: #10b981;
        font-weight: bold;
        font-size: 1.1em;
    }
    .negative {
        color: #ef4444;
        font-weight: bold;
        font-size: 1.1em;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        margin: 0.5rem;
    }
    .footer {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        color: white;
        padding: 2rem;
        text-align: center;
        margin-top: 3rem;
        border-radius: 15px;
    }
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    .tab-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    .edit-btn {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        margin-right: 0.5rem;
    }
    .delete-btn {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    }
    .quick-action-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        width: 100%;
        margin: 0.5rem 0;
    }
    .quick-action-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Database setup for persistent storage
def init_database():
    conn = sqlite3.connect('hmd_solutions.db')
    c = conn.cursor()

    # Create employees table
    c.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            initial_balance REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create transactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            employee_id TEXT,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    ''')

    # Create expenses table
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            employee_name TEXT,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect('hmd_solutions.db')

class EmployeeLedger:
    def __init__(self):
        init_database()

    def add_employee(self, name, initial_balance=0):
        conn = get_db_connection()
        c = conn.cursor()

        employee_id = str(uuid.uuid4())
        c.execute(
            'INSERT INTO employees (id, name, initial_balance) VALUES (?, ?, ?)',
            (employee_id, name, initial_balance)
        )

        # Add initial transaction if balance is not zero
        if initial_balance != 0:
            transaction_id = str(uuid.uuid4())
            transaction_type = 'payment' if initial_balance > 0 else 'expense'
            c.execute(
                '''INSERT INTO transactions (id, employee_id, type, amount, description, date) 
                VALUES (?, ?, ?, ?, ?, ?)''',
                (transaction_id, employee_id, transaction_type, abs(initial_balance),
                 "Initial balance", datetime.now().date().isoformat())
            )

        conn.commit()
        conn.close()

    def update_employee(self, employee_id, name, initial_balance=0):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            'UPDATE employees SET name = ?, initial_balance = ? WHERE id = ?',
            (name, initial_balance, employee_id)
        )
        conn.commit()
        conn.close()

    def add_transaction(self, employee_id, type, amount, description, date):
        conn = get_db_connection()
        c = conn.cursor()

        transaction_id = str(uuid.uuid4())
        c.execute(
            '''INSERT INTO transactions (id, employee_id, type, amount, description, date) 
            VALUES (?, ?, ?, ?, ?, ?)''',
            (transaction_id, employee_id, type, float(amount), description, date)
        )

        conn.commit()
        conn.close()

    def update_transaction(self, transaction_id, type, amount, description, date):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            '''UPDATE transactions SET type = ?, amount = ?, description = ?, date = ? 
            WHERE id = ?''',
            (type, float(amount), description, date, transaction_id)
        )
        conn.commit()
        conn.close()

    def get_employees(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM employees ORDER BY created_at DESC')
        employees = [{'id': row[0], 'name': row[1], 'initial_balance': row[2], 'created_at': row[3]}
                     for row in c.fetchall()]
        conn.close()
        return employees

    def get_employee(self, employee_id):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM employees WHERE id = ?', (employee_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'name': row[1], 'initial_balance': row[2], 'created_at': row[3]}
        return None

    def get_transaction(self, transaction_id):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'employee_id': row[1], 'type': row[2], 'amount': row[3],
                    'description': row[4], 'date': row[5], 'created_at': row[6]}
        return None

    def get_transactions(self, employee_id=None, start_date=None, end_date=None):
        conn = get_db_connection()
        c = conn.cursor()

        query = 'SELECT * FROM transactions'
        params = []

        if employee_id or start_date or end_date:
            query += ' WHERE'
            conditions = []

            if employee_id:
                conditions.append(' employee_id = ?')
                params.append(employee_id)

            if start_date:
                conditions.append(' date >= ?')
                params.append(start_date)

            if end_date:
                conditions.append(' date <= ?')
                params.append(end_date)

            query += ' AND'.join(conditions)

        query += ' ORDER BY date DESC'
        c.execute(query, params)

        transactions = [{'id': row[0], 'employee_id': row[1], 'type': row[2], 'amount': row[3],
                         'description': row[4], 'date': row[5], 'created_at': row[6]}
                        for row in c.fetchall()]
        conn.close()
        return transactions

    def get_employee_balance(self, employee_id):
        transactions = self.get_transactions(employee_id)
        employee_transactions = [t for t in transactions if t['employee_id'] == employee_id]
        total_expenses = sum(t['amount'] for t in employee_transactions if t['type'] == 'expense')
        total_payments = sum(t['amount'] for t in employee_transactions if t['type'] == 'payment')
        return total_expenses - total_payments

    def get_employee_summary(self, employee_id, start_date=None, end_date=None):
        transactions = self.get_transactions(employee_id, start_date, end_date)
        employee_transactions = [t for t in transactions if t['employee_id'] == employee_id]
        total_expenses = sum(t['amount'] for t in employee_transactions if t['type'] == 'expense')
        total_payments = sum(t['amount'] for t in employee_transactions if t['type'] == 'payment')
        balance = total_expenses - total_payments

        return {
            'total_expenses': total_expenses,
            'total_payments': total_payments,
            'balance': balance
        }

    def delete_transaction(self, transaction_id):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        conn.commit()
        conn.close()

    def delete_employee(self, employee_id):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
        c.execute('DELETE FROM transactions WHERE employee_id = ?', (employee_id,))
        conn.commit()
        conn.close()

class ExpenseTracker:
    def __init__(self):
        init_database()

    def add_expense(self, expense_type, description, amount, employee_name, date):
        conn = get_db_connection()
        c = conn.cursor()

        expense_id = str(uuid.uuid4())
        c.execute(
            '''INSERT INTO expenses (id, type, description, amount, employee_name, date) 
            VALUES (?, ?, ?, ?, ?, ?)''',
            (expense_id, expense_type, description, float(amount), employee_name, date)
        )

        conn.commit()
        conn.close()

    def update_expense(self, expense_id, expense_type, description, amount, employee_name, date):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            '''UPDATE expenses SET type = ?, description = ?, amount = ?, employee_name = ?, date = ? 
            WHERE id = ?''',
            (expense_type, description, float(amount), employee_name, date, expense_id)
        )
        conn.commit()
        conn.close()

    def get_expense(self, expense_id):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'type': row[1], 'description': row[2], 'amount': row[3],
                    'employee_name': row[4], 'date': row[5], 'created_at': row[6]}
        return None

    def get_expenses(self, expense_type=None, start_date=None, end_date=None, employee_name=None):
        conn = get_db_connection()
        c = conn.cursor()

        query = 'SELECT * FROM expenses'
        params = []

        conditions = []
        if expense_type and expense_type != 'all':
            conditions.append(' type = ?')
            params.append(expense_type)

        if start_date:
            conditions.append(' date >= ?')
            params.append(start_date)

        if end_date:
            conditions.append(' date <= ?')
            params.append(end_date)

        if employee_name:
            conditions.append(' employee_name LIKE ?')
            params.append(f'%{employee_name}%')

        if conditions:
            query += ' WHERE' + ' AND'.join(conditions)

        query += ' ORDER BY date DESC'
        c.execute(query, params)

        expenses = [{'id': row[0], 'type': row[1], 'description': row[2], 'amount': row[3],
                     'employee_name': row[4], 'date': row[5], 'created_at': row[6]}
                    for row in c.fetchall()]
        conn.close()
        return expenses

    def delete_expense(self, expense_id):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
        conn.close()

    def get_summary(self, start_date=None, end_date=None):
        expenses = self.get_expenses(start_date=start_date, end_date=end_date)
        company_expenses = sum(e['amount'] for e in expenses if e['type'] == 'company')
        employee_expenses = sum(e['amount'] for e in expenses if e['type'] == 'employee')
        total_expenses = company_expenses + employee_expenses

        return {
            'company_total': company_expenses,
            'employee_total': employee_expenses,
            'grand_total': total_expenses
        }

def main():
    st.markdown('<div class="main-header">HMD Solutions - Business Management System</div>', unsafe_allow_html=True)

    # Initialize systems
    ledger = EmployeeLedger()
    expense_tracker = ExpenseTracker()

    # Sidebar navigation
    st.sidebar.markdown("""
    <div style='background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center;'>
        <h2>🚀 Navigation</h2>
    </div>
    """, unsafe_allow_html=True)

    app_mode = st.sidebar.selectbox(
        "Choose Application",
        ["🏠 Dashboard", "👥 Employee Ledger", "💰 Expense Management", "📊 Reports & Analytics", "📁 Data Management"]
    )

    # Footer in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='text-align: center; color: #666;'>
        <h4>DatanexSolution</h4>
        <p>For any query please feel free to contact:</p>
        <p><strong>+92-3207429422</strong></p>
    </div>
    """, unsafe_allow_html=True)

    if app_mode == "🏠 Dashboard":
        render_dashboard(ledger, expense_tracker)
    elif app_mode == "👥 Employee Ledger":
        render_employee_ledger(ledger)
    elif app_mode == "💰 Expense Management":
        render_expense_dashboard(expense_tracker, ledger)
    elif app_mode == "📊 Reports & Analytics":
        render_reports_analytics(ledger, expense_tracker)
    else:
        render_data_management(ledger, expense_tracker)

def render_dashboard(ledger, expense_tracker):
    st.markdown('<div class="sub-header">📊 Business Dashboard</div>', unsafe_allow_html=True)

    # Quick stats
    employees = ledger.get_employees()
    transactions = ledger.get_transactions()
    expenses = expense_tracker.get_expenses()
    expense_summary = expense_tracker.get_summary()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f'<div class="metric-card">Total Employees<br>{len(employees)}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card">Total Transactions<br>{len(transactions)}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card">Company Expenses<br>PKR {expense_summary["company_total"]:.2f}</div>',
                    unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card">Employee Expenses<br>PKR {expense_summary["employee_total"]:.2f}</div>',
                    unsafe_allow_html=True)

    # Recent activity
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👥 Recent Employees")
        if employees:
            for emp in employees[:5]:
                balance = ledger.get_employee_balance(emp['id'])
                balance_text = f"PKR {abs(balance):.2f} {'(Due)' if balance > 0 else '(Advance)' if balance < 0 else ''}"
                st.write(f"**{emp['name']}** - {balance_text}")
        else:
            st.info("No employees added yet")

    with col2:
        st.markdown("### 💰 Recent Expenses")
        if expenses:
            for exp in expenses[:5]:
                type_icon = "🏢" if exp['type'] == 'company' else "👤"
                st.write(f"{type_icon} **{exp['description']}** - PKR {exp['amount']:.2f} ({exp['date']})")
        else:
            st.info("No expenses recorded yet")

    # Quick actions - FIXED
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("➕ Add New Employee", use_container_width=True, key="quick_add_emp"):
            st.session_state.quick_action = "add_employee"
            st.rerun()

    with col2:
        if st.button("💸 Record Transaction", use_container_width=True, key="quick_add_trans"):
            st.session_state.quick_action = "add_transaction"
            st.rerun()

    with col3:
        if st.button("💰 Add Expense", use_container_width=True, key="quick_add_exp"):
            st.session_state.quick_action = "add_expense"
            st.rerun()

    with col4:
        if st.button("📊 View Reports", use_container_width=True, key="quick_reports"):
            st.session_state.quick_action = "view_reports"
            st.rerun()

    # Handle quick actions
    if st.session_state.get('quick_action') == "add_employee":
        st.markdown("---")
        st.markdown("### ➕ Quick Add Employee")
        with st.form("quick_employee_form", clear_on_submit=True):
            emp_name = st.text_input("Employee Name")
            initial_balance = st.number_input("Initial Balance (PKR)", value=0.0, step=100.0)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Add Employee", use_container_width=True):
                    if emp_name:
                        ledger.add_employee(emp_name, initial_balance)
                        st.success(f"Employee {emp_name} added successfully!")
                        st.session_state.quick_action = None
                        st.rerun()
                    else:
                        st.error("Please enter employee name")
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.quick_action = None
                    st.rerun()

    elif st.session_state.get('quick_action') == "add_transaction":
        st.markdown("---")
        st.markdown("### 💸 Quick Record Transaction")
        employees = ledger.get_employees()
        if employees:
            with st.form("quick_transaction_form", clear_on_submit=True):
                employee_options = {emp['name']: emp['id'] for emp in employees}
                selected_emp = st.selectbox("Employee", list(employee_options.keys()))
                transaction_type = st.selectbox("Transaction Type", ["Expense (Debit)", "Payment (Credit)"])
                amount = st.number_input("Amount (PKR)", min_value=0.0, step=100.0)
                description = st.text_input("Description")
                date = st.date_input("Date", value=datetime.now())
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Record Transaction", use_container_width=True):
                        emp_id = employee_options[selected_emp]
                        type_code = 'expense' if 'Expense' in transaction_type else 'payment'
                        ledger.add_transaction(emp_id, type_code, amount, description, date.isoformat())
                        st.success("Transaction recorded successfully!")
                        st.session_state.quick_action = None
                        st.rerun()
                with col2:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.quick_action = None
                        st.rerun()
        else:
            st.info("No employees available. Please add employees first.")
            if st.button("OK", use_container_width=True):
                st.session_state.quick_action = None
                st.rerun()

    elif st.session_state.get('quick_action') == "add_expense":
        st.markdown("---")
        st.markdown("### 💰 Quick Add Expense")
        with st.form("quick_expense_form", clear_on_submit=True):
            expense_type = st.radio("Expense Type", ["Company", "Employee"])
            description = st.text_input("Description")
            amount = st.number_input("Amount (PKR)", min_value=0.0, step=100.0)

            employee_name = None
            if expense_type == "Employee":
                employees = ledger.get_employees()
                if employees:
                    employee_options = [emp['name'] for emp in employees]
                    employee_name = st.selectbox("Employee", employee_options)
                else:
                    st.info("No employees available.")
                    employee_name = st.text_input("Or enter employee name")

            date = st.date_input("Date", value=datetime.now())
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Add Expense", use_container_width=True):
                    if description and amount > 0:
                        expense_tracker.add_expense(
                            expense_type.lower(),
                            description,
                            amount,
                            employee_name,
                            date.isoformat()
                        )
                        st.success("Expense added successfully!")
                        st.session_state.quick_action = None
                        st.rerun()
                    else:
                        st.error("Please fill all required fields")
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.quick_action = None
                    st.rerun()

    elif st.session_state.get('quick_action') == "view_reports":
        st.markdown("---")
        st.markdown("### 📊 Quick Reports")
        st.info("Navigate to 'Reports & Analytics' section for detailed reports")
        if st.button("OK", use_container_width=True):
            st.session_state.quick_action = None
            st.rerun()

def render_employee_ledger(ledger):
    st.markdown('<div class="sub-header">👥 Employee Ledger System</div>', unsafe_allow_html=True)
    st.write("Track expenses, payments, and balances for all employees")

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Employee Summary", "➕ Add Employee", "💸 Record Transaction", "📊 Employee Details"])

    with tab1:
        st.markdown("### 📋 Employee Ledger Summary")

        employees = ledger.get_employees()
        if employees:
            # Date range filter for summary
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30),
                                           key="emp_summary_start")
            with col2:
                end_date = st.date_input("End Date", value=datetime.now(), key="emp_summary_end")

            for emp in employees:
                with st.container():
                    summary = ledger.get_employee_summary(emp['id'], start_date.isoformat(), end_date.isoformat())

                    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 2, 2])
                    col1.write(f"**{emp['name']}**")
                    col2.write(f"Expenses: PKR {summary['total_expenses']:.2f}")
                    col3.write(f"Payments: PKR {summary['total_payments']:.2f}")

                    balance_color = "negative" if summary['balance'] > 0 else "positive" if summary['balance'] < 0 else ""
                    balance_text = f"PKR {abs(summary['balance']):.2f} {'(Due)' if summary['balance'] > 0 else '(Advance)' if summary['balance'] < 0 else ''}"
                    col4.markdown(f"<div class='{balance_color}'>Balance: {balance_text}</div>", unsafe_allow_html=True)

                    # Action buttons
                    if col5.button("View Details", key=f"view_{emp['id']}"):
                        st.session_state.selected_employee = emp['id']
                        st.session_state.selected_employee_name = emp['name']

                    # Edit and Delete buttons
                    col61, col62 = col6.columns(2)
                    with col61:
                        if st.button("✏️", key=f"edit_{emp['id']}"):
                            st.session_state.editing_employee = emp['id']
                            st.rerun()
                    with col62:
                        if st.button("🗑️", key=f"delete_{emp['id']}"):
                            st.session_state.deleting_employee = emp['id']
                            st.rerun()

                    st.divider()

            # Handle employee editing
            if st.session_state.get('editing_employee'):
                employee_id = st.session_state.editing_employee
                employee = ledger.get_employee(employee_id)
                if employee:
                    st.markdown("---")
                    st.markdown("### ✏️ Edit Employee")
                    with st.form(f"edit_employee_{employee_id}"):
                        name = st.text_input("Employee Name", value=employee['name'])
                        initial_balance = st.number_input("Initial Balance (PKR)", 
                                                         value=float(employee['initial_balance']), 
                                                         step=100.0)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Update Employee", use_container_width=True):
                                if name:
                                    ledger.update_employee(employee_id, name, initial_balance)
                                    st.success(f"Employee {name} updated successfully!")
                                    st.session_state.editing_employee = None
                                    st.rerun()
                                else:
                                    st.error("Please enter employee name")
                        with col2:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                st.session_state.editing_employee = None
                                st.rerun()

            # Handle employee deletion
            if st.session_state.get('deleting_employee'):
                employee_id = st.session_state.deleting_employee
                employee = ledger.get_employee(employee_id)
                if employee:
                    st.markdown("---")
                    st.markdown("### 🗑️ Delete Employee")
                    st.warning(f"Are you sure you want to delete **{employee['name']}**? This action cannot be undone!")
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button("✅ Yes, Delete", use_container_width=True, type="primary"):
                            ledger.delete_employee(employee_id)
                            st.success(f"Employee {employee['name']} deleted successfully!")
                            st.session_state.deleting_employee = None
                            st.rerun()
                    with col2:
                        if st.button("❌ Cancel", use_container_width=True):
                            st.session_state.deleting_employee = None
                            st.rerun()

        else:
            st.info("No employees found. Add employees to see the ledger.")

    with tab2:
        st.markdown("### ➕ Add New Employee")
        with st.form("employee_form", clear_on_submit=True):
            emp_name = st.text_input("Employee Name")
            initial_balance = st.number_input("Initial Balance (PKR)", value=0.0, step=100.0)

            if st.form_submit_button("Add Employee", use_container_width=True):
                if emp_name:
                    ledger.add_employee(emp_name, initial_balance)
                    st.success(f"Employee {emp_name} added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter employee name")

    with tab3:
        st.markdown("### 💰 Record Transaction")
        employees = ledger.get_employees()
        if employees:
            with st.form("transaction_form", clear_on_submit=True):
                employee_options = {emp['name']: emp['id'] for emp in employees}
                selected_emp = st.selectbox("Employee", list(employee_options.keys()))
                transaction_type = st.selectbox("Transaction Type", ["Expense (Debit)", "Payment (Credit)"])
                amount = st.number_input("Amount (PKR)", min_value=0.0, step=100.0)
                description = st.text_input("Description")
                date = st.date_input("Date", value=datetime.now())

                if st.form_submit_button("Record Transaction", use_container_width=True):
                    emp_id = employee_options[selected_emp]
                    type_code = 'expense' if 'Expense' in transaction_type else 'payment'
                    ledger.add_transaction(emp_id, type_code, amount, description, date.isoformat())
                    st.success("Transaction recorded successfully!")
                    st.rerun()
        else:
            st.info("No employees available. Please add employees first.")

    with tab4:
        st.markdown("### 📊 Employee Detailed View")

        employees = ledger.get_employees()
        if employees:
            selected_emp_name = st.selectbox("Select Employee", [emp['name'] for emp in employees],
                                             key="detail_employee_select")

            if selected_emp_name:
                emp_id = next(emp['id'] for emp in employees if emp['name'] == selected_emp_name)

                # Date range for detailed view
                col1, col2 = st.columns(2)
                with col1:
                    detail_start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30),
                                                      key="detail_start")
                with col2:
                    detail_end_date = st.date_input("End Date", value=datetime.now(), key="detail_end")

                show_employee_details(ledger, emp_id, selected_emp_name,
                                      detail_start_date.isoformat(), detail_end_date.isoformat())

def show_employee_details(ledger, employee_id, employee_name, start_date=None, end_date=None):
    st.markdown(f"### 📊 {employee_name} - Detailed Ledger")

    transactions = ledger.get_transactions(employee_id, start_date, end_date)

    if transactions:
        # Sort by date
        transactions.sort(key=lambda x: x['date'])

        # Calculate running balance
        running_balance = 0
        detailed_data = []

        for t in transactions:
            if t['type'] == 'expense':
                running_balance += t['amount']
            else:
                running_balance -= t['amount']

            detailed_data.append({
                'id': t['id'],
                'Date': t['date'],
                'Type': t['type'].title(),
                'Description': t['description'],
                'Amount': t['amount'],
                'Balance': running_balance
            })

        # Display detailed transactions with edit/delete
        for idx, row in enumerate(detailed_data):
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 3, 2, 2, 1, 1])
            col1.write(row['Date'])
            col2.write(row['Type'])
            col3.write(row['Description'])
            col4.write(f"PKR {row['Amount']:.2f}")

            balance_color = "negative" if row['Balance'] > 0 else "positive" if row['Balance'] < 0 else ""
            balance_text = f"PKR {abs(row['Balance']):.2f} {'(Due)' if row['Balance'] > 0 else '(Advance)' if row['Balance'] < 0 else ''}"
            col5.markdown(f"<div class='{balance_color}'>{balance_text}</div>", unsafe_allow_html=True)

            # Edit and Delete buttons for transactions
            if col6.button("✏️", key=f"edit_trans_{row['id']}"):
                st.session_state.editing_transaction = row['id']
                st.rerun()

            if col7.button("🗑️", key=f"delete_trans_{row['id']}"):
                st.session_state.deleting_transaction = row['id']
                st.rerun()

        # Handle transaction editing
        if st.session_state.get('editing_transaction'):
            transaction_id = st.session_state.editing_transaction
            transaction = ledger.get_transaction(transaction_id)
            if transaction:
                st.markdown("---")
                st.markdown("### ✏️ Edit Transaction")
                with st.form(f"edit_transaction_{transaction_id}"):
                    employees = ledger.get_employees()
                    employee_name = next((emp['name'] for emp in employees if emp['id'] == transaction['employee_id']), "Unknown")
                    st.text_input("Employee", value=employee_name, disabled=True)
                    
                    transaction_type = st.selectbox("Transaction Type", 
                                                   ["Expense (Debit)", "Payment (Credit)"],
                                                   index=0 if transaction['type'] == 'expense' else 1)
                    amount = st.number_input("Amount (PKR)", value=float(transaction['amount']), min_value=0.0, step=100.0)
                    description = st.text_input("Description", value=transaction['description'])
                    date = st.date_input("Date", value=datetime.strptime(transaction['date'], '%Y-%m-%d').date())
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Update Transaction", use_container_width=True):
                            type_code = 'expense' if 'Expense' in transaction_type else 'payment'
                            ledger.update_transaction(transaction_id, type_code, amount, description, date.isoformat())
                            st.success("Transaction updated successfully!")
                            st.session_state.editing_transaction = None
                            st.rerun()
                    with col2:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state.editing_transaction = None
                            st.rerun()

        # Handle transaction deletion
        if st.session_state.get('deleting_transaction'):
            transaction_id = st.session_state.deleting_transaction
            transaction = ledger.get_transaction(transaction_id)
            if transaction:
                st.markdown("---")
                st.markdown("### 🗑️ Delete Transaction")
                st.warning(f"Are you sure you want to delete this transaction? This action cannot be undone!")
                st.write(f"**Date:** {transaction['date']}")
                st.write(f"**Type:** {transaction['type'].title()}")
                st.write(f"**Description:** {transaction['description']}")
                st.write(f"**Amount:** PKR {transaction['amount']:.2f}")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("✅ Yes, Delete", use_container_width=True, type="primary"):
                        ledger.delete_transaction(transaction_id)
                        st.success("Transaction deleted successfully!")
                        st.session_state.deleting_transaction = None
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.deleting_transaction = None
                        st.rerun()

        # Summary
        summary = ledger.get_employee_summary(employee_id, start_date, end_date)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Expenses", f"PKR {summary['total_expenses']:.2f}")
        col2.metric("Total Payments", f"PKR {summary['total_payments']:.2f}")

        balance_color = "negative" if summary['balance'] > 0 else "positive" if summary['balance'] < 0 else ""
        balance_text = f"PKR {abs(summary['balance']):.2f} {'(Due)' if summary['balance'] > 0 else '(Advance)' if summary['balance'] < 0 else ''}"
        col3.markdown(f"<div class='{balance_color}' style='font-size: 1.2em;'>{balance_text}</div>",
                      unsafe_allow_html=True)

    else:
        st.info("No transactions found for this employee in the selected period.")

def render_expense_dashboard(expense_tracker, ledger):
    st.markdown('<div class="sub-header">💰 Expense Management</div>', unsafe_allow_html=True)
    st.write("Track and manage all company and employee expenses")

    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📈 Expense Overview", "➕ Add Expense", "📋 Expense List"])

    with tab1:
        # Summary metrics
        col1, col2, col3 = st.columns(3)

        # Date range for summary
        col1, col2 = st.columns(2)
        with col1:
            exp_start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30),
                                           key="exp_summary_start")
        with col2:
            exp_end_date = st.date_input("End Date", value=datetime.now(), key="exp_summary_end")

        summary = expense_tracker.get_summary(exp_start_date.isoformat(), exp_end_date.isoformat())

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card">Company Total<br>PKR {summary["company_total"]:.2f}</div>',
                        unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card">Employee Total<br>PKR {summary["employee_total"]:.2f}</div>',
                        unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card">Grand Total<br>PKR {summary["grand_total"]:.2f}</div>',
                        unsafe_allow_html=True)

        # Expense analysis charts
        expenses = expense_tracker.get_expenses(start_date=exp_start_date.isoformat(),
                                                end_date=exp_end_date.isoformat())
        if expenses and PLOTLY_AVAILABLE:
            expense_df = pd.DataFrame(expenses)

            # Charts
            col1, col2 = st.columns(2)

            with col1:
                # Expense distribution by type
                type_dist = expense_df['type'].value_counts()
                fig1 = px.pie(
                    values=type_dist.values,
                    names=type_dist.index,
                    title="Expense Distribution by Type",
                    color_discrete_sequence=['#667eea', '#764ba2']
                )
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                # Monthly trend
                expense_df['date'] = pd.to_datetime(expense_df['date'])
                monthly_expenses = expense_df.groupby([expense_df['date'].dt.to_period('M'), 'type'])[
                    'amount'].sum().reset_index()
                monthly_expenses['date'] = monthly_expenses['date'].astype(str)
                fig2 = px.bar(
                    monthly_expenses,
                    x='date',
                    y='amount',
                    color='type',
                    title="Monthly Expenses Trend",
                    labels={'date': 'Month', 'amount': 'Amount (PKR)', 'type': 'Type'},
                    color_discrete_sequence=['#667eea', '#764ba2']
                )
                st.plotly_chart(fig2, use_container_width=True)
        elif expenses:
            st.info("Visualizations require plotly. Install with: pip install plotly")

    with tab2:
        st.markdown("### ➕ Add New Expense")
        with st.form("expense_form", clear_on_submit=True):
            expense_type = st.radio("Expense Type", ["Company", "Employee"])
            description = st.text_input("Description")
            amount = st.number_input("Amount (PKR)", min_value=0.0, step=100.0)

            employee_name = None
            if expense_type == "Employee":
                employees = ledger.get_employees()
                if employees:
                    employee_options = [emp['name'] for emp in employees]
                    employee_name = st.selectbox("Employee", employee_options)
                else:
                    st.info("No employees available. Please add employees first.")
                    employee_name = st.text_input("Or enter employee name")

            date = st.date_input("Date", value=datetime.now())

            if st.form_submit_button("Add Expense", use_container_width=True):
                if description and amount > 0:
                    expense_tracker.add_expense(
                        expense_type.lower(),
                        description,
                        amount,
                        employee_name,
                        date.isoformat()
                    )
                    st.success("Expense added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")

    with tab3:
        st.markdown("### 📋 Expense List")

        expenses = expense_tracker.get_expenses()
        if expenses:
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                search_term = st.text_input("🔍 Search expenses")
            with col2:
                type_filter = st.selectbox("Filter by type", ["All", "Company", "Employee"])
            with col3:
                emp_filter = st.text_input("Filter by employee")

            # Date range filter
            col1, col2 = st.columns(2)
            with col1:
                list_start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30),
                                                key="list_start")
            with col2:
                list_end_date = st.date_input("End Date", value=datetime.now(), key="list_end")

            # Apply filters
            filtered_expenses = expense_tracker.get_expenses(
                expense_type=type_filter.lower() if type_filter != "All" else None,
                start_date=list_start_date.isoformat(),
                end_date=list_end_date.isoformat(),
                employee_name=emp_filter if emp_filter else None
            )

            if search_term:
                filtered_expenses = [e for e in filtered_expenses if search_term.lower() in e['description'].lower()]

            # Display expenses with edit/delete
            for expense in sorted(filtered_expenses, key=lambda x: x['date'], reverse=True)[:20]:
                with st.container():
                    col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 3, 2, 2, 1, 1])
                    col1.write(expense['date'])
                    col2.write(f"{expense['type'].title()}")
                    col3.write(expense['description'])
                    if expense['type'] == 'employee' and expense['employee_name']:
                        col4.write(f"{expense['employee_name']}")
                    else:
                        col4.write("N/A")
                    col5.write(f"PKR {expense['amount']:.2f}")

                    # Edit and Delete buttons
                    if col6.button("✏️", key=f"edit_exp_{expense['id']}"):
                        st.session_state.editing_expense = expense['id']
                        st.rerun()

                    if col7.button("🗑️", key=f"del_exp_{expense['id']}"):
                        st.session_state.deleting_expense = expense['id']
                        st.rerun()

                    st.divider()

            # Handle expense editing
            if st.session_state.get('editing_expense'):
                expense_id = st.session_state.editing_expense
                expense = expense_tracker.get_expense(expense_id)
                if expense:
                    st.markdown("---")
                    st.markdown("### ✏️ Edit Expense")
                    with st.form(f"edit_expense_{expense_id}"):
                        expense_type = st.radio("Expense Type", ["Company", "Employee"], 
                                               index=0 if expense['type'] == 'company' else 1)
                        description = st.text_input("Description", value=expense['description'])
                        amount = st.number_input("Amount (PKR)", value=float(expense['amount']), min_value=0.0, step=100.0)
                        
                        employee_name = None
                        if expense_type == "Employee":
                            employees = ledger.get_employees()
                            if employees:
                                employee_options = [emp['name'] for emp in employees]
                                default_index = employee_options.index(expense['employee_name']) if expense['employee_name'] in employee_options else 0
                                employee_name = st.selectbox("Employee", employee_options, index=default_index)
                            else:
                                st.info("No employees available.")
                                employee_name = st.text_input("Or enter employee name", value=expense['employee_name'] or "")
                        else:
                            employee_name = expense['employee_name']

                        date = st.date_input("Date", value=datetime.strptime(expense['date'], '%Y-%m-%d').date())
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Update Expense", use_container_width=True):
                                if description and amount > 0:
                                    expense_tracker.update_expense(
                                        expense_id,
                                        expense_type.lower(),
                                        description,
                                        amount,
                                        employee_name,
                                        date.isoformat()
                                    )
                                    st.success("Expense updated successfully!")
                                    st.session_state.editing_expense = None
                                    st.rerun()
                                else:
                                    st.error("Please fill all required fields")
                        with col2:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                st.session_state.editing_expense = None
                                st.rerun()

            # Handle expense deletion
            if st.session_state.get('deleting_expense'):
                expense_id = st.session_state.deleting_expense
                expense = expense_tracker.get_expense(expense_id)
                if expense:
                    st.markdown("---")
                    st.markdown("### 🗑️ Delete Expense")
                    st.warning(f"Are you sure you want to delete this expense? This action cannot be undone!")
                    st.write(f"**Date:** {expense['date']}")
                    st.write(f"**Type:** {expense['type'].title()}")
                    st.write(f"**Description:** {expense['description']}")
                    st.write(f"**Amount:** PKR {expense['amount']:.2f}")
                    if expense['employee_name']:
                        st.write(f"**Employee:** {expense['employee_name']}")
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button("✅ Yes, Delete", use_container_width=True, type="primary"):
                            expense_tracker.delete_expense(expense_id)
                            st.success("Expense deleted successfully!")
                            st.session_state.deleting_expense = None
                            st.rerun()
                    with col2:
                        if st.button("❌ Cancel", use_container_width=True):
                            st.session_state.deleting_expense = None
                            st.rerun()

        else:
            st.info("No expenses recorded yet. Add expenses to see the list.")

def render_reports_analytics(ledger, expense_tracker):
    st.markdown('<div class="sub-header">📊 Reports & Analytics</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📈 Analytics Dashboard", "📋 Export Data"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 👥 Employee Analytics")
            employees = ledger.get_employees()

            if employees and PLOTLY_AVAILABLE:
                # Employee balances chart
                employee_data = []
                for emp in employees:
                    summary = ledger.get_employee_summary(emp['id'])
                    employee_data.append({
                        'Employee': emp['name'],
                        'Balance': summary['balance'],
                        'Total Expenses': summary['total_expenses'],
                        'Total Payments': summary['total_payments']
                    })

                df = pd.DataFrame(employee_data)

                fig = px.bar(
                    df,
                    x='Employee',
                    y='Balance',
                    title="Employee Balances",
                    color='Balance',
                    color_continuous_scale=['#ef4444', '#10b981']
                )
                st.plotly_chart(fig, use_container_width=True)
            elif employees:
                st.info("Charts require plotly. Install with: pip install plotly")
                # Show data in table format as fallback
                employee_data = []
                for emp in employees:
                    summary = ledger.get_employee_summary(emp['id'])
                    employee_data.append({
                        'Employee': emp['name'],
                        'Balance': f"PKR {summary['balance']:.2f}",
                        'Total Expenses': f"PKR {summary['total_expenses']:.2f}",
                        'Total Payments': f"PKR {summary['total_payments']:.2f}"
                    })
                st.dataframe(pd.DataFrame(employee_data))
            else:
                st.info("No employee data available")

        with col2:
            st.markdown("### 💰 Expense Analytics")
            expenses = expense_tracker.get_expenses()

            if expenses and PLOTLY_AVAILABLE:
                expense_df = pd.DataFrame(expenses)

                # Top expenses
                top_expenses = expense_df.nlargest(10, 'amount')
                fig = px.bar(
                    top_expenses,
                    x='description',
                    y='amount',
                    title="Top 10 Expenses",
                    color='type',
                    color_discrete_sequence=['#667eea', '#764ba2']
                )
                st.plotly_chart(fig, use_container_width=True)
            elif expenses:
                st.info("Charts require plotly. Install with: pip install plotly")
                # Show data in table format as fallback
                expense_df = pd.DataFrame(expenses)
                st.dataframe(expense_df[['date', 'type', 'description', 'amount', 'employee_name']].head(10))
            else:
                st.info("No expense data available")

    with tab2:
        st.markdown("### 📤 Export Data")

        # Export templates
        st.markdown("#### Download Import Templates")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Employee Template", use_container_width=True):
                template_df = pd.DataFrame(columns=['name', 'initial_balance'])
                csv = template_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV Template",
                    data=csv,
                    file_name="employee_import_template.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        with col2:
            if st.button("📝 Expense Template", use_container_width=True):
                template_df = pd.DataFrame(columns=['type', 'description', 'amount', 'employee_name', 'date'])
                csv = template_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV Template",
                    data=csv,
                    file_name="expense_import_template.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        # Export actual data
        st.markdown("#### Export Current Data")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export Employee Data to CSV", use_container_width=True):
                employees = ledger.get_employees()
                if employees:
                    employee_data = []
                    for emp in employees:
                        summary = ledger.get_employee_summary(emp['id'])
                        employee_data.append({
                            'name': emp['name'],
                            'initial_balance': emp['initial_balance'],
                            'total_expenses': summary['total_expenses'],
                            'total_payments': summary['total_payments'],
                            'current_balance': summary['balance']
                        })

                    df = pd.DataFrame(employee_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download Employee CSV",
                        data=csv,
                        file_name=f"employees_export_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("No employee data to export")

        with col2:
            if st.button("Export Expense Data to CSV", use_container_width=True):
                expenses = expense_tracker.get_expenses()
                if expenses:
                    df = pd.DataFrame(expenses)
                    # Remove internal IDs for export
                    export_df = df[['type', 'description', 'amount', 'employee_name', 'date']]
                    csv = export_df.to_csv(index=False)
                    st.download_button(
                        label="Download Expense CSV",
                        data=csv,
                        file_name=f"expenses_export_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("No expense data to export")

def render_data_management(ledger, expense_tracker):
    st.markdown('<div class="sub-header">📁 Data Management</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📥 Import Data", "🔧 System Management"])

    with tab1:
        st.markdown("### 📥 Import Data")

        st.markdown("#### Import Employees")
        employee_file = st.file_uploader("Upload Employee CSV", type="csv", key="emp_upload")
        if employee_file is not None:
            try:
                df = pd.read_csv(employee_file)
                st.write("Preview of employee data:")
                st.dataframe(df.head())

                if st.button("Import Employees", use_container_width=True):
                    imported_count = 0
                    for _, row in df.iterrows():
                        if 'name' in row and pd.notna(row['name']):
                            ledger.add_employee(
                                row['name'],
                                row.get('initial_balance', 0)
                            )
                            imported_count += 1
                    st.success(f"Successfully imported {imported_count} employees!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")

        st.markdown("#### Import Expenses")
        expense_file = st.file_uploader("Upload Expense CSV", type="csv", key="exp_upload")
        if expense_file is not None:
            try:
                df = pd.read_csv(expense_file)
                st.write("Preview of expense data:")
                st.dataframe(df.head())

                if st.button("Import Expenses", use_container_width=True):
                    imported_count = 0
                    for _, row in df.iterrows():
                        if all(k in row and pd.notna(row[k]) for k in ['type', 'description', 'amount', 'date']):
                            expense_tracker.add_expense(
                                row['type'],
                                row['description'],
                                row['amount'],
                                row.get('employee_name'),
                                row['date']
                            )
                            imported_count += 1
                    st.success(f"Successfully imported {imported_count} expenses!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")

    with tab2:
        # System statistics and cleanup
        st.markdown("### 🔧 System Management")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Employees", len(ledger.get_employees()))
        with col2:
            st.metric("Total Transactions", len(ledger.get_transactions()))
        with col3:
            st.metric("Total Expenses", len(expense_tracker.get_expenses()))

        # Data cleanup with confirmation
        st.markdown("#### Data Management")
        if st.button("🚨 Clear All Data", use_container_width=True):
            st.warning("This will delete ALL data permanently!")
            if st.checkbox("I understand this action cannot be undone"):
                if st.button("Confirm Delete All Data", type="primary", use_container_width=True):
                    # Clear all data from database
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute('DELETE FROM employees')
                    c.execute('DELETE FROM transactions')
                    c.execute('DELETE FROM expenses')
                    conn.commit()
                    conn.close()
                    st.success("All data cleared successfully!")
                    st.rerun()

# Footer for all pages
def render_footer():
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <h3>DatanexSolution</h3>
        <p>Advanced Business Management Solutions</p>
        <p>For any query please feel free to contact: <strong>+92-3207429422</strong></p>
        <p>Email: info@datanexsolution.com | Website: www.datanexsolution.com</p>
        <p style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
            &copy; 2024 HMD Solutions. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    render_footer()
