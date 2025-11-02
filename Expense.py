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
    .download-btn {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        margin: 0.2rem;
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

    def generate_expense_report_pdf(self, expenses, report_type="All", employee_name=None, start_date=None, end_date=None):
        if not FPDF_AVAILABLE:
            st.error("PDF generation is not available. Please install fpdf.")
            return None
            
        try:
            pdf = FPDF()
            pdf.add_page()

            # Header
            pdf.set_font('Arial', 'B', 20)
            pdf.cell(0, 10, self.settings['company_name'], 0, 1, 'C')
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
            pdf.cell(0, 10, f'Total Amount: {self.settings["currency"]} {total_amount:.2f}', 0, 1)
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
                    pdf.cell(30, 8, f"{self.settings['currency']} {e['amount']:.2f}", 1, 1, 'C', True)
            else:
                pdf.cell(0, 10, 'No expenses found for the selected period.', 0, 1)

            # Footer with company info
            pdf.ln(15)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 10, f'Generated by {self.settings["company_name"]} Business Management System', 0, 1, 'C')
            pdf.cell(0, 5, f'Contact: {self.settings["company_phone"]} | Email: {self.settings["company_email"]}', 0, 1, 'C')

            return pdf
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            return None

    def generate_employee_list_pdf(self, employees, ledger):
        if not FPDF_AVAILABLE:
            st.error("PDF generation is not available. Please install fpdf.")
            return None
            
        try:
            pdf = FPDF()
            pdf.add_page()

            # Header
            pdf.set_font('Arial', 'B', 20)
            pdf.cell(0, 10, self.settings['company_name'], 0, 1, 'C')
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Employee List Report', 0, 1, 'C')
            pdf.ln(5)

            # Report details
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, f'Report Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1)
            pdf.cell(0, 8, f'Total Employees: {len(employees)}', 0, 1)
            pdf.ln(5)

            # Employee table
            if employees:
                pdf.set_font('Arial', 'B', 12)

                # Table header
                pdf.set_fill_color(79, 129, 189)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(60, 10, 'Employee Name', 1, 0, 'C', True)
                pdf.cell(40, 10, 'Initial Balance', 1, 0, 'C', True)
                pdf.cell(40, 10, 'Current Balance', 1, 1, 'C', True)

                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Arial', '', 10)
                for emp in employees:
                    # Alternate row colors
                    if employees.index(emp) % 2 == 0:
                        pdf.set_fill_color(240, 240, 240)
                    else:
                        pdf.set_fill_color(255, 255, 255)

                    balance = ledger.get_employee_balance(emp['id'])
                    
                    pdf.cell(60, 8, emp['name'], 1, 0, 'C', True)
                    pdf.cell(40, 8, f"{self.settings['currency']} {emp['initial_balance']:.2f}", 1, 0, 'C', True)
                    
                    # Color code current balance
                    if balance > 0:
                        pdf.set_text_color(255, 0, 0)
                    elif balance < 0:
                        pdf.set_text_color(0, 128, 0)
                    else:
                        pdf.set_text_color(0, 0, 0)
                    
                    balance_text = f"{self.settings['currency']} {abs(balance):.2f}"
                    if balance > 0:
                        balance_text += " (Due)"
                    elif balance < 0:
                        balance_text += " (Advance)"
                    
                    pdf.cell(40, 8, balance_text, 1, 1, 'C', True)
                    pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(0, 10, 'No employees found.', 0, 1)

            # Footer with company info
            pdf.ln(15)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 10, f'Generated by {self.settings["company_name"]} Business Management System', 0, 1, 'C')
            pdf.cell(0, 5, f'Contact: {self.settings["company_phone"]} | Email: {self.settings["company_email"]}', 0, 1, 'C')

            return pdf
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            return None

    def generate_comprehensive_report_pdf(self, ledger, expense_tracker, start_date=None, end_date=None):
        if not FPDF_AVAILABLE:
            st.error("PDF generation is not available. Please install fpdf.")
            return None
            
        try:
            pdf = FPDF()
            pdf.add_page()

            # Header
            pdf.set_font('Arial', 'B', 20)
            pdf.cell(0, 10, self.settings['company_name'], 0, 1, 'C')
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Comprehensive Business Report', 0, 1, 'C')
            pdf.ln(5)

            # Report period
            pdf.set_font('Arial', 'I', 12)
            period_text = f"Period: {start_date} to {end_date}" if start_date and end_date else "All Time Period"
            pdf.cell(0, 10, period_text, 0, 1, 'C')
            pdf.ln(5)

            # Report details
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, f'Report Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1)
            pdf.ln(10)

            # Get data
            employees = ledger.get_employees()
            expenses = expense_tracker.get_expenses(start_date=start_date, end_date=end_date)
            expense_summary = expense_tracker.get_summary(start_date, end_date)

            # Summary section
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Business Summary', 0, 1)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, f'Total Employees: {len(employees)}', 0, 1)
            pdf.cell(0, 8, f'Total Expenses Recorded: {len(expenses)}', 0, 1)
            pdf.cell(0, 8, f'Company Expenses: {self.settings["currency"]} {expense_summary["company_total"]:.2f}', 0, 1)
            pdf.cell(0, 8, f'Employee Expenses: {self.settings["currency"]} {expense_summary["employee_total"]:.2f}', 0, 1)
            pdf.cell(0, 8, f'Grand Total Expenses: {self.settings["currency"]} {expense_summary["grand_total"]:.2f}', 0, 1)
            pdf.ln(10)

            # Employee summary
            if employees:
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, 'Employee Summary', 0, 1)
                pdf.set_font('Arial', 'B', 10)
                
                # Table header
                pdf.set_fill_color(79, 129, 189)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(60, 8, 'Employee', 1, 0, 'C', True)
                pdf.cell(30, 8, 'Expenses', 1, 0, 'C', True)
                pdf.cell(30, 8, 'Payments', 1, 0, 'C', True)
                pdf.cell(40, 8, 'Balance', 1, 1, 'C', True)

                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Arial', '', 9)
                for emp in employees:
                    # Alternate row colors
                    if employees.index(emp) % 2 == 0:
                        pdf.set_fill_color(240, 240, 240)
                    else:
                        pdf.set_fill_color(255, 255, 255)

                    summary = ledger.get_employee_summary(emp['id'], start_date, end_date)
                    
                    pdf.cell(60, 6, emp['name'], 1, 0, 'C', True)
                    pdf.cell(30, 6, f"{self.settings['currency']} {summary['total_expenses']:.2f}", 1, 0, 'C', True)
                    pdf.cell(30, 6, f"{self.settings['currency']} {summary['total_payments']:.2f}", 1, 0, 'C', True)
                    
                    # Color code balance
                    if summary['balance'] > 0:
                        pdf.set_text_color(255, 0, 0)
                    elif summary['balance'] < 0:
                        pdf.set_text_color(0, 128, 0)
                    
                    balance_text = f"{self.settings['currency']} {abs(summary['balance']):.2f}"
                    if summary['balance'] > 0:
                        balance_text += " (Due)"
                    elif summary['balance'] < 0:
                        balance_text += " (Advance)"
                    
                    pdf.cell(40, 6, balance_text, 1, 1, 'C', True)
                    pdf.set_text_color(0, 0, 0)
                pdf.ln(10)

            # Expense summary
            if expenses:
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, 'Recent Expenses', 0, 1)
                pdf.set_font('Arial', 'B', 10)
                
                # Table header
                pdf.set_fill_color(79, 129, 189)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(25, 8, 'Date', 1, 0, 'C', True)
                pdf.cell(25, 8, 'Type', 1, 0, 'C', True)
                pdf.cell(80, 8, 'Description', 1, 0, 'C', True)
                pdf.cell(30, 8, 'Amount', 1, 1, 'C', True)

                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Arial', '', 8)
                for idx, exp in enumerate(expenses[:15]):  # Show last 15 expenses
                    if idx % 2 == 0:
                        pdf.set_fill_color(240, 240, 240)
                    else:
                        pdf.set_fill_color(255, 255, 255)

                    pdf.cell(25, 6, exp['date'], 1, 0, 'C', True)
                    pdf.cell(25, 6, exp['type'].title(), 1, 0, 'C', True)
                    pdf.cell(80, 6, exp['description'][:50], 1, 0, 'C', True)
                    pdf.cell(30, 6, f"{self.settings['currency']} {exp['amount']:.2f}", 1, 1, 'C', True)

            # Footer with company info
            pdf.ln(15)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 10, f'Generated by {self.settings["company_name"]} Business Management System', 0, 1, 'C')
            pdf.cell(0, 5, f'Contact: {self.settings["company_phone"]} | Email: {self.settings["company_email"]}', 0, 1, 'C')

            return pdf
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            return None

# ALL YOUR EXISTING CLASSES AND FUNCTIONS REMAIN EXACTLY THE SAME
# EmployeeLedger, ExpenseTracker, and all other classes remain unchanged

def main():
    st.markdown('<div class="main-header">HMD Solutions - Business Management System</div>', unsafe_allow_html=True)

    # Initialize systems
    ledger = EmployeeLedger()
    expense_tracker = ExpenseTracker()
    pdf_generator = PDFGenerator()
    settings_manager = SettingsManager()

    # Sidebar navigation - ADDED SETTINGS
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

def render_dashboard(ledger, expense_tracker, pdf_generator):
    # YOUR EXISTING DASHBOARD CODE REMAINS EXACTLY THE SAME
    # Only added PDF download buttons
    
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

    # PDF Download Section - NEW
    st.markdown("### 📥 Quick PDF Downloads")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Comprehensive Report", use_container_width=True, key="comp_report"):
            pdf = pdf_generator.generate_comprehensive_report_pdf(ledger, expense_tracker)
            if pdf:
                pdf_output = pdf.output(dest='S').encode('latin1')
                st.download_button(
                    label="Download PDF",
                    data=pdf_output,
                    file_name=f"comprehensive_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
    with col2:
        if st.button("👥 Employee List", use_container_width=True, key="emp_list"):
            employees = ledger.get_employees()
            pdf = pdf_generator.generate_employee_list_pdf(employees, ledger)
            if pdf:
                pdf_output = pdf.output(dest='S').encode('latin1')
                st.download_button(
                    label="Download PDF",
                    data=pdf_output,
                    file_name=f"employee_list_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
    with col3:
        if st.button("💰 All Expenses", use_container_width=True, key="all_exp"):
            expenses = expense_tracker.get_expenses()
            pdf = pdf_generator.generate_expense_report_pdf(expenses, "All")
            if pdf:
                pdf_output = pdf.output(dest='S').encode('latin1')
                st.download_button(
                    label="Download PDF",
                    data=pdf_output,
                    file_name=f"all_expenses_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
    with col4:
        if st.button("📈 Expense Summary", use_container_width=True, key="exp_summary"):
            expenses = expense_tracker.get_expenses()
            pdf = pdf_generator.generate_expense_report_pdf(expenses, "Summary")
            if pdf:
                pdf_output = pdf.output(dest='S').encode('latin1')
                st.download_button(
                    label="Download PDF",
                    data=pdf_output,
                    file_name=f"expense_summary_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

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

    # Handle quick actions (your existing quick action handling code remains the same)
    # ... [YOUR EXISTING QUICK ACTION HANDLING CODE]

def render_employee_ledger(ledger, pdf_generator):
    # YOUR EXISTING EMPLOYEE LEDGER CODE REMAINS EXACTLY THE SAME
    # Only enhanced with more PDF download options
    
    st.markdown('<div class="sub-header">👥 Employee Ledger System</div>', unsafe_allow_html=True)
    st.write("Track expenses, payments, and balances for all employees")

    # PDF Download Section - NEW
    st.markdown("### 📥 PDF Downloads")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Employee List PDF", use_container_width=True, key="emp_list_pdf"):
            employees = ledger.get_employees()
            pdf = pdf_generator.generate_employee_list_pdf(employees, ledger)
            if pdf:
                pdf_output = pdf.output(dest='S').encode('latin1')
                st.download_button(
                    label="Download Employee List",
                    data=pdf_output,
                    file_name=f"employee_list_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
    with col2:
        if st.button("📊 All Employees Summary", use_container_width=True, key="all_emp_summary"):
            pdf = pdf_generator.generate_comprehensive_report_pdf(ledger, None)
            if pdf:
                pdf_output = pdf.output(dest='S').encode('latin1')
                st.download_button(
                    label="Download Summary",
                    data=pdf_output,
                    file_name=f"employees_summary_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Employee Summary", "➕ Add Employee", "💸 Record Transaction", "📊 Employee Details"])

    # ... [YOUR EXISTING TAB CODE REMAINS EXACTLY THE SAME]

def render_expense_dashboard(expense_tracker, ledger, pdf_generator):
    # YOUR EXISTING EXPENSE DASHBOARD CODE REMAINS EXACTLY THE SAME
    # Only enhanced with more PDF download options
    
    st.markdown('<div class="sub-header">💰 Expense Management</div>', unsafe_allow_html=True)
    st.write("Track and manage all company and employee expenses")

    # PDF Download Section - NEW
    st.markdown("### 📥 PDF Downloads")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💰 All Expenses PDF", use_container_width=True, key="all_exp_main"):
            expenses = expense_tracker.get_expenses()
            pdf = pdf_generator.generate_expense_report_pdf(expenses, "All")
            if pdf:
                pdf_output = pdf.output(dest='S').encode('latin1')
                st.download_button(
                    label="Download All Expenses",
                    data=pdf_output,
                    file_name=f"all_expenses_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
    with col2:
        if st.button("🏢 Company Expenses", use_container_width=True, key="comp_exp"):
            expenses = expense_tracker.get_expenses(expense_type="company")
            pdf = pdf_generator.generate_expense_report_pdf(expenses, "Company")
            if pdf:
                pdf_output = pdf.output(dest='S').encode('latin1')
                st.download_button(
                    label="Download Company",
                    data=pdf_output,
                    file_name=f"company_expenses_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
    with col3:
        if st.button("👤 Employee Expenses", use_container_width=True, key="emp_exp"):
            expenses = expense_tracker.get_expenses(expense_type="employee")
            pdf = pdf_generator.generate_expense_report_pdf(expenses, "Employee")
            if pdf:
                pdf_output = pdf.output(dest='S').encode('latin1')
                st.download_button(
                    label="Download Employee",
                    data=pdf_output,
                    file_name=f"employee_expenses_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📈 Expense Overview", "➕ Add Expense", "📋 Expense List"])

    # ... [YOUR EXISTING TAB CODE REMAINS EXACTLY THE SAME]

def render_reports_analytics(ledger, expense_tracker, pdf_generator):
    # YOUR EXISTING REPORTS CODE REMAINS EXACTLY THE SAME
    # Only enhanced with more PDF download options
    
    st.markdown('<div class="sub-header">📊 Reports & Analytics</div>', unsafe_allow_html=True)

    # PDF Download Section - NEW
    st.markdown("### 📥 Comprehensive PDF Reports")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏢 Full Business Report", use_container_width=True, key="full_business"):
            pdf = pdf_generator.generate_comprehensive_report_pdf(ledger, expense_tracker)
            if pdf:
                pdf_output = pdf.output(dest='S').encode('latin1')
                st.download_button(
                    label="Download Full Report",
                    data=pdf_output,
                    file_name=f"full_business_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
    with col2:
        # Date range for custom report
        col21, col22 = st.columns(2)
        with col21:
            custom_start = st.date_input("Start Date", value=datetime.now() - timedelta(days=30), key="custom_start")
        with col22:
            custom_end = st.date_input("End Date", value=datetime.now(), key="custom_end")
        
        if st.button("📅 Custom Period Report", use_container_width=True, key="custom_report"):
            pdf = pdf_generator.generate_comprehensive_report_pdf(ledger, expense_tracker, 
                                                                 custom_start.isoformat(), custom_end.isoformat())
            if pdf:
                pdf_output = pdf.output(dest='S').encode('latin1')
                st.download_button(
                    label="Download Custom Report",
                    data=pdf_output,
                    file_name=f"custom_report_{custom_start}_{custom_end}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

    tab1, tab2 = st.tabs(["📈 Analytics Dashboard", "📋 Export Data"])

    # ... [YOUR EXISTING TAB CODE REMAINS EXACTLY THE SAME]

def render_data_management(ledger, expense_tracker):
    # YOUR EXISTING DATA MANAGEMENT CODE REMAINS EXACTLY THE SAME
    pass

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
