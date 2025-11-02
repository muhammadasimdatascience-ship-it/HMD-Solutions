import streamlit as st
import pandas as pd
import json
import datetime
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import io
import base64
from fpdf import FPDF
import tempfile
import os
import sqlite3
import uuid
from PIL import Image

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

    def get_employees(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM employees ORDER BY created_at DESC')
        employees = [{'id': row[0], 'name': row[1], 'initial_balance': row[2], 'created_at': row[3]}
                     for row in c.fetchall()]
        conn.close()
        return employees

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


class PDFGenerator:
    def __init__(self):
        self.logo_path = "logo.png"
        self.signature_path = "Asim_Signature.jpg"

    def image_to_base64(self, image_path):
        """Convert image to base64 string"""
        try:
            if os.path.exists(image_path):
                with open(image_path, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode('utf-8')
        except:
            pass
        return None

    def generate_employee_ledger_pdf(self, employee_name, transactions, summary, start_date=None, end_date=None):
        pdf = FPDF()
        pdf.add_page()

        # Add logo if exists
        if os.path.exists(self.logo_path):
            pdf.image(self.logo_path, x=10, y=8, w=30)

        # Header with company name
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 10, 'HMD Solutions', 0, 1, 'C')
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
        pdf.cell(0, 8, f'Total Expenses: PKR {summary["total_expenses"]:.2f}', 0, 1)
        pdf.cell(0, 8, f'Total Payments: PKR {summary["total_payments"]:.2f}', 0, 1)

        balance_status = '(Due)' if summary['balance'] > 0 else '(Advance)' if summary['balance'] < 0 else ''
        balance_color = 255, 0, 0 if summary['balance'] > 0 else 0, 128, 0
        pdf.set_text_color(*balance_color)
        pdf.cell(0, 8, f'Balance: PKR {abs(summary["balance"]):.2f} {balance_status}', 0, 1)
        pdf.set_text_color(0, 0, 0)
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
                pdf.cell(30, 8, f"PKR {t['amount']:.2f}", 1, 1, 'C', True)
                pdf.set_text_color(0, 0, 0)
        else:
            pdf.cell(0, 10, 'No transactions found for the selected period.', 0, 1)

        # Footer with signatures
        pdf.ln(15)

        # Add signature if exists
        if os.path.exists(self.signature_path):
            try:
                pdf.image(self.signature_path, x=120, y=pdf.get_y(), w=30)
                pdf.ln(25)
            except:
                pass

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(80, 10, '________________________', 0, 0, 'C')
        pdf.cell(40, 10, '', 0, 0)
        pdf.cell(80, 10, '________________________', 0, 1, 'C')

        pdf.set_font('Arial', '', 10)
        pdf.cell(80, 5, 'Employee Signature', 0, 0, 'C')
        pdf.cell(40, 5, '', 0, 0)
        pdf.cell(80, 5, 'Manager Signature', 0, 1, 'C')

        pdf.ln(10)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 10, 'Generated by HMD Solutions Business Management System', 0, 1, 'C')

        return pdf

    def generate_expense_report_pdf(self, expenses, report_type="All", employee_name=None, start_date=None,
                                    end_date=None):
        pdf = FPDF()
        pdf.add_page()

        # Add logo if exists
        if os.path.exists(self.logo_path):
            pdf.image(self.logo_path, x=10, y=8, w=30)

        # Header
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 10, 'HMD Solutions', 0, 1, 'C')
        pdf.set_font('Arial', 'B', 16)

        if report_type == "employee" and employee_name:
            pdf.cell(0, 10, f'Expense Report - {employee_name}', 0, 1, 'C')
        else:
            pdf.cell(0, 10, f'{report_type.title()} Expense Report', 0, 1, 'C')

        # Report period
        pdf.set_font('Arial', 'I', 12)
        period_text = f"Period: {start_date} to {end_date}" if start_date and end_date else "All Time Period"
        pdf.cell(0, 10, period_text, 0, 1, 'C')
        pdf.ln(5)

        # Report details
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f'Report Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1)
        pdf.ln(5)

        # Summary
        total_amount = sum(e['amount'] for e in expenses)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f'Total Amount: PKR {total_amount:.2f}', 0, 1)
        pdf.ln(5)

        # Expenses table
        if expenses:
            pdf.set_font('Arial', 'B', 12)

            # Table header
            pdf.set_fill_color(79, 129, 189)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(25, 10, 'Date', 1, 0, 'C', True)
            pdf.cell(25, 10, 'Type', 1, 0, 'C', True)
            pdf.cell(60, 10, 'Description', 1, 0, 'C', True)
            pdf.cell(30, 10, 'Employee', 1, 0, 'C', True)
            pdf.cell(30, 10, 'Amount', 1, 1, 'C', True)

            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 10)
            for idx, e in enumerate(expenses):
                # Alternate row colors
                if idx % 2 == 0:
                    pdf.set_fill_color(240, 240, 240)
                else:
                    pdf.set_fill_color(255, 255, 255)

                pdf.cell(25, 8, e['date'], 1, 0, 'C', True)
                pdf.cell(25, 8, e['type'].title(), 1, 0, 'C', True)
                pdf.cell(60, 8, e['description'][:35], 1, 0, 'C', True)
                pdf.cell(30, 8, e['employee_name'] or 'N/A', 1, 0, 'C', True)
                pdf.cell(30, 8, f"PKR {e['amount']:.2f}", 1, 1, 'C', True)
        else:
            pdf.cell(0, 10, 'No expenses found for the selected period.', 0, 1)

        # Footer with signatures
        pdf.ln(15)

        # Add signature if exists
        if os.path.exists(self.signature_path):
            try:
                pdf.image(self.signature_path, x=120, y=pdf.get_y(), w=30)
                pdf.ln(25)
            except:
                pass

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(80, 10, '________________________', 0, 0, 'C')
        pdf.cell(40, 10, '', 0, 0)
        pdf.cell(80, 10, '________________________', 0, 1, 'C')

        pdf.set_font('Arial', '', 10)
        pdf.cell(80, 5, 'Prepared By', 0, 0, 'C')
        pdf.cell(40, 5, '', 0, 0)
        pdf.cell(80, 5, 'Approved By', 0, 1, 'C')

        pdf.ln(10)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 10, 'Generated by HMD Solutions Business Management System', 0, 1, 'C')

        return pdf


def main():
    st.markdown('<div class="main-header">HMD Solutions - Business Management System</div>', unsafe_allow_html=True)

    # Initialize systems
    ledger = EmployeeLedger()
    expense_tracker = ExpenseTracker()
    pdf_generator = PDFGenerator()

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
        render_employee_ledger(ledger, pdf_generator)
    elif app_mode == "💰 Expense Management":
        render_expense_dashboard(expense_tracker, pdf_generator, ledger)
    elif app_mode == "📊 Reports & Analytics":
        render_reports_analytics(ledger, expense_tracker, pdf_generator)
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

    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("➕ Add New Employee", use_container_width=True):
            st.session_state.show_employee_form = True
            st.rerun()

    with col2:
        if st.button("💸 Record Transaction", use_container_width=True):
            st.session_state.show_transaction_form = True
            st.rerun()

    with col3:
        if st.button("📊 View Reports", use_container_width=True):
            st.session_state.active_tab = "Reports & Analytics"
            st.rerun()


def render_employee_ledger(ledger, pdf_generator):
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

                    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
                    col1.write(f"**{emp['name']}**")
                    col2.write(f"Expenses: PKR {summary['total_expenses']:.2f}")
                    col3.write(f"Payments: PKR {summary['total_payments']:.2f}")

                    balance_color = "negative" if summary['balance'] > 0 else "positive" if summary[
                                                                                                'balance'] < 0 else ""
                    balance_text = f"PKR {abs(summary['balance']):.2f} {'(Due)' if summary['balance'] > 0 else '(Advance)' if summary['balance'] < 0 else ''}"
                    col4.markdown(f"<div class='{balance_color}'>Balance: {balance_text}</div>", unsafe_allow_html=True)

                    # Action buttons
                    if col5.button("View Details", key=f"view_{emp['id']}"):
                        st.session_state.selected_employee = emp['id']
                        st.session_state.selected_employee_name = emp['name']
                        st.rerun()

                    st.divider()
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
                else:
                    st.error("Please enter employee name")

    with tab3:
        st.markdown("### 💰 Record Transaction")
        with st.form("transaction_form", clear_on_submit=True):
            employees = ledger.get_employees()
            if employees:
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
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    detail_start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30),
                                                      key="detail_start")
                with col2:
                    detail_end_date = st.date_input("End Date", value=datetime.now(), key="detail_end")
                with col3:
                    if st.button("📥 Download PDF", use_container_width=True):
                        download_employee_pdf(ledger, pdf_generator, emp_id, selected_emp_name,
                                              detail_start_date.isoformat(), detail_end_date.isoformat())

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
                'Date': t['date'],
                'Type': t['type'].title(),
                'Description': t['description'],
                'Amount': t['amount'],
                'Balance': running_balance
            })

        # Display detailed transactions
        for idx, row in enumerate(detailed_data):
            col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 2])
            col1.write(row['Date'])
            col2.write(row['Type'])
            col3.write(row['Description'])
            col4.write(f"PKR {row['Amount']:.2f}")

            balance_color = "negative" if row['Balance'] > 0 else "positive" if row['Balance'] < 0 else ""
            balance_text = f"PKR {abs(row['Balance']):.2f} {'(Due)' if row['Balance'] > 0 else '(Advance)' if row['Balance'] < 0 else ''}"
            col5.markdown(f"<div class='{balance_color}'>{balance_text}</div>", unsafe_allow_html=True)

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


def download_employee_pdf(ledger, pdf_generator, employee_id, employee_name, start_date=None, end_date=None):
    transactions = ledger.get_transactions(employee_id, start_date, end_date)
    summary = ledger.get_employee_summary(employee_id, start_date, end_date)

    pdf = pdf_generator.generate_employee_ledger_pdf(employee_name, transactions, summary, start_date, end_date)

    # Save PDF to bytes
    pdf_output = pdf.output(dest='S').encode('latin1')

    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_output,
        file_name=f"employee_ledger_{employee_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )


def render_expense_dashboard(expense_tracker, pdf_generator, ledger):
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

        # Download buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📥 All Expenses PDF", use_container_width=True):
                download_expense_pdf(expense_tracker, pdf_generator, "all",
                                     exp_start_date.isoformat(), exp_end_date.isoformat())
        with col2:
            if st.button("🏢 Company Expenses PDF", use_container_width=True):
                download_expense_pdf(expense_tracker, pdf_generator, "company",
                                     exp_start_date.isoformat(), exp_end_date.isoformat())
        with col3:
            if st.button("👤 Employee Expenses PDF", use_container_width=True):
                download_expense_pdf(expense_tracker, pdf_generator, "employee",
                                     exp_start_date.isoformat(), exp_end_date.isoformat())

        # Expense analysis charts
        expenses = expense_tracker.get_expenses(start_date=exp_start_date.isoformat(),
                                                end_date=exp_end_date.isoformat())
        if expenses:
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

            # Display expenses
            for expense in sorted(filtered_expenses, key=lambda x: x['date'], reverse=True)[:20]:
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 3, 2, 2, 1])
                    col1.write(expense['date'])
                    col2.write(f"{expense['type'].title()}")
                    col3.write(expense['description'])
                    if expense['type'] == 'employee' and expense['employee_name']:
                        col4.write(f"{expense['employee_name']}")
                    else:
                        col4.write("N/A")
                    col5.write(f"PKR {expense['amount']:.2f}")

                    if col6.button("🗑️", key=f"del_exp_{expense['id']}"):
                        expense_tracker.delete_expense(expense['id'])
                        st.rerun()
                    st.divider()
        else:
            st.info("No expenses recorded yet. Add expenses to see the list.")


def download_expense_pdf(expense_tracker, pdf_generator, expense_type, start_date=None, end_date=None):
    expenses = expense_tracker.get_expenses(
        expense_type=expense_type if expense_type != 'all' else None,
        start_date=start_date,
        end_date=end_date
    )

    pdf = pdf_generator.generate_expense_report_pdf(expenses, expense_type, start_date=start_date, end_date=end_date)
    pdf_output = pdf.output(dest='S').encode('latin1')

    st.download_button(
        label=f"📥 Download {expense_type.title()} Expenses PDF",
        data=pdf_output,
        file_name=f"{expense_type}_expenses_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )


def render_reports_analytics(ledger, expense_tracker, pdf_generator):
    st.markdown('<div class="sub-header">📊 Reports & Analytics</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 Analytics Dashboard", "📋 Employee Reports", "💰 Expense Reports"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 👥 Employee Analytics")
            employees = ledger.get_employees()

            if employees:
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
            else:
                st.info("No employee data available")

        with col2:
            st.markdown("### 💰 Expense Analytics")
            expenses = expense_tracker.get_expenses()

            if expenses:
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
            else:
                st.info("No expense data available")

    with tab2:
        st.markdown("### 📋 Employee Reports")

        employees = ledger.get_employees()
        if employees:
            col1, col2, col3 = st.columns(3)

            with col1:
                selected_employee = st.selectbox("Select Employee", [emp['name'] for emp in employees],
                                                 key="report_emp")
            with col2:
                emp_start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30),
                                               key="emp_report_start")
            with col3:
                emp_end_date = st.date_input("End Date", value=datetime.now(), key="emp_report_end")

            if st.button("Generate Employee Report PDF", use_container_width=True):
                emp_id = next(emp['id'] for emp in employees if emp['name'] == selected_employee)
                download_employee_pdf(ledger, pdf_generator, emp_id, selected_employee,
                                      emp_start_date.isoformat(), emp_end_date.isoformat())
        else:
            st.info("No employees available for reports")

    with tab3:
        st.markdown("### 💰 Expense Reports")

        col1, col2, col3 = st.columns(3)

        with col1:
            expense_types = ["All", "Company", "Employee"]
            selected_type = st.selectbox("Select Expense Type", expense_types, key="report_exp")
        with col2:
            exp_start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30),
                                           key="exp_report_start")
        with col3:
            exp_end_date = st.date_input("End Date", value=datetime.now(), key="exp_report_end")

        if st.button("Generate Expense Report PDF", use_container_width=True):
            download_expense_pdf(expense_tracker, pdf_generator, selected_type.lower(),
                                 exp_start_date.isoformat(), exp_end_date.isoformat())


def render_data_management(ledger, expense_tracker):
    st.markdown('<div class="sub-header">📁 Data Management</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📤 Export Data", "📥 Import Data"])

    with tab1:
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

    with tab2:
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
            except Exception as e:
                st.error(f"Error reading file: {e}")

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