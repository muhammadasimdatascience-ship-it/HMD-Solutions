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
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        margin-right: 0.5rem;
    }
    .delete-btn {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    }
    .update-btn {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
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
    .download-btn {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        margin: 0.2rem;
    }
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .warning-message {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .data-table {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
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
            phone TEXT,
            email TEXT,
            position TEXT,
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
            category TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create settings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id TEXT PRIMARY KEY,
            company_name TEXT DEFAULT 'HMD Solutions',
            company_address TEXT DEFAULT 'Karachi, Pakistan',
            company_phone TEXT DEFAULT '+92-3207429422',
            company_email TEXT DEFAULT 'info@hmdsolutions.com',
            currency TEXT DEFAULT 'PKR',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert default settings if not exists
    c.execute('''
        INSERT OR IGNORE INTO settings (id, company_name, company_address, company_phone, company_email, currency)
        VALUES ('default', 'HMD Solutions', 'Karachi, Pakistan', '+92-3207429422', 'info@hmdsolutions.com', 'PKR')
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect('hmd_solutions.db')

class SettingsManager:
    def __init__(self):
        init_database()

    def get_settings(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM settings WHERE id = "default"')
        row = c.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'company_name': row[1],
                'company_address': row[2],
                'company_phone': row[3],
                'company_email': row[4],
                'currency': row[5],
                'created_at': row[6]
            }
        return None

    def update_settings(self, company_name, company_address, company_phone, company_email, currency):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            UPDATE settings 
            SET company_name = ?, company_address = ?, company_phone = ?, company_email = ?, currency = ?
            WHERE id = "default"
        ''', (company_name, company_address, company_phone, company_email, currency))
        conn.commit()
        conn.close()

class EmployeeLedger:
    def __init__(self):
        init_database()
    
    def add_employee(self, name, initial_balance=0, phone="", email="", position=""):
        conn = get_db_connection()
        c = conn.cursor()
        employee_id = str(uuid.uuid4())
        c.execute('INSERT INTO employees (id, name, initial_balance, phone, email, position) VALUES (?, ?, ?, ?, ?, ?)',
                 (employee_id, name, initial_balance, phone, email, position))
        conn.commit()
        conn.close()
        return employee_id
    
    def get_employees(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM employees ORDER BY name')
        employees = [{'id': row[0], 'name': row[1], 'initial_balance': row[2], 
                     'phone': row[3], 'email': row[4], 'position': row[5]} for row in c.fetchall()]
        conn.close()
        return employees
    
    def get_employee(self, employee_id):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM employees WHERE id = ?', (employee_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'name': row[1], 'initial_balance': row[2], 
                   'phone': row[3], 'email': row[4], 'position': row[5]}
        return None
    
    def update_employee(self, employee_id, name, initial_balance, phone, email, position):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            UPDATE employees 
            SET name = ?, initial_balance = ?, phone = ?, email = ?, position = ?
            WHERE id = ?
        ''', (name, initial_balance, phone, email, position, employee_id))
        conn.commit()
        conn.close()
    
    def delete_employee(self, employee_id):
        conn = get_db_connection()
        c = conn.cursor()
        # First delete all transactions for this employee
        c.execute('DELETE FROM transactions WHERE employee_id = ?', (employee_id,))
        # Then delete the employee
        c.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
        conn.commit()
        conn.close()
    
    def add_transaction(self, employee_id, transaction_type, amount, description, date):
        conn = get_db_connection()
        c = conn.cursor()
        transaction_id = str(uuid.uuid4())
        c.execute('''
            INSERT INTO transactions (id, employee_id, type, amount, description, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transaction_id, employee_id, transaction_type, amount, description, date))
        conn.commit()
        conn.close()
        return transaction_id
    
    def get_transaction(self, transaction_id):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'employee_id': row[1],
                'type': row[2],
                'amount': row[3],
                'description': row[4],
                'date': row[5]
            }
        return None
    
    def update_transaction(self, transaction_id, transaction_type, amount, description, date):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            UPDATE transactions 
            SET type = ?, amount = ?, description = ?, date = ?
            WHERE id = ?
        ''', (transaction_type, amount, description, date, transaction_id))
        conn.commit()
        conn.close()
    
    def delete_transaction(self, transaction_id):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        conn.commit()
        conn.close()
    
    def get_employee_transactions(self, employee_id, start_date=None, end_date=None):
        conn = get_db_connection()
        c = conn.cursor()
        
        query = 'SELECT * FROM transactions WHERE employee_id = ?'
        params = [employee_id]
        
        if start_date and end_date:
            query += ' AND date BETWEEN ? AND ?'
            params.extend([start_date, end_date])
        
        query += ' ORDER BY date DESC'
        
        c.execute(query, params)
        transactions = [{
            'id': row[0],
            'employee_id': row[1],
            'type': row[2],
            'amount': row[3],
            'description': row[4],
            'date': row[5]
        } for row in c.fetchall()]
        
        conn.close()
        return transactions
    
    def get_employee_balance(self, employee_id):
        conn = get_db_connection()
        c = conn.cursor()
        
        # Get initial balance
        c.execute('SELECT initial_balance FROM employees WHERE id = ?', (employee_id,))
        result = c.fetchone()
        initial_balance = result[0] if result else 0
        
        # Calculate total expenses and payments
        c.execute('SELECT type, SUM(amount) FROM transactions WHERE employee_id = ? GROUP BY type', (employee_id,))
        transactions = c.fetchall()
        
        total_expenses = 0
        total_payments = 0
        
        for trans_type, amount in transactions:
            if trans_type == 'expense':
                total_expenses += amount if amount else 0
            elif trans_type == 'payment':
                total_payments += amount if amount else 0
        
        conn.close()
        
        # Balance = Initial Balance + Expenses - Payments
        # Positive balance means employee owes money, negative means advance
        return initial_balance + total_expenses - total_payments
    
    def get_employee_summary(self, employee_id, start_date=None, end_date=None):
        transactions = self.get_employee_transactions(employee_id, start_date, end_date)
        
        total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        total_payments = sum(t['amount'] for t in transactions if t['type'] == 'payment')
        
        # Get initial balance for the employee
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT initial_balance FROM employees WHERE id = ?', (employee_id,))
        result = c.fetchone()
        initial_balance = result[0] if result else 0
        conn.close()
        
        balance = initial_balance + total_expenses - total_payments
        
        return {
            'total_expenses': total_expenses,
            'total_payments': total_payments,
            'balance': balance,
            'transaction_count': len(transactions)
        }
    
    def get_transactions(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            SELECT t.*, e.name as employee_name 
            FROM transactions t 
            LEFT JOIN employees e ON t.employee_id = e.id 
            ORDER BY t.date DESC
        ''')
        transactions = [{
            'id': row[0],
            'employee_id': row[1],
            'type': row[2],
            'amount': row[3],
            'description': row[4],
            'date': row[5],
            'employee_name': row[6]
        } for row in c.fetchall()]
        conn.close()
        return transactions

class ExpenseTracker:
    def __init__(self):
        init_database()
    
    def add_expense(self, expense_type, description, amount, employee_name=None, date=None, category="General"):
        conn = get_db_connection()
        c = conn.cursor()
        expense_id = str(uuid.uuid4())
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        c.execute('''
            INSERT INTO expenses (id, type, description, amount, employee_name, date, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (expense_id, expense_type, description, amount, employee_name, date, category))
        
        conn.commit()
        conn.close()
        return expense_id
    
    def get_expense(self, expense_id):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'type': row[1],
                'description': row[2],
                'amount': row[3],
                'employee_name': row[4],
                'date': row[5],
                'category': row[6]
            }
        return None
    
    def update_expense(self, expense_id, expense_type, description, amount, employee_name, date, category):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            UPDATE expenses 
            SET type = ?, description = ?, amount = ?, employee_name = ?, date = ?, category = ?
            WHERE id = ?
        ''', (expense_type, description, amount, employee_name, date, category, expense_id))
        conn.commit()
        conn.close()
    
    def delete_expense(self, expense_id):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
        conn.close()
    
    def get_expenses(self, expense_type=None, start_date=None, end_date=None):
        conn = get_db_connection()
        c = conn.cursor()
        
        query = 'SELECT * FROM expenses WHERE status != "deleted"'
        params = []
        
        conditions = []
        if expense_type:
            conditions.append('type = ?')
            params.append(expense_type)
        
        if start_date and end_date:
            conditions.append('date BETWEEN ? AND ?')
            params.extend([start_date, end_date])
        
        if conditions:
            query += ' AND ' + ' AND '.join(conditions)
        
        query += ' ORDER BY date DESC'
        
        c.execute(query, params)
        expenses = [{
            'id': row[0],
            'type': row[1],
            'description': row[2],
            'amount': row[3],
            'employee_name': row[4],
            'date': row[5],
            'category': row[6]
        } for row in c.fetchall()]
        
        conn.close()
        return expenses
    
    def get_summary(self, start_date=None, end_date=None):
        expenses = self.get_expenses(start_date=start_date, end_date=end_date)
        
        company_total = sum(e['amount'] for e in expenses if e['type'] == 'company')
        employee_total = sum(e['amount'] for e in expenses if e['type'] == 'employee')
        grand_total = company_total + employee_total
        
        return {
            'company_total': company_total,
            'employee_total': employee_total,
            'grand_total': grand_total,
            'expense_count': len(expenses)
        }

class PDFGenerator:
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.get_settings()

    def generate_employee_ledger_pdf(self, employee_name, transactions, summary, start_date=None, end_date=None):
        if not FPDF_AVAILABLE:
            st.error("PDF generation is not available. Please install fpdf.")
            return None
            
        try:
            pdf = FPDF()
            pdf.add_page()

            # Header with company name from settings
            pdf.set_font('Arial', 'B', 20)
            pdf.cell(0, 10, self.settings['company_name'], 0, 1, 'C')
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Employee Ledger Report', 0, 1, 'C')
            pdf.ln(5)

            # Report period
            pdf.set_font('Arial', 'I', 12)
            period_text = f"Period: {start_date} to {end_date}" if start_date and end_date else "All Time Period"
            pdf.cell(0, 10, period_text, 0, 1, 'C')
            pdf.ln(10)

            # Employee information
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, f'Employee: {employee_name}', 0, 1)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Report Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1)
            pdf.ln(5)

            # Summary
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Summary:', 0, 1)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, f'Total Expenses: {self.settings["currency"]} {summary["total_expenses"]:.2f}', 0, 1)
            pdf.cell(0, 8, f'Total Payments: {self.settings["currency"]} {summary["total_payments"]:.2f}', 0, 1)

            # Balance with color
            balance_status = '(Due)' if summary['balance'] > 0 else '(Advance)' if summary['balance'] < 0 else ''
            if summary['balance'] > 0:
                pdf.set_text_color(255, 0, 0)  # Red for due
            else:
                pdf.set_text_color(0, 128, 0)  # Green for advance
                
            pdf.cell(0, 8, f'Balance: {self.settings["currency"]} {abs(summary["balance"]):.2f} {balance_status}', 0, 1)
            pdf.set_text_color(0, 0, 0)  # Reset to black
            pdf.ln(10)

            # Transactions table
            if transactions:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'Transaction History:', 0, 1)

                # Table header
                pdf.set_fill_color(79, 129, 189)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(40, 10, 'Date', 1, 0, 'C', True)
                pdf.cell(30, 10, 'Type', 1, 0, 'C', True)
                pdf.cell(70, 10, 'Description', 1, 0, 'C', True)
                pdf.cell(30, 10, 'Amount', 1, 1, 'C', True)

                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Arial', '', 10)
                for t in transactions:
                    # Alternate row colors
                    if transactions.index(t) % 2 == 0:
                        pdf.set_fill_color(240, 240, 240)
                    else:
                        pdf.set_fill_color(255, 255, 255)

                    pdf.cell(40, 8, t['date'], 1, 0, 'C', True)
                    pdf.cell(30, 8, t['type'].title(), 1, 0, 'C', True)
                    pdf.cell(70, 8, t['description'][:40], 1, 0, 'C', True)

                    # Color code amounts
                    if t['type'] == 'expense':
                        pdf.set_text_color(255, 0, 0)
                    else:
                        pdf.set_text_color(0, 128, 0)
                    pdf.cell(30, 8, f"{self.settings['currency']} {t['amount']:.2f}", 1, 1, 'C', True)
                    pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(0, 10, 'No transactions found for the selected period.', 0, 1)

            # Footer with company info
            pdf.ln(15)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 10, f'Generated by {self.settings["company_name"]} Business Management System', 0, 1, 'C')
            pdf.cell(0, 5, f'Contact: {self.settings["company_phone"]} | Email: {self.settings["company_email"]}', 0, 1, 'C')

            return pdf
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            return None

def render_dashboard(ledger, expense_tracker, pdf_generator):
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

    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("➕ Add New Employee", use_container_width=True, key="quick_add_emp"):
            st.session_state.quick_action = "add_employee"

    with col2:
        if st.button("💸 Record Transaction", use_container_width=True, key="quick_add_trans"):
            st.session_state.quick_action = "add_transaction"

    with col3:
        if st.button("💰 Add Expense", use_container_width=True, key="quick_add_exp"):
            st.session_state.quick_action = "add_expense"

    with col4:
        if st.button("📊 View Reports", use_container_width=True, key="quick_reports"):
            st.session_state.quick_action = "view_reports"

def render_employee_ledger(ledger, pdf_generator):
    st.markdown('<div class="sub-header">👥 Employee Ledger System</div>', unsafe_allow_html=True)
    st.write("Track expenses, payments, and balances for all employees")

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Employee Management", "➕ Add Employee", "💸 Record Transaction", "📊 Employee Details"])

    with tab1:
        st.markdown("### Employee Management")
        employees = ledger.get_employees()
        
        if employees:
            st.markdown('<div class="data-table">', unsafe_allow_html=True)
            for emp in employees:
                col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 1, 1])
                
                with col1:
                    st.write(f"**{emp['name']}**")
                    if emp['position']:
                        st.caption(f"{emp['position']}")
                
                with col2:
                    st.write(f"Initial: PKR {emp['initial_balance']:.2f}")
                
                with col3:
                    balance = ledger.get_employee_balance(emp['id'])
                    balance_color = "red" if balance > 0 else "green" if balance < 0 else "gray"
                    st.markdown(f"Balance: <span style='color: {balance_color};'>PKR {abs(balance):.2f}</span>", 
                              unsafe_allow_html=True)
                    st.caption("(Due)" if balance > 0 else "(Advance)" if balance < 0 else "")
                
                with col4:
                    if emp['phone']:
                        st.caption(f"📞 {emp['phone']}")
                    if emp['email']:
                        st.caption(f"📧 {emp['email']}")
                
                with col5:
                    if st.button("✏️", key=f"edit_emp_{emp['id']}"):
                        st.session_state.editing_employee = emp['id']
                
                with col6:
                    if st.button("🗑️", key=f"delete_emp_{emp['id']}"):
                        st.session_state.deleting_employee = emp['id']
                
                st.divider()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No employees found. Add employees to get started.")

        # Edit Employee Modal
        if 'editing_employee' in st.session_state:
            employee = ledger.get_employee(st.session_state.editing_employee)
            if employee:
                st.markdown("---")
                st.markdown("### ✏️ Edit Employee")
                
                with st.form(f"edit_employee_{employee['id']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("Employee Name", value=employee['name'])
                        phone = st.text_input("Phone Number", value=employee['phone'] or "")
                        position = st.text_input("Position", value=employee['position'] or "")
                    with col2:
                        initial_balance = st.number_input("Initial Balance", value=float(employee['initial_balance']), step=100.0)
                        email = st.text_input("Email", value=employee['email'] or "")
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        if st.form_submit_button("💾 Update Employee", use_container_width=True):
                            ledger.update_employee(employee['id'], name, initial_balance, phone, email, position)
                            st.success(f"Employee {name} updated successfully!")
                            del st.session_state.editing_employee
                            st.rerun()
                    with col2:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            del st.session_state.editing_employee
                            st.rerun()

        # Delete Confirmation
        if 'deleting_employee' in st.session_state:
            employee = ledger.get_employee(st.session_state.deleting_employee)
            if employee:
                st.markdown("---")
                st.markdown("### 🗑️ Delete Employee")
                st.warning(f"Are you sure you want to delete **{employee['name']}**? This action cannot be undone and will also delete all associated transactions.")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    if st.button("✅ Confirm Delete", use_container_width=True, type="primary"):
                        ledger.delete_employee(employee['id'])
                        st.success(f"Employee {employee['name']} deleted successfully!")
                        del st.session_state.deleting_employee
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        del st.session_state.deleting_employee
                        st.rerun()

    with tab2:
        st.markdown("### Add New Employee")
        with st.form("add_employee_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Employee Name*")
                phone = st.text_input("Phone Number")
                position = st.text_input("Position")
            with col2:
                initial_balance = st.number_input("Initial Balance", value=0.0, step=100.0)
                email = st.text_input("Email")
            
            if st.form_submit_button("➕ Add Employee"):
                if name:
                    ledger.add_employee(name, initial_balance, phone, email, position)
                    st.success(f"Employee {name} added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter employee name")

    with tab3:
        st.markdown("### Record Transaction")
        employees = ledger.get_employees()
        
        if employees:
            with st.form("add_transaction_form"):
                col1, col2 = st.columns(2)
                with col1:
                    employee_id = st.selectbox("Select Employee*", 
                                             options=[emp['id'] for emp in employees],
                                             format_func=lambda x: next(emp['name'] for emp in employees if emp['id'] == x))
                    transaction_type = st.selectbox("Transaction Type*", ["expense", "payment"])
                    amount = st.number_input("Amount*", min_value=0.0, step=100.0)
                with col2:
                    description = st.text_input("Description*")
                    date = st.date_input("Date", value=datetime.now())
                
                if st.form_submit_button("💾 Record Transaction"):
                    if description and amount > 0:
                        ledger.add_transaction(employee_id, transaction_type, amount, description, date.isoformat())
                        st.success("Transaction recorded successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill all required fields (*) correctly")
        else:
            st.info("No employees found. Please add employees first.")

    with tab4:
        st.markdown("### Employee Details & Ledger")
        employees = ledger.get_employees()
        
        if employees:
            selected_employee = st.selectbox("Select Employee", 
                                           options=[emp['id'] for emp in employees],
                                           format_func=lambda x: next(emp['name'] for emp in employees if emp['id'] == x),
                                           key="employee_detail_select")
            
            if selected_employee:
                employee_name = next(emp['name'] for emp in employees if emp['id'] == selected_employee)
                employee = ledger.get_employee(selected_employee)
                
                # Display employee info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Name:** {employee['name']}")
                    if employee['position']:
                        st.write(f"**Position:** {employee['position']}")
                with col2:
                    st.write(f"**Initial Balance:** PKR {employee['initial_balance']:.2f}")
                    if employee['phone']:
                        st.write(f"**Phone:** {employee['phone']}")
                with col3:
                    if employee['email']:
                        st.write(f"**Email:** {employee['email']}")
                
                transactions = ledger.get_employee_transactions(selected_employee)
                summary = ledger.get_employee_summary(selected_employee)
                
                st.markdown(f"#### Ledger Summary for {employee_name}")
                
                # Display summary
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Expenses", f"PKR {summary['total_expenses']:.2f}")
                with col2:
                    st.metric("Total Payments", f"PKR {summary['total_payments']:.2f}")
                with col3:
                    balance_status = "Due" if summary['balance'] > 0 else "Advance" if summary['balance'] < 0 else "Settled"
                    balance_color = "red" if summary['balance'] > 0 else "green" if summary['balance'] < 0 else "gray"
                    st.metric("Current Balance", f"PKR {abs(summary['balance']):.2f}", balance_status)
                with col4:
                    st.metric("Total Transactions", summary['transaction_count'])
                
                # Date filter for transactions
                st.markdown("#### Transaction History")
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30), key="ledger_start")
                with col2:
                    end_date = st.date_input("End Date", value=datetime.now(), key="ledger_end")
                
                if st.button("Apply Filter", key="filter_ledger"):
                    filtered_transactions = ledger.get_employee_transactions(
                        selected_employee, start_date.isoformat(), end_date.isoformat()
                    )
                    transactions = filtered_transactions
                
                # Display transactions with edit/delete
                if transactions:
                    for t in transactions:
                        with st.container():
                            col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
                            with col1:
                                st.write(f"**{t['description']}**")
                            with col2:
                                st.write(t['date'])
                            with col3:
                                st.write(t['type'].title())
                            with col4:
                                amount_color = "red" if t['type'] == 'expense' else "green"
                                st.markdown(f"<span style='color: {amount_color}; font-weight: bold;'>PKR {t['amount']:.2f}</span>", 
                                          unsafe_allow_html=True)
                            with col5:
                                if st.button("✏️", key=f"edit_trans_{t['id']}"):
                                    st.session_state.editing_transaction = t['id']
                            with col6:
                                if st.button("🗑️", key=f"delete_trans_{t['id']}"):
                                    st.session_state.deleting_transaction = t['id']
                            st.divider()
                else:
                    st.info("No transactions found for this employee.")
        else:
            st.info("No employees found. Please add employees first.")

        # Edit Transaction Modal
        if 'editing_transaction' in st.session_state:
            transaction = ledger.get_transaction(st.session_state.editing_transaction)
            if transaction:
                st.markdown("---")
                st.markdown("### ✏️ Edit Transaction")
                
                employees = ledger.get_employees()
                with st.form(f"edit_transaction_{transaction['id']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        employee_id = st.selectbox("Select Employee", 
                                                 options=[emp['id'] for emp in employees],
                                                 format_func=lambda x: next(emp['name'] for emp in employees if emp['id'] == x),
                                                 index=next(i for i, emp in enumerate(employees) if emp['id'] == transaction['employee_id']))
                        transaction_type = st.selectbox("Transaction Type", ["expense", "payment"], 
                                                       index=0 if transaction['type'] == 'expense' else 1)
                        amount = st.number_input("Amount", min_value=0.0, step=100.0, value=float(transaction['amount']))
                    with col2:
                        description = st.text_input("Description", value=transaction['description'])
                        date = st.date_input("Date", value=datetime.strptime(transaction['date'], '%Y-%m-%d'))
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        if st.form_submit_button("💾 Update Transaction", use_container_width=True):
                            ledger.update_transaction(transaction['id'], transaction_type, amount, description, date.isoformat())
                            st.success("Transaction updated successfully!")
                            del st.session_state.editing_transaction
                            st.rerun()
                    with col2:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            del st.session_state.editing_transaction
                            st.rerun()

        # Delete Transaction Confirmation
        if 'deleting_transaction' in st.session_state:
            transaction = ledger.get_transaction(st.session_state.deleting_transaction)
            if transaction:
                st.markdown("---")
                st.markdown("### 🗑️ Delete Transaction")
                st.warning(f"Are you sure you want to delete this transaction? This action cannot be undone.")
                st.write(f"**Description:** {transaction['description']}")
                st.write(f"**Amount:** PKR {transaction['amount']:.2f}")
                st.write(f"**Type:** {transaction['type'].title()}")
                st.write(f"**Date:** {transaction['date']}")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    if st.button("✅ Confirm Delete", use_container_width=True, type="primary"):
                        ledger.delete_transaction(transaction['id'])
                        st.success("Transaction deleted successfully!")
                        del st.session_state.deleting_transaction
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        del st.session_state.deleting_transaction
                        st.rerun()

def render_expense_dashboard(expense_tracker, ledger, pdf_generator):
    st.markdown('<div class="sub-header">💰 Expense Management</div>', unsafe_allow_html=True)
    st.write("Track and manage all company and employee expenses")

    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📈 Expense Overview", "➕ Add Expense", "📋 Expense Management"])

    with tab1:
        st.markdown("### Expense Overview")
        expense_summary = expense_tracker.get_summary()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Company Expenses", f"PKR {expense_summary['company_total']:.2f}")
        with col2:
            st.metric("Employee Expenses", f"PKR {expense_summary['employee_total']:.2f}")
        with col3:
            st.metric("Total Expenses", f"PKR {expense_summary['grand_total']:.2f}")
        
        # Expense breakdown
        expenses = expense_tracker.get_expenses()
        if expenses:
            df = pd.DataFrame(expenses)
            df['date'] = pd.to_datetime(df['date'])
            
            # Monthly trend
            monthly_expenses = df.groupby([df['date'].dt.to_period('M'), 'type'])['amount'].sum().reset_index()
            monthly_expenses['date'] = monthly_expenses['date'].astype(str)
            
            if PLOTLY_AVAILABLE:
                fig = px.bar(monthly_expenses, x='date', y='amount', color='type',
                           title="Monthly Expenses Trend", barmode='group')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.bar_chart(monthly_expenses.pivot(index='date', columns='type', values='amount'))

    with tab2:
        st.markdown("### Add New Expense")
        with st.form("add_expense_form"):
            col1, col2 = st.columns(2)
            with col1:
                expense_type = st.selectbox("Expense Type*", ["company", "employee"])
                amount = st.number_input("Amount*", min_value=0.0, step=100.0)
                date = st.date_input("Date", value=datetime.now())
            with col2:
                description = st.text_area("Description*")
                category = st.selectbox("Category", ["General", "Office Supplies", "Travel", "Utilities", "Salaries", "Other"])
                employee_name = st.selectbox("Employee (if employee expense)", 
                                           options=[""] + [emp['name'] for emp in ledger.get_employees()],
                                           disabled=expense_type != "employee")
            
            if st.form_submit_button("➕ Add Expense"):
                if description and amount > 0:
                    emp_name = employee_name if expense_type == "employee" else None
                    expense_tracker.add_expense(expense_type, description, amount, emp_name, date.isoformat(), category)
                    st.success("Expense added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields (*) correctly")

    with tab3:
        st.markdown("### Expense Management")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_type = st.selectbox("Filter by Type", ["All", "company", "employee"])
        with col2:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30), key="expense_start")
        with col3:
            end_date = st.date_input("End Date", value=datetime.now(), key="expense_end")
        
        # Get filtered expenses
        expense_type_filter = None if filter_type == "All" else filter_type
        expenses = expense_tracker.get_expenses(expense_type_filter, start_date.isoformat(), end_date.isoformat())
        
        if expenses:
            st.markdown(f"**Found {len(expenses)} expenses**")
            for exp in expenses:
                with st.container():
                    col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 1, 1, 1, 1, 1, 1])
                    with col1:
                        st.write(f"**{exp['description']}**")
                        if exp['employee_name']:
                            st.caption(f"👤 {exp['employee_name']}")
                        if exp['category'] and exp['category'] != "General":
                            st.caption(f"🏷️ {exp['category']}")
                    with col2:
                        st.write(exp['date'])
                    with col3:
                        type_badge = "🏢" if exp['type'] == 'company' else "👤"
                        st.write(f"{type_badge} {exp['type'].title()}")
                    with col4:
                        st.write(f"PKR {exp['amount']:.2f}")
                    with col5:
                        st.caption(exp['category'] or "General")
                    with col6:
                        if st.button("✏️", key=f"edit_exp_{exp['id']}"):
                            st.session_state.editing_expense = exp['id']
                    with col7:
                        if st.button("🗑️", key=f"delete_exp_{exp['id']}"):
                            st.session_state.deleting_expense = exp['id']
                    st.divider()
        else:
            st.info("No expenses found for the selected filters.")

        # Edit Expense Modal
        if 'editing_expense' in st.session_state:
            expense = expense_tracker.get_expense(st.session_state.editing_expense)
            if expense:
                st.markdown("---")
                st.markdown("### ✏️ Edit Expense")
                
                with st.form(f"edit_expense_{expense['id']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        expense_type = st.selectbox("Expense Type", ["company", "employee"], 
                                                  index=0 if expense['type'] == 'company' else 1)
                        amount = st.number_input("Amount", min_value=0.0, step=100.0, value=float(expense['amount']))
                        date = st.date_input("Date", value=datetime.strptime(expense['date'], '%Y-%m-%d'))
                    with col2:
                        description = st.text_area("Description", value=expense['description'])
                        category = st.selectbox("Category", ["General", "Office Supplies", "Travel", "Utilities", "Salaries", "Other"],
                                              index=["General", "Office Supplies", "Travel", "Utilities", "Salaries", "Other"].index(expense['category']) if expense['category'] in ["General", "Office Supplies", "Travel", "Utilities", "Salaries", "Other"] else 0)
                        employee_name = st.selectbox("Employee (if employee expense)", 
                                                   options=[""] + [emp['name'] for emp in ledger.get_employees()],
                                                   disabled=expense_type != "employee",
                                                   index=([""] + [emp['name'] for emp in ledger.get_employees()]).index(expense['employee_name']) if expense['employee_name'] in [""] + [emp['name'] for emp in ledger.get_employees()] else 0)
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        if st.form_submit_button("💾 Update Expense", use_container_width=True):
                            emp_name = employee_name if expense_type == "employee" else None
                            expense_tracker.update_expense(expense['id'], expense_type, description, amount, emp_name, date.isoformat(), category)
                            st.success("Expense updated successfully!")
                            del st.session_state.editing_expense
                            st.rerun()
                    with col2:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            del st.session_state.editing_expense
                            st.rerun()

        # Delete Expense Confirmation
        if 'deleting_expense' in st.session_state:
            expense = expense_tracker.get_expense(st.session_state.deleting_expense)
            if expense:
                st.markdown("---")
                st.markdown("### 🗑️ Delete Expense")
                st.warning(f"Are you sure you want to delete this expense? This action cannot be undone.")
                st.write(f"**Description:** {expense['description']}")
                st.write(f"**Amount:** PKR {expense['amount']:.2f}")
                st.write(f"**Type:** {expense['type'].title()}")
                st.write(f"**Date:** {expense['date']}")
                if expense['employee_name']:
                    st.write(f"**Employee:** {expense['employee_name']}")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    if st.button("✅ Confirm Delete", use_container_width=True, type="primary"):
                        expense_tracker.delete_expense(expense['id'])
                        st.success("Expense deleted successfully!")
                        del st.session_state.deleting_expense
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        del st.session_state.deleting_expense
                        st.rerun()

def render_reports_analytics(ledger, expense_tracker, pdf_generator):
    st.markdown('<div class="sub-header">📊 Reports & Analytics</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📈 Analytics Dashboard", "📋 Export Data"])

    with tab1:
        st.markdown("### Business Analytics")
        
        # Employee analytics
        employees = ledger.get_employees()
        if employees:
            employee_data = []
            for emp in employees:
                balance = ledger.get_employee_balance(emp['id'])
                employee_data.append({
                    'name': emp['name'],
                    'balance': balance,
                    'status': 'Due' if balance > 0 else 'Advance' if balance < 0 else 'Settled'
                })
            
            df_employees = pd.DataFrame(employee_data)
            
            if PLOTLY_AVAILABLE:
                fig = px.bar(df_employees, x='name', y='balance', color='status',
                           title="Employee Balances", color_discrete_map={'Due': 'red', 'Advance': 'green', 'Settled': 'blue'})
                st.plotly_chart(fig, use_container_width=True)
        
        # Expense analytics
        expenses = expense_tracker.get_expenses()
        if expenses:
            df_expenses = pd.DataFrame(expenses)
            expense_by_type = df_expenses.groupby('type')['amount'].sum().reset_index()
            
            if PLOTLY_AVAILABLE:
                fig = px.pie(expense_by_type, values='amount', names='type', 
                           title="Expense Distribution by Type")
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("### Data Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Export Employee Data")
            employees = ledger.get_employees()
            if employees:
                df_employees = pd.DataFrame(employees)
                csv_employees = df_employees.to_csv(index=False)
                st.download_button(
                    label="Download Employee CSV",
                    data=csv_employees,
                    file_name=f"employees_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("No employee data to export")
        
        with col2:
            st.markdown("#### Export Expense Data")
            expenses = expense_tracker.get_expenses()
            if expenses:
                df_expenses = pd.DataFrame(expenses)
                csv_expenses = df_expenses.to_csv(index=False)
                st.download_button(
                    label="Download Expense CSV",
                    data=csv_expenses,
                    file_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("No expense data to export")

def render_data_management(ledger, expense_tracker):
    st.markdown('<div class="sub-header">📁 Data Management</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🗃️ Database Management", "🔄 System Reset"])
    
    with tab1:
        st.markdown("### Database Information")
        
        employees = ledger.get_employees()
        transactions = ledger.get_transactions()
        expenses = expense_tracker.get_expenses()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Employees", len(employees))
        with col2:
            st.metric("Total Transactions", len(transactions))
        with col3:
            st.metric("Total Expenses", len(expenses))
        
        st.markdown("### Backup Data")
        if st.button("Create Backup", key="create_backup"):
            # Simple backup implementation
            backup_data = {
                'employees': employees,
                'transactions': transactions,
                'expenses': expenses,
                'backup_date': datetime.now().isoformat()
            }
            
            json_data = json.dumps(backup_data, indent=2)
            st.download_button(
                label="Download Backup",
                data=json_data,
                file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with tab2:
        st.markdown("### System Reset")
        st.warning("⚠️ This action cannot be undone!")
        
        if st.button("Reset All Data", type="secondary"):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('DELETE FROM employees')
            c.execute('DELETE FROM transactions')
            c.execute('DELETE FROM expenses')
            conn.commit()
            conn.close()
            st.success("All data has been reset!")
            st.rerun()

def render_settings(settings_manager):
    st.markdown('<div class="sub-header">⚙️ System Settings</div>', unsafe_allow_html=True)
    
    settings = settings_manager.get_settings()
    
    with st.form("settings_form"):
        st.markdown("### Company Information")
        
        company_name = st.text_input("Company Name", value=settings['company_name'])
        company_address = st.text_area("Company Address", value=settings['company_address'])
        company_phone = st.text_input("Phone Number", value=settings['company_phone'])
        company_email = st.text_input("Email Address", value=settings['company_email'])
        
        st.markdown("### System Settings")
        currency = st.selectbox("Currency", ["PKR", "USD", "EUR", "GBP"], 
                               index=["PKR", "USD", "EUR", "GBP"].index(settings['currency']))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Save Settings", use_container_width=True):
                settings_manager.update_settings(company_name, company_address, company_phone, company_email, currency)
                st.success("Settings saved successfully!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("🔄 Reset to Default", use_container_width=True):
                settings_manager.update_settings(
                    "HMD Solutions", 
                    "Karachi, Pakistan", 
                    "+92-3207429422", 
                    "info@hmdsolutions.com", 
                    "PKR"
                )
                st.success("Settings reset to default!")
                st.rerun()

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

def main():
    st.markdown('<div class="main-header">HMD Solutions - Business Management System</div>', unsafe_allow_html=True)

    # Initialize systems
    ledger = EmployeeLedger()
    expense_tracker = ExpenseTracker()
    pdf_generator = PDFGenerator()
    settings_manager = SettingsManager()

    # Sidebar navigation
    st.sidebar.markdown("""
    <div style='background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center;'>
        <h2>🚀 Navigation</h2>
    </div>
    """, unsafe_allow_html=True)

    app_mode = st.sidebar.selectbox(
        "Choose Application",
        ["🏠 Dashboard", "👥 Employee Ledger", "💰 Expense Management", "📊 Reports & Analytics", "📁 Data Management", "⚙️ Settings"]
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
        render_dashboard(ledger, expense_tracker, pdf_generator)
    elif app_mode == "👥 Employee Ledger":
        render_employee_ledger(ledger, pdf_generator)
    elif app_mode == "💰 Expense Management":
        render_expense_dashboard(expense_tracker, ledger, pdf_generator)
    elif app_mode == "📊 Reports & Analytics":
        render_reports_analytics(ledger, expense_tracker, pdf_generator)
    elif app_mode == "📁 Data Management":
        render_data_management(ledger, expense_tracker)
    else:  # Settings
        render_settings(settings_manager)

if __name__ == "__main__":
    main()
    render_footer()
