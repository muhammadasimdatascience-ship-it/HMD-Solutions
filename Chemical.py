import streamlit as st
import pandas as pd
import json
from datetime import datetime
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import os
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import tempfile
import csv
import zipfile

# Page configuration with optimized settings
st.set_page_config(
    page_title="Green - Chemical Management System",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for white background and blue theme
st.markdown(
    """
    <style>
    /* App background - WHITE */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Main container */
    .main-container {
        background: #FFFFFF;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0, 78, 146, 0.1);
        border: 2px solid #004e92;
    }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #004e92 0%, #0077b6 100%);
        color: #FFFFFF;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0, 78, 146, 0.3);
        border: 2px solid #004e92;
    }

    /* Section header */
    .section-header {
        background: linear-gradient(135deg, #004e92 0%, #0077b6 100%);
        color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0, 78, 146, 0.2);
        border: 2px solid #004e92;
    }

    /* Cards */
    .card {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0, 78, 146, 0.1);
        border-left: 5px solid #004e92;
        border: 1px solid #004e92;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 78, 146, 0.2);
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #004e92 0%, #0077b6 100%);
        color: #FFFFFF;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0, 78, 146, 0.3);
        margin: 10px;
        border: 2px solid #004e92;
    }

    /* Vendor & Payment Cards */
    .vendor-card {
        background: linear-gradient(135deg, #004e92 0%, #0077b6 100%);
        color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 78, 146, 0.2);
        border: 1px solid #004e92;
    }

    .payment-card {
        background: linear-gradient(135deg, #004e92 0%, #0077b6 100%);
        color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 78, 146, 0.2);
        border: 1px solid #004e92;
    }

    /* Buttons - BLUE and GREEN with WHITE BOLD TEXT */
    .stButton>button {
        background: linear-gradient(135deg, #004e92 0%, #0077b6 100%);
        color: #FFFFFF !important;
        border: 2px solid #004e92;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 700 !important;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 78, 146, 0.3);
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #0077b6 0%, #004e92 100%);
        border: 2px solid #004e92;
        color: #FFFFFF !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 78, 146, 0.4);
    }

    /* Green buttons */
    .green-button>button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
        color: #FFFFFF !important;
        border: 2px solid #28a745 !important;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 700 !important;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
    }

    .green-button>button:hover {
        background: linear-gradient(135deg, #20c997 0%, #28a745 100%) !important;
        border: 2px solid #28a745 !important;
        color: #FFFFFF !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
    }

    /* Sidebar */
    .css-1d391kg, .sidebar .sidebar-content {
        background: linear-gradient(180deg, #004e92 0%, #0077b6 100%);
        border-right: 2px solid #004e92;
    }

    /* DataFrame */
    .stDataFrame {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(0, 78, 146, 0.1);
        border: 1px solid #004e92;
    }

    /* Forms */
    .stForm {
        background: #FFFFFF;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 78, 146, 0.1);
        margin: 20px 0;
        border: 1px solid #004e92;
    }

    /* Input fields with blue outline */
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #FFFFFF !important;
        border-radius: 8px;
        color: #000000 !important;
        border: 2px solid #004e92 !important;
        font-weight: 500;
    }

    .stSelectbox > div > div:focus,
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border: 2px solid #0077b6 !important;
        box-shadow: 0 0 0 1px #0077b6;
    }

    /* Message boxes */
    .stSuccess {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: #FFFFFF;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #28a745;
    }

    .stWarning {
        background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
        color: #000000;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #ffc107;
    }

    .stError {
        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        color: #FFFFFF;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #dc3545;
    }

    .stInfo {
        background: linear-gradient(135deg, #004e92 0%, #0077b6 100%);
        color: #FFFFFF;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #004e92;
    }

    /* Metric container */
    [data-testid="metric-container"] {
        background: #FFFFFF;
        border: 2px solid #004e92;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 78, 146, 0.1);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #004e92 0%, #0077b6 100%) !important;
        color: #FFFFFF !important;
        border-radius: 8px;
        border: 1px solid #004e92;
        font-weight: 700;
    }

    /* Table headers in PDF reports */
    .table-header {
        background: #004e92 !important;
        color: #FFFFFF !important;
    }

    /* Blue outline for all containers */
    .css-1r6slb0, .css-12oz5g7, .block-container {
        border: none;
    }

    /* Sidebar text color */
    .css-1d391kg p, .css-1d391kg label {
        color: #FFFFFF !important;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Data persistence functions
def save_data():
    """Save all session state data to JSON files"""
    try:
        data = {
            'chemicals': st.session_state.chemicals,
            'packaging_materials': st.session_state.packaging_materials,
            'vendor_ledger': st.session_state.vendor_ledger,
            'vendor_payments': st.session_state.vendor_payments,
            'production_history': st.session_state.production_history,
            'settings': st.session_state.settings
        }
        
        with open('green_data.json', 'w') as f:
            json.dump(data, f, indent=4)
        
        # Also create backup with timestamp
        backup_filename = f"backup/green_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('backup', exist_ok=True)
        with open(backup_filename, 'w') as f:
            json.dump(data, f, indent=4)
            
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

def load_data():
    """Load all data from JSON files"""
    try:
        if os.path.exists('green_data.json'):
            with open('green_data.json', 'r') as f:
                data = json.load(f)
                
            st.session_state.chemicals = data.get('chemicals', [])
            st.session_state.packaging_materials = data.get('packaging_materials', {})
            st.session_state.vendor_ledger = data.get('vendor_ledger', [])
            st.session_state.vendor_payments = data.get('vendor_payments', [])
            st.session_state.production_history = data.get('production_history', [])
            st.session_state.settings = data.get('settings', {
                'company_name': "Green",
                'default_batch_size': 500,
                'low_stock_threshold': 5.0,
                'packaging_low_stock': 10
            })
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

def auto_save():
    """Auto-save data with user feedback"""
    save_data()
    st.toast("💾 Data saved successfully!", icon="✅")

# Initialize session state for data persistence
if 'chemicals' not in st.session_state:
    st.session_state.chemicals = []

if 'packaging_materials' not in st.session_state:
    st.session_state.packaging_materials = {}

if 'vendor_ledger' not in st.session_state:
    st.session_state.vendor_ledger = []

if 'vendor_payments' not in st.session_state:
    st.session_state.vendor_payments = []

if 'production_history' not in st.session_state:
    st.session_state.production_history = []

if 'settings' not in st.session_state:
    st.session_state.settings = {
        'company_name': "Green",
        'default_batch_size': 500,
        'low_stock_threshold': 5.0,
        'packaging_low_stock': 10
    }

if 'editing_chemical' not in st.session_state:
    st.session_state.editing_chemical = None

if 'editing_vendor' not in st.session_state:
    st.session_state.editing_vendor = None

if 'editing_payment' not in st.session_state:
    st.session_state.editing_payment = None

# Load data on startup
load_data()

# Cache product formulas for better performance
@st.cache_data
def get_product_formulas():
    return {
        "NETONIL": [
            {"chemical_name": "Butyric Acid", "amount_per_550": 200.00},
            {"chemical_name": "Phosphoric Acid", "amount_per_550": 100.00},
            {"chemical_name": "Propanic Acid", "amount_per_550": 25.00},
            {"chemical_name": "Formic Acid", "amount_per_550": 210.00},
            {"chemical_name": "Lactic Acid", "amount_per_550": 25.00},
            {"chemical_name": "Acetic Acid", "amount_per_550": 35.00},
            {"chemical_name": "Copper Sulphate", "amount_per_550": 25.00},
            {"chemical_name": "Citric Acid", "amount_per_550": 50.00}
        ],
        "URIVIT": [
            {"chemical_name": "Sodium Benzoate", "amount_per_300": 150.00},
            {"chemical_name": "Vitamin A", "amount_per_300": 0.09},
            {"chemical_name": "Vitamin E Powder", "amount_per_300": 0.75},
            {"chemical_name": "Vitamin C", "amount_per_300": 0.75},
            {"chemical_name": "Vitamin K3", "amount_per_300": 0.30},
            {"chemical_name": "Artichoke", "amount_per_300": 1.80},
            {"chemical_name": "Dextoxirose", "amount_per_300": 250.00}
        ],
        "DEXTOXI-VIT": [
            {"chemical_name": "Slymarine", "amount_per_500": 5.00},
            {"chemical_name": "Choline Chloride", "amount_per_500": 12.00},
            {"chemical_name": "Magnesium Sulphate", "amount_per_500": 50.00},
            {"chemical_name": "Betain", "amount_per_500": 5.00},
            {"chemical_name": "Nicotinamide", "amount_per_500": 3.00},
            {"chemical_name": "Zinc-sulphate", "amount_per_500": 15.00},
            {"chemical_name": "L-Carnitine", "amount_per_500": 3.00},
            {"chemical_name": "DL-Mtahileene", "amount_per_500": 3.00},
            {"chemical_name": "Vitamin- B1", "amount_per_500": 0.00},
            {"chemical_name": "Vitamin- B6", "amount_per_500": 0.00},
            {"chemical_name": "Twin-80", "amount_per_500": 200.00},
            {"chemical_name": "Artichoke", "amount_per_500": 0.00},
            {"chemical_name": "Sorbitol", "amount_per_500": 250.00},
            {"chemical_name": "Methyl Paraben Sodium", "amount_per_500": 0.00},
            {"chemical_name": "Propyl Paraben Sodium", "amount_per_500": 0.00},
            {"chemical_name": "Sodium Benzoate", "amount_per_500": 0.00},
            {"chemical_name": "Insocitol", "amount_per_500": 2.00}
        ],
        "NURBUS": [
            {"chemical_name": "Eucalyptus oil", "amount_per_300": 25.00},
            {"chemical_name": "Menthol", "amount_per_300": 25.00},
            {"chemical_name": "Thymoil", "amount_per_300": 4.00},
            {"chemical_name": "Twin-80", "amount_per_300": 200.00},
            {"chemical_name": "Camphor", "amount_per_300": 8.00},
            {"chemical_name": "Peppermentoil", "amount_per_300": 5.00},
            {"chemical_name": "P.G", "amount_per_300": 430.00},
            {"chemical_name": "Pine Oil", "amount_per_300": 6.00}
        ],
        "KEYTON": [
            {"chemical_name": "Vitamin E Liquid", "amount_per_500": 40.00},
            {"chemical_name": "Twin-80", "amount_per_500": 136.00},
            {"chemical_name": "Citamatagoal", "amount_per_500": 0.00},
            {"chemical_name": "Vitamin C", "amount_per_500": 100.00},
            {"chemical_name": "Choline Chloride", "amount_per_500": -3.00},
            {"chemical_name": "Zinc-sulphate", "amount_per_500": 9.00},
            {"chemical_name": "Benzail Alchol", "amount_per_500": 0.00},
            {"chemical_name": "P.G", "amount_per_500": 296.00}
        ],
        "PROLYTE-C": [
            {"chemical_name": "Vitamin C", "amount_per_300": 100.00},
            {"chemical_name": "Sodium Chloride", "amount_per_300": 10.00},
            {"chemical_name": "Potasium Chloride", "amount_per_300": 2.00},
            {"chemical_name": "Sodium Citrate", "amount_per_300": 2.00},
            {"chemical_name": "Nicotinamide", "amount_per_300": -3.00},
            {"chemical_name": "Dextoxirose", "amount_per_300": 104.00}
        ],
        "ACTIVO LAZE": [
            {"chemical_name": "Lysozme", "amount_per_500": 175.00},
            {"chemical_name": "Vitamin E Powder", "amount_per_500": 10.00},
            {"chemical_name": "Vitamin C", "amount_per_500": 40.00},
            {"chemical_name": "Fe SO4", "amount_per_500": 1.00}
        ],
        "AMBROXAL(HCL)": [
            {"chemical_name": "Bromhexine", "amount_per_500": 5.00},
            {"chemical_name": "Ambroxal", "amount_per_500": 25.00},
            {"chemical_name": "Aminophylline", "amount_per_500": 25.00},
            {"chemical_name": "Guaifenesin", "amount_per_500": 25.00},
            {"chemical_name": "Ammonium Chloride", "amount_per_500": 1.00},
            {"chemical_name": "Menthol", "amount_per_500": 10.00},
            {"chemical_name": "Peppermentoil", "amount_per_500": 2.00},
            {"chemical_name": "N Acetyl L cysteine", "amount_per_500": 2.50}
        ]
    }

@st.cache_data
def get_product_packaging():
    return {
        "NETONIL": {"type": "can", "size": 25},
        "URIVIT": {"type": "box", "size": 1},
        "DEXTOXI-VIT": {"type": "bottle", "size": 1},
        "NURBUS": {"type": "bottle", "size": 1},
        "KEYTON": {"type": "bottle", "size": 1},
        "PROLYTE-C": {"type": "box", "size": 1},
        "ACTIVO LAZE": {"type": "bottle", "size": 1},
        "AMBROXAL(HCL)": {"type": "bottle", "size": 1}
    }

# Helper functions
def show_alert(message, type="info"):
    """Show alert message"""
    if type == "success":
        st.success(message)
    elif type == "warning":
        st.warning(message)
    elif type == "error":
        st.error(message)
    else:
        st.info(message)

def get_next_chemical_id():
    """Get next chemical ID"""
    if not st.session_state.chemicals:
        return 1
    return max(chem['id'] for chem in st.session_state.chemicals) + 1

def get_next_vendor_id():
    """Get next vendor transaction ID"""
    if not st.session_state.vendor_ledger:
        return 1
    return max(vendor['id'] for vendor in st.session_state.vendor_ledger) + 1

def get_next_payment_id():
    """Get next payment ID"""
    if not st.session_state.vendor_payments:
        return 1
    return max(payment['id'] for payment in st.session_state.vendor_payments) + 1

def update_dashboard():
    """Update dashboard statistics"""
    total_chemicals = len([c for c in st.session_state.chemicals if c['stock'] > 0])
    low_stock_count = len(
        [c for c in st.session_state.chemicals if 0 < c['stock'] < st.session_state.settings['low_stock_threshold']])
    out_of_stock_count = len([c for c in st.session_state.chemicals if c['stock'] <= 0])
    total_packaging = len([p for p in st.session_state.packaging_materials.values() if p['stock'] > 0])

    return total_chemicals, low_stock_count, out_of_stock_count, total_packaging

def calculate_vendor_balance(vendor_name):
    """Calculate vendor balance (total purchases - total payments)"""
    total_purchases = sum(
        ledger['total_amount']
        for ledger in st.session_state.vendor_ledger
        if ledger['vendor_name'] == vendor_name
    )
    total_payments = sum(
        payment['amount']
        for payment in st.session_state.vendor_payments
        if payment['vendor_name'] == vendor_name
    )
    return total_purchases - total_payments

def grams_to_kg(grams):
    """Convert grams to kilograms"""
    return grams / 1000.0

def kg_to_grams(kg):
    """Convert kilograms to grams"""
    return kg * 1000.0

# PDF creation functions
def add_watermark(canvas, doc):
    """Add professional watermark to PDF pages"""
    try:
        if os.path.exists("logo.png"):
            canvas.saveState()
            canvas.setFillAlpha(0.03)
            watermark = ImageReader("logo.png")
            img_width, img_height = watermark.getSize()
            aspect = img_height / float(img_width)

            display_width = 500
            display_height = display_width * aspect

            x = (doc.pagesize[0] - display_width) / 2
            y = (doc.pagesize[1] - display_height) / 2

            canvas.drawImage("logo.png", x, y, width=display_width, height=display_height)
            canvas.restoreState()
    except Exception as e:
        print(f"Watermark error: {e}")

@st.cache_data(ttl=300)
def create_vendor_ledger_pdf(vendor_type=None, vendor_name=None):
    """Create professional PDF for vendor ledger"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40, bottomMargin=40)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        textColor=colors.HexColor('#004e92'),
        alignment=1
    )

    # Filter data based on vendor type or vendor name
    if vendor_type:
        filtered_data = [v for v in st.session_state.vendor_ledger if v['vendor_type'] == vendor_type]
        title_text = f"GREEN - {vendor_type.upper()} VENDOR LEDGER REPORT"
        filtered_payments = [p for p in st.session_state.vendor_payments
                             if any(v['vendor_name'] == p['vendor_name']
                                    for v in st.session_state.vendor_ledger
                                    if v['vendor_type'] == vendor_type)]
    elif vendor_name:
        filtered_data = [v for v in st.session_state.vendor_ledger if v['vendor_name'] == vendor_name]
        title_text = f"GREEN - {vendor_name.upper()} LEDGER REPORT"
        filtered_payments = [p for p in st.session_state.vendor_payments if p['vendor_name'] == vendor_name]
    else:
        filtered_data = st.session_state.vendor_ledger
        title_text = "GREEN - COMPLETE VENDOR LEDGER REPORT"
        filtered_payments = st.session_state.vendor_payments

    # Title Section
    title = Paragraph(title_text, title_style)
    elements.append(title)

    # Company Info
    company_info = Paragraph(
        f"<b>Company:</b> Green | <b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        styles['Normal']
    )
    elements.append(company_info)
    elements.append(Spacer(1, 15))

    # Vendor Transactions Section
    if filtered_data:
        elements.append(Paragraph("<b>VENDOR TRANSACTIONS</b>", styles['Heading2']))

        data = [['Date', 'Vendor', 'Type', 'Item', 'Qty', 'Rate', 'Amount']]

        for vendor in filtered_data:
            data.append([
                vendor['date'],
                vendor['vendor_name'][:15],
                vendor['vendor_type'].title(),
                vendor['item_name'][:20],
                f"{vendor['quantity']:.2f}",
                f"Rs. {vendor['rate']:.2f}",
                f"Rs. {vendor['total_amount']:.2f}"
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004e92')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)

        elements.append(Spacer(1, 10))
        total_purchases = sum(vendor['total_amount'] for vendor in filtered_data)
        total_text = Paragraph(f"<b>Total Purchases: Rs. {total_purchases:,.2f}</b>", styles['Normal'])
        elements.append(total_text)

    # Payment History Section
    if filtered_payments:
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("<b>PAYMENT HISTORY</b>", styles['Heading2']))

        payment_data = [['Date', 'Vendor', 'Method', 'Amount', 'Notes']]

        for payment in filtered_payments:
            payment_data.append([
                payment['date'],
                payment['vendor_name'][:15],
                payment['method'],
                f"Rs. {payment['amount']:.2f}",
                payment['notes'][:25] if payment['notes'] else ""
            ])

        payment_table = Table(payment_data, repeatRows=1)
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004e92')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(payment_table)

        elements.append(Spacer(1, 10))
        total_payments = sum(payment['amount'] for payment in filtered_payments)
        payment_text = Paragraph(f"<b>Total Payments: Rs. {total_payments:,.2f}</b>", styles['Normal'])
        elements.append(payment_text)

    # Summary Section
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("<b>FINANCIAL SUMMARY</b>", styles['Heading2']))

    if vendor_name:
        total_debit = sum(v['total_amount'] for v in filtered_data)
        total_credit = sum(p['amount'] for p in filtered_payments)
        balance = total_debit - total_credit

        summary_data = [
            ["Total Debit (Purchases)", f"Rs. {total_debit:,.2f}"],
            ["Total Credit (Payments)", f"Rs. {total_credit:,.2f}"],
            ["Outstanding Balance", f"Rs. {balance:,.2f}"]
        ]
    else:
        total_debit = sum(v['total_amount'] for v in filtered_data)
        total_credit = sum(p['amount'] for p in filtered_payments)
        balance = total_debit - total_credit

        summary_data = [
            ["Total Debit (All Purchases)", f"Rs. {total_debit:,.2f}"],
            ["Total Credit (All Payments)", f"Rs. {total_credit:,.2f}"],
            ["Net Outstanding Balance", f"Rs. {balance:,.2f}"]
        ]

    summary_table = Table(summary_data, colWidths=[200, 100])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004e92')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#bdc3c7')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(summary_table)

    elements.append(Spacer(1, 25))

    try:
        if os.path.exists("signature.jpg"):
            signature_img = Image("signature.jpg", width=120, height=40)
            elements.append(signature_img)
    except:
        pass

    signature_text = Paragraph("Authorized Signature<br/><b>Green</b>",
                               ParagraphStyle(
                                   'SignatureStyle',
                                   parent=styles['Normal'],
                                   fontSize=10,
                                   spaceBefore=5,
                                   alignment=1
                               ))
    elements.append(signature_text)

    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)
    buffer.seek(0)
    return buffer

@st.cache_data(ttl=300)
def create_stock_pdf():
    """Create PDF for chemical stock"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40, bottomMargin=40)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        textColor=colors.HexColor('#004e92'),
        alignment=1
    )

    title = Paragraph("GREEN - CHEMICAL STOCK REPORT", title_style)
    elements.append(title)
    elements.append(Spacer(1, 15))

    if st.session_state.chemicals:
        data = [['ID', 'Chemical Name', 'Stock (KG)', 'Rate', 'Status']]

        for chem in st.session_state.chemicals:
            status = "Adequate"
            if chem['stock'] < st.session_state.settings['low_stock_threshold']:
                status = "Low Stock"
            if chem['stock'] <= 0:
                status = "Out of Stock"

            data.append([
                str(chem['id']),
                chem['name'][:20],
                f"{chem['stock']:.2f}",
                f"Rs. {chem['rate']:.2f}",
                status
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004e92')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)

        total_chemicals = len(st.session_state.chemicals)
        low_stock = len([c for c in st.session_state.chemicals if
                         0 < c['stock'] < st.session_state.settings['low_stock_threshold']])
        out_of_stock = len([c for c in st.session_state.chemicals if c['stock'] <= 0])

        elements.append(Spacer(1, 15))
        summary_data = [
            ["Total Chemicals", str(total_chemicals)],
            ["Low Stock Items", str(low_stock)],
            ["Out of Stock", str(out_of_stock)]
        ]

        summary_table = Table(summary_data, colWidths=[150, 80])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004e92')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#bdc3c7')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(summary_table)

    else:
        no_data = Paragraph("No chemical data available", styles['Heading2'])
        elements.append(no_data)

    elements.append(Spacer(1, 25))

    try:
        if os.path.exists("signature.jpg"):
            signature_img = Image("signature.jpg", width=120, height=40)
            elements.append(signature_img)
    except:
        pass

    signature_text = Paragraph("Authorized Signature<br/><b>Green</b>",
                               ParagraphStyle(
                                   'SignatureStyle',
                                   parent=styles['Normal'],
                                   fontSize=10,
                                   spaceBefore=5,
                                   alignment=1
                               ))
    elements.append(signature_text)

    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)
    buffer.seek(0)
    return buffer

@st.cache_data(ttl=300)
def create_production_pdf(production_data, product_name, batch_size, chemical_requirements):
    """Create PDF for production details"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40, bottomMargin=40)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        textColor=colors.HexColor('#004e92'),
        alignment=1
    )

    title = Paragraph(f"GREEN - PRODUCTION REPORT: {product_name}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 15))

    # Production Details
    elements.append(Paragraph("<b>PRODUCTION DETAILS</b>", styles['Heading2']))
    
    production_info = [
        ["Product Name", product_name],
        ["Batch Size", str(batch_size)],
        ["Production Date", datetime.now().strftime('%Y-%m-%d %H:%M')],
        ["Status", "Completed"]
    ]

    info_table = Table(production_info, colWidths=[150, 200])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004e92')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(info_table)

    elements.append(Spacer(1, 20))

    # Chemical Requirements
    elements.append(Paragraph("<b>CHEMICAL REQUIREMENTS</b>", styles['Heading2']))

    chem_data = [['Chemical Name', 'Stock (KG)', 'Required (KG)', 'To Purchase (KG)', 'Remaining (KG)', 'Rate', 'Price']]

    total_cost = 0
    for req in chemical_requirements:
        chem_data.append([
            req['Chemical Name'],
            f"{req['Stock In-Hand']}",
            f"{req['Required']}",
            f"{req['R-Purchasing']}",
            f"{req['Remaining']}",
            f"Rs. {req['Rate Per Kg']}",
            f"Rs. {req['Total Price']}"
        ])
        total_cost += float(req['Total Price'].replace('Rs. ', '').replace(',', ''))

    chem_table = Table(chem_data, repeatRows=1)
    chem_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004e92')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(chem_table)

    elements.append(Spacer(1, 15))
    total_cost_text = Paragraph(f"<b>Total Chemical Cost: Rs. {total_cost:,.2f}</b>", styles['Normal'])
    elements.append(total_cost_text)

    elements.append(Spacer(1, 25))

    try:
        if os.path.exists("signature.jpg"):
            signature_img = Image("signature.jpg", width=120, height=40)
            elements.append(signature_img)
    except:
        pass

    signature_text = Paragraph("Production Manager Signature<br/><b>Green</b>",
                               ParagraphStyle(
                                   'SignatureStyle',
                                   parent=styles['Normal'],
                                   fontSize=10,
                                   spaceBefore=5,
                                   alignment=1
                               ))
    elements.append(signature_text)

    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)
    buffer.seek(0)
    return buffer

# CSV Export/Import Functions
def export_to_csv():
    """Export all data to separate CSV files in a zip"""
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        if st.session_state.chemicals:
            chem_df = pd.DataFrame(st.session_state.chemicals)
            chem_csv = chem_df.to_csv(index=False)
            zip_file.writestr('chemicals.csv', chem_csv)

        if st.session_state.packaging_materials:
            pack_data = []
            for p_type, material in st.session_state.packaging_materials.items():
                pack_data.append({
                    'Type': p_type,
                    'Name': material['name'],
                    'Stock': material['stock'],
                    'Rate': material['rate']
                })
            pack_df = pd.DataFrame(pack_data)
            pack_csv = pack_df.to_csv(index=False)
            zip_file.writestr('packaging.csv', pack_csv)

        if st.session_state.vendor_ledger:
            vendor_df = pd.DataFrame(st.session_state.vendor_ledger)
            vendor_csv = vendor_df.to_csv(index=False)
            zip_file.writestr('vendor_ledger.csv', vendor_csv)

        if st.session_state.vendor_payments:
            payments_df = pd.DataFrame(st.session_state.vendor_payments)
            payments_csv = payments_df.to_csv(index=False)
            zip_file.writestr('vendor_payments.csv', payments_csv)

        if st.session_state.production_history:
            production_df = pd.DataFrame(st.session_state.production_history)
            production_csv = production_df.to_csv(index=False)
            zip_file.writestr('production_history.csv', production_csv)

    buffer.seek(0)
    return buffer

def create_sample_csv():
    """Create sample CSV files for import template"""
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        sample_chemicals = pd.DataFrame({
            'id': [1, 2],
            'name': ['Chemical A', 'Chemical B'],
            'stock': [100.0, 50.0],
            'rate': [500.0, 750.0]
        })
        chem_csv = sample_chemicals.to_csv(index=False)
        zip_file.writestr('chemicals.csv', chem_csv)

        sample_packaging = pd.DataFrame({
            'Type': ['bottle', 'carton'],
            'Name': ['Bottles (1L)', 'Cartons (12 bottles)'],
            'Stock': [100, 50],
            'Rate': [25.0, 120.0]
        })
        pack_csv = sample_packaging.to_csv(index=False)
        zip_file.writestr('packaging.csv', pack_csv)

    buffer.seek(0)
    return buffer

def import_from_csv(uploaded_zip):
    """Import data from CSV zip file"""
    try:
        with zipfile.ZipFile(uploaded_zip) as z:
            imported_data = {}

            if 'chemicals.csv' in z.namelist():
                with z.open('chemicals.csv') as f:
                    chem_df = pd.read_csv(f)
                    imported_data['chemicals'] = chem_df.to_dict('records')

            if 'packaging.csv' in z.namelist():
                with z.open('packaging.csv') as f:
                    pack_df = pd.read_csv(f)
                    packaging_materials = {}
                    for _, row in pack_df.iterrows():
                        packaging_materials[row['Type']] = {
                            'name': row['Name'],
                            'stock': row['Stock'],
                            'rate': row['Rate']
                        }
                    imported_data['packaging_materials'] = packaging_materials

            return imported_data
    except Exception as e:
        raise Exception(f"Error importing CSV files: {str(e)}")

# Production Template Functions
def save_production_template():
    """Save production template for users to fill"""
    template_data = {
        "product_name": "",
        "batch_size": 500,
        "chemicals_used": [],
        "packaging_used": [],
        "notes": ""
    }
    
    template_json = json.dumps(template_data, indent=2)
    return template_json

def load_production_template(uploaded_file):
    """Load production template from uploaded file"""
    try:
        template_data = json.load(uploaded_file)
        return template_data
    except Exception as e:
        raise Exception(f"Error loading template: {str(e)}")

# Main application
def main():
    # Header with updated design
    st.markdown(
        """
        <div class="main-header">
            <h1>🧪 Green</h1>
            <p>Chemical Management System | Professional Inventory & Production Management</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sidebar navigation
    with st.sidebar:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #004e92 0%, #0077b6 100%); padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px; border: 2px solid #004e92;">
                <h3>📊 Navigation</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        menu = ["Dashboard", "Chemical Stock", "Packaging", "Production", "Vendor Ledger", "Vendor Payments", "Reports", "Settings", "Data Import/Export"]
        choice = st.selectbox("Select Section", menu, label_visibility="collapsed")

        # Quick stats in sidebar
        if st.session_state.chemicals:
            st.markdown("---")
            st.subheader("📈 Quick Stats")
            total_chems = len(st.session_state.chemicals)
            low_stock = len([c for c in st.session_state.chemicals if
                             0 < c['stock'] < st.session_state.settings['low_stock_threshold']])
            total_vendors = len(set([v['vendor_name'] for v in
                                     st.session_state.vendor_ledger])) if st.session_state.vendor_ledger else 0

            st.metric("Chemicals", total_chems)
            st.metric("Low Stock", low_stock)
            st.metric("Vendors", total_vendors)

        # Auto-save button
        st.markdown("---")
        if st.button("💾 Save Data", use_container_width=True):
            auto_save()

    # Dashboard
    if choice == "Dashboard":
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.title("📊 Dashboard Overview")
        st.markdown('</div>', unsafe_allow_html=True)

        if not st.session_state.chemicals and not st.session_state.packaging_materials:
            st.info("👋 Welcome to Green Chemical Management System! Start by adding chemicals and packaging materials.")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="green-button">', unsafe_allow_html=True)
                if st.button("🧪 Add Chemicals", use_container_width=True, key="add_chem_btn"):
                    st.session_state.current_page = "Chemical Stock"
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="green-button">', unsafe_allow_html=True)
                if st.button("📦 Add Packaging", use_container_width=True, key="add_pack_btn"):
                    st.session_state.current_page = "Packaging"
                st.markdown('</div>', unsafe_allow_html=True)
            with col3:
                if st.button("⚙️ Setup Wizard", use_container_width=True, key="setup_btn"):
                    st.session_state.current_page = "Settings"

        # Quick actions
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.subheader("🚀 Quick Actions")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🧪 Manage Chemicals", use_container_width=True, key="manage_chem"):
                st.session_state.current_page = "Chemical Stock"
        with col2:
            if st.button("📦 Manage Packaging", use_container_width=True, key="manage_pack"):
                st.session_state.current_page = "Packaging"
        with col3:
            st.markdown('<div class="green-button">', unsafe_allow_html=True)
            if st.button("🏭 Production", use_container_width=True, key="prod_btn"):
                st.session_state.current_page = "Production"
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            if st.button("💰 Vendor Payments", use_container_width=True, key="vendor_pay_btn"):
                st.session_state.current_page = "Vendor Payments"

        # Dashboard cards
        total_chemicals, low_stock_count, out_of_stock_count, total_packaging = update_dashboard()

        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.subheader("📈 Business Overview")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Chemicals", total_chemicals)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Low Stock Items", low_stock_count, delta_color="inverse")
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Out of Stock", out_of_stock_count, delta_color="off")
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Packaging Items", total_packaging)
            st.markdown('</div>', unsafe_allow_html=True)

        # Recent activity
        if st.session_state.vendor_ledger:
            st.markdown('<div class="section-header">', unsafe_allow_html=True)
            st.subheader("📋 Recent Vendor Transactions")
            st.markdown('</div>', unsafe_allow_html=True)

            recent_vendors = st.session_state.vendor_ledger[-5:][::-1]
            for vendor in recent_vendors:
                st.markdown(f"""
                <div class="vendor-card">
                    <b>{vendor['vendor_name']}</b> - {vendor['item_name']}<br>
                    <small>Date: {vendor['date']} | Amount: Rs. {vendor['total_amount']:,.2f}</small>
                </div>
                """, unsafe_allow_html=True)

    # Chemical Stock Management
    elif choice == "Chemical Stock":
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.title("🧪 Chemical Stock Management")
        st.markdown('</div>', unsafe_allow_html=True)

        # Add new chemical
        with st.expander("➕ Add New Chemical", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                new_chemical_name = st.text_input("Chemical Name", key="new_chem_name")
            with col2:
                initial_stock = st.number_input("Initial Stock (KG)", min_value=0.0, step=0.1, value=0.0,
                                                key="init_stock")
            with col3:
                chemical_rate = st.number_input("Rate (Per KG)", min_value=0.0, step=0.1, value=0.0, key="chem_rate")

            st.markdown('<div class="green-button">', unsafe_allow_html=True)
            if st.button("Add Chemical", type="primary", key="add_chem_btn2"):
                if new_chemical_name:
                    if any(chem['name'].lower() == new_chemical_name.lower() for chem in st.session_state.chemicals):
                        show_alert("Chemical already exists!", "warning")
                    else:
                        new_chemical = {
                            'id': get_next_chemical_id(),
                            'name': new_chemical_name,
                            'stock': initial_stock,
                            'rate': chemical_rate
                        }
                        st.session_state.chemicals.append(new_chemical)
                        auto_save()
                        show_alert(f"Chemical '{new_chemical_name}' added successfully!", "success")
                        st.rerun()
                else:
                    show_alert("Please enter a chemical name", "error")
            st.markdown('</div>', unsafe_allow_html=True)

        # Add stock to existing chemical
        with st.expander("📥 Add Stock to Existing Chemical", expanded=False):
            if st.session_state.chemicals:
                chemical_names = [chem['name'] for chem in st.session_state.chemicals]
                selected_chemical = st.selectbox("Select Chemical", chemical_names, key="select_chem")

                col1, col2 = st.columns(2)
                with col1:
                    stock_to_add = st.number_input("Stock to Add (KG)", min_value=0.0, step=0.1, key="stock_add")
                with col2:
                    new_rate = st.number_input("New Rate (Optional)", min_value=0.0, step=0.1, key="new_rate")

                st.markdown('<div class="green-button">', unsafe_allow_html=True)
                if st.button("Add Stock", key="add_stock_btn"):
                    chemical = next(chem for chem in st.session_state.chemicals if chem['name'] == selected_chemical)
                    chemical['stock'] += stock_to_add
                    if new_rate > 0:
                        chemical['rate'] = new_rate
                    auto_save()
                    show_alert(f"Added {stock_to_add} KG to {selected_chemical}", "success")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No chemicals available. Add chemicals first.")

        # Edit Chemical Section
        if st.session_state.chemicals:
            with st.expander("✏️ Edit Chemical", expanded=False):
                chemical_to_edit = st.selectbox("Select Chemical to Edit", 
                                              [f"{chem['id']} - {chem['name']} - Stock: {chem['stock']} KG" 
                                               for chem in st.session_state.chemicals],
                                              key="edit_chem_select")

                if chemical_to_edit:
                    chemical_id = int(chemical_to_edit.split(" - ")[0])
                    chemical = next((chem for chem in st.session_state.chemicals if chem['id'] == chemical_id), None)

                    if chemical:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            edit_name = st.text_input("Chemical Name", value=chemical['name'], key="edit_chem_name")
                        with col2:
                            edit_stock = st.number_input("Stock (KG)", value=chemical['stock'], key="edit_chem_stock")
                        with col3:
                            edit_rate = st.number_input("Rate (Per KG)", value=chemical['rate'], key="edit_chem_rate")

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown('<div class="green-button">', unsafe_allow_html=True)
                            update_chemical = st.button("🔄 Update Chemical", use_container_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        with col2:
                            delete_chemical = st.button("🗑️ Delete Chemical", type="secondary", use_container_width=True)

                        if update_chemical:
                            chemical['name'] = edit_name
                            chemical['stock'] = edit_stock
                            chemical['rate'] = edit_rate
                            auto_save()
                            show_alert("Chemical updated successfully!", "success")
                            st.rerun()

                        if delete_chemical:
                            st.session_state.chemicals = [chem for chem in st.session_state.chemicals if chem['id'] != chemical_id]
                            auto_save()
                            show_alert("Chemical deleted successfully!", "success")
                            st.rerun()

        # Show all chemicals
        with st.expander("📋 All Chemicals Stock", expanded=True):
            if st.session_state.chemicals:
                chemical_data = []
                for chem in st.session_state.chemicals:
                    status = "Adequate"
                    if chem['stock'] < st.session_state.settings['low_stock_threshold']:
                        status = "Low Stock"
                    if chem['stock'] <= 0:
                        status = "Out of Stock"

                    chemical_data.append({
                        'ID': chem['id'],
                        'Name': chem['name'],
                        'Stock (KG)': f"{chem['stock']:.2f}",
                        'Rate': f"Rs. {chem['rate']:.2f}",
                        'Status': status
                    })

                df = pd.DataFrame(chemical_data)
                st.dataframe(df, use_container_width=True, height=400)

                # PDF Download button
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📄 Generate Stock Report PDF", use_container_width=True, key="gen_stock_pdf"):
                        with st.spinner("Generating PDF..."):
                            pdf_buffer = create_stock_pdf()
                            st.download_button(
                                label="⬇️ Download Stock PDF",
                                data=pdf_buffer,
                                file_name=f"Green_Chemical_Stock_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                key="download_stock_pdf"
                            )
            else:
                st.info("No chemicals added yet.")

    # Packaging Management
    elif choice == "Packaging":
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.title("📦 Packaging Materials Management")
        st.markdown('</div>', unsafe_allow_html=True)

        # Add packaging materials
        with st.expander("➕ Add Packaging Materials", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                packaging_type = st.selectbox("Packaging Type",
                                              ["", "bottle", "carton", "can", "box"],
                                              format_func=lambda x: {
                                                  "": "-- Select Type --",
                                                  "bottle": "Bottles (1L)",
                                                  "carton": "Cartons (12 bottles)",
                                                  "can": "Cans (25L)",
                                                  "box": "Boxes (1KG)"
                                              }[x], key="pack_type")
            with col2:
                packaging_quantity = st.number_input("Quantity", min_value=0, step=1, value=0, key="pack_qty")
            with col3:
                packaging_rate = st.number_input("Rate (Per Unit)", min_value=0.0, step=0.1, value=0.0, key="pack_rate")

            st.markdown('<div class="green-button">', unsafe_allow_html=True)
            if st.button("Add Packaging Stock", type="primary", key="add_pack_btn2"):
                if packaging_type:
                    packaging_names = {
                        "bottle": "Bottles (1L)",
                        "carton": "Cartons (12 bottles)",
                        "can": "Cans (25L)",
                        "box": "Boxes (1KG)"
                    }

                    if packaging_type not in st.session_state.packaging_materials:
                        st.session_state.packaging_materials[packaging_type] = {
                            'name': packaging_names[packaging_type],
                            'stock': 0,
                            'rate': 0
                        }

                    st.session_state.packaging_materials[packaging_type]['stock'] += packaging_quantity
                    if packaging_rate > 0:
                        st.session_state.packaging_materials[packaging_type]['rate'] = packaging_rate

                    auto_save()
                    show_alert(f"Added {packaging_quantity} units to {packaging_names[packaging_type]}", "success")
                    st.rerun()
                else:
                    show_alert("Please select packaging type", "error")
            st.markdown('</div>', unsafe_allow_html=True)

        # Show all packaging materials
        with st.expander("📋 All Packaging Materials", expanded=True):
            if st.session_state.packaging_materials:
                packaging_data = []
                for p_type, material in st.session_state.packaging_materials.items():
                    status = "Adequate"
                    if material['stock'] < st.session_state.settings['packaging_low_stock']:
                        status = "Low Stock"
                    if material['stock'] <= 0:
                        status = "Out of Stock"

                    packaging_data.append({
                        'Type': p_type,
                        'Description': material['name'],
                        'Stock': material['stock'],
                        'Rate': f"Rs. {material['rate']:.2f}",
                        'Status': status
                    })

                df = pd.DataFrame(packaging_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No packaging materials added yet.")

    # Production Management
    elif choice == "Production":
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.title("🏭 Production Batch Management")
        st.markdown('</div>', unsafe_allow_html=True)

        # Production Template Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 Production Template")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Download template
            template_json = save_production_template()
            st.download_button(
                label="📥 Download Production Template",
                data=template_json,
                file_name="green_production_template.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            # Upload template
            uploaded_template = st.file_uploader("Upload Production Template", type=['json'], key="template_upload")
            if uploaded_template is not None:
                try:
                    template_data = load_production_template(uploaded_template)
                    st.success("✅ Template loaded successfully!")
                    
                    # Pre-fill form with template data
                    if st.button("🔄 Load Template Data", use_container_width=True):
                        # Here you would populate your production form with template data
                        st.session_state.template_data = template_data
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error loading template: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

        PRODUCT_FORMULAS = get_product_formulas()
        PRODUCT_PACKAGING = get_product_packaging()

        # Production Form
        with st.form("production_form", clear_on_submit=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                product_select = st.selectbox("Select Product", [""] + list(PRODUCT_FORMULAS.keys()), key="prod_select")
            with col2:
                batch_size = st.number_input("Batch Size", min_value=1,
                                             value=st.session_state.settings['default_batch_size'], key="batch_size")
            with col3:
                production_date = st.date_input("Production Date", value=datetime.now(), key="prod_date")

            st.markdown('<div class="green-button">', unsafe_allow_html=True)
            calculate_requirements = st.form_submit_button("Calculate Requirements", type="primary",
                                                           use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if calculate_requirements and product_select:
            formula = PRODUCT_FORMULAS[product_select]
            base_batch_size = 550 if product_select == "NETONIL" else (
                300 if product_select in ["URIVIT", "NURBUS", "PROLYTE-C"] else 500)

            # Check for missing chemicals
            missing_chemicals = []
            for item in formula:
                if not any(chem['name'] == item['chemical_name'] for chem in st.session_state.chemicals):
                    missing_chemicals.append(item['chemical_name'])

            if missing_chemicals:
                show_alert(f"Missing chemicals: {', '.join(missing_chemicals)}. Please add them to inventory first.",
                           "error")
            else:
                # Calculate requirements - CONVERT GRAMS TO KG
                st.subheader("Chemical Requirements")
                requirements_data = []
                total_price = 0

                for item in formula:
                    chemical = next(
                        chem for chem in st.session_state.chemicals if chem['name'] == item['chemical_name'])
                    
                    # Convert formula amount from grams to kg and calculate required amount
                    formula_amount_kg = grams_to_kg(item[f'amount_per_{base_batch_size}'])
                    required = (formula_amount_kg / base_batch_size) * batch_size
                    
                    purchasing = max(0, required - chemical['stock'])
                    remaining = max(0, chemical['stock'] - required)
                    price = purchasing * chemical['rate']
                    total_price += price

                    requirements_data.append({
                        'Chemical Name': chemical['name'],
                        'Stock In-Hand': f"{chemical['stock']:.3f}",
                        'Required': f"{required:.3f}",
                        'R-Purchasing': f"{purchasing:.3f}",
                        'Remaining': f"{remaining:.3f}",
                        'Rate Per Kg': f"{chemical['rate']:.2f}",
                        'Total Price': f"{price:.2f}"
                    })

                df_requirements = pd.DataFrame(requirements_data)
                st.dataframe(df_requirements, use_container_width=True)

                # Production actions
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="green-button">', unsafe_allow_html=True)
                    if st.button("Update Stock After Production", use_container_width=True, key="update_stock"):
                        # Update chemical stock
                        for item in formula:
                            chemical = next(
                                chem for chem in st.session_state.chemicals if chem['name'] == item['chemical_name'])
                            formula_amount_kg = grams_to_kg(item[f'amount_per_{base_batch_size}'])
                            required = (formula_amount_kg / base_batch_size) * batch_size
                            chemical['stock'] = max(0, chemical['stock'] - required)

                        # Update packaging stock
                        packaging_type = PRODUCT_PACKAGING[product_select]['type']
                        packaging_size = PRODUCT_PACKAGING[product_select]['size']

                        if packaging_type == 'can':
                            packaging_required = (batch_size + packaging_size - 1) // packaging_size
                        else:
                            packaging_required = batch_size / packaging_size

                        if packaging_type in st.session_state.packaging_materials:
                            st.session_state.packaging_materials[packaging_type]['stock'] = max(
                                0, st.session_state.packaging_materials[packaging_type]['stock'] - packaging_required
                            )

                        # Add to production history
                        production_record = {
                            'date': production_date.strftime("%Y-%m-%d"),
                            'product': product_select,
                            'batch_size': batch_size,
                            'status': 'Completed'
                        }
                        st.session_state.production_history.append(production_record)

                        auto_save()
                        show_alert("Stock updated after production successfully!", "success")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    if st.button("📄 Download Production Report PDF", use_container_width=True, key="prod_pdf"):
                        with st.spinner("Generating Production PDF..."):
                            pdf_buffer = create_production_pdf(
                                production_record if 'production_record' in locals() else {},
                                product_select,
                                batch_size,
                                requirements_data
                            )
                            st.download_button(
                                label="⬇️ Download Production Report",
                                data=pdf_buffer,
                                file_name=f"Green_Production_Report_{product_select}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                key="download_prod_pdf"
                            )

    # Vendor Ledger Management
    elif choice == "Vendor Ledger":
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.title("🚚 Vendor Ledger Management")
        st.markdown('</div>', unsafe_allow_html=True)

        with st.form("vendor_form", clear_on_submit=True):
            st.subheader("📝 Add Vendor Transaction")

            col1, col2 = st.columns(2)

            with col1:
                vendor_name = st.text_input("Vendor Name", key="vendor_name", placeholder="Enter vendor name...")
                vendor_type = st.selectbox("Vendor Type",
                                           ["", "chemical", "bottle", "carton", "can", "shipper", "other"],
                                           key="vendor_type")
            with col2:
                item_quantity = st.number_input("Quantity", min_value=0.0, step=0.1, value=0.0, key="item_qty")
                item_rate = st.number_input("Rate (Per Unit)", min_value=0.0, step=0.1, value=0.0, key="item_rate")

            if vendor_type == "chemical" and st.session_state.chemicals:
                item_name = st.selectbox("Item Name", [chem['name'] for chem in st.session_state.chemicals],
                                         key="chem_item")
            else:
                item_name = st.text_input("Item Name", key="other_item", placeholder="Enter item name...")

            transaction_date = st.date_input("Transaction Date", value=datetime.now(), key="trans_date")
            transaction_notes = st.text_area("Notes", key="trans_notes", placeholder="Enter transaction details...")

            st.markdown('<div class="green-button">', unsafe_allow_html=True)
            add_transaction = st.form_submit_button("💾 Add Transaction", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if add_transaction:
            if vendor_name and vendor_type and item_name and item_quantity > 0 and item_rate > 0:
                total_amount = item_quantity * item_rate

                vendor_transaction = {
                    'id': get_next_vendor_id(),
                    'date': transaction_date.strftime("%Y-%m-%d"),
                    'vendor_name': vendor_name,
                    'vendor_type': vendor_type,
                    'item_name': item_name,
                    'quantity': item_quantity,
                    'rate': item_rate,
                    'total_amount': total_amount,
                    'notes': transaction_notes
                }
                st.session_state.vendor_ledger.append(vendor_transaction)

                # Update stock if applicable
                if vendor_type == "chemical":
                    chemical = next((chem for chem in st.session_state.chemicals if chem['name'] == item_name), None)
                    if chemical:
                        chemical['stock'] += item_quantity
                        chemical['rate'] = item_rate

                auto_save()
                show_alert(f"Vendor transaction added successfully! Total amount: Rs. {total_amount:,.2f}", "success")
                st.rerun()
            else:
                show_alert("Please fill all required fields with valid values", "error")

        # Show vendor ledger
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.subheader("📋 Vendor Transaction History")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.vendor_ledger:
            display_ledger = st.session_state.vendor_ledger[-50:]

            vendor_data = []
            for transaction in display_ledger:
                vendor_data.append({
                    'ID': transaction['id'],
                    'Date': transaction['date'],
                    'Vendor Name': transaction['vendor_name'],
                    'Vendor Type': transaction['vendor_type'].title(),
                    'Item Name': transaction['item_name'],
                    'Quantity': f"{transaction['quantity']:.2f}",
                    'Rate': f"Rs. {transaction['rate']:.2f}",
                    'Total Amount': f"Rs. {transaction['total_amount']:,.2f}",
                    'Notes': transaction['notes']
                })

            df = pd.DataFrame(vendor_data)
            st.dataframe(df, use_container_width=True, height=400)

            # PDF Download buttons
            st.markdown('<div class="section-header">', unsafe_allow_html=True)
            st.subheader("📄 Download Vendor Ledger Reports")
            st.markdown('</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📄 All Vendors PDF Report", use_container_width=True, key="all_vendors_pdf"):
                    with st.spinner("🔄 Generating professional PDF report..."):
                        pdf_buffer = create_vendor_ledger_pdf()
                        st.download_button(
                            label="⬇️ Download Complete Vendor Ledger PDF",
                            data=pdf_buffer,
                            file_name=f"Green_Complete_Vendor_Ledger_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="download_complete_vendor_pdf"
                        )
        else:
            st.info("📝 No vendor transactions recorded yet. Start by adding your first transaction above.")

    # Vendor Payments Management
    elif choice == "Vendor Payments":
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.title("💰 Vendor Payments Management")
        st.markdown('</div>', unsafe_allow_html=True)

        # Add payment form
        with st.form("payment_form", clear_on_submit=True):
            st.subheader("💳 Add New Payment")

            col1, col2 = st.columns(2)
            with col1:
                vendor_names = sorted(set([v['vendor_name'] for v in
                                           st.session_state.vendor_ledger])) if st.session_state.vendor_ledger else []
                selected_vendor = st.selectbox("Select Vendor", [""] + vendor_names, key="payment_vendor")
                payment_amount = st.number_input("Payment Amount (Rs.)", min_value=0.0, step=100.0, value=0.0,
                                                 key="payment_amount")
            with col2:
                payment_date = st.date_input("Payment Date", value=datetime.now(), key="payment_date")
                payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Cash", "Cheque", "Online"],
                                              key="payment_method")

            payment_notes = st.text_area("Payment Notes", placeholder="Enter payment details or reference number...",
                                         key="payment_notes")

            st.markdown('<div class="green-button">', unsafe_allow_html=True)
            add_payment = st.form_submit_button("💾 Add Payment", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if add_payment:
            if selected_vendor and payment_amount > 0:
                payment_record = {
                    'id': get_next_payment_id(),
                    'date': payment_date.strftime("%Y-%m-%d"),
                    'vendor_name': selected_vendor,
                    'amount': payment_amount,
                    'method': payment_method,
                    'notes': payment_notes
                }
                st.session_state.vendor_payments.append(payment_record)
                auto_save()
                show_alert(f"Payment of Rs. {payment_amount:,.2f} added successfully for {selected_vendor}!", "success")
                st.rerun()
            else:
                show_alert("Please select a vendor and enter a valid payment amount", "error")

        # Payment history
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.subheader("📋 Payment History")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.vendor_payments:
            for payment in st.session_state.vendor_payments[::-1]:
                st.markdown(f"""
                <div class="payment-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <b>{payment['vendor_name']}</b><br>
                            <small>Date: {payment['date']} | Method: {payment['method']}</small>
                            {f"<br><small>Notes: {payment['notes']}</small>" if payment['notes'] else ""}
                        </div>
                        <div style="text-align: right;">
                            <b style="color: #FFFFFF; font-size: 1.2em;">Rs. {payment['amount']:,.2f}</b>
                            <br>
                            <small>Paid</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No payment records available.")

    # Reports
    elif choice == "Reports":
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.title("📊 Reports")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 Chemical Stock Report", use_container_width=True, key="chem_report"):
                if st.session_state.chemicals:
                    chemical_data = []
                    for chem in st.session_state.chemicals:
                        chemical_data.append({
                            'ID': chem['id'],
                            'Chemical Name': chem['name'],
                            'Current Stock (KG)': f"{chem['stock']:.2f}",
                            'Rate (Per KG)': f"Rs. {chem['rate']:.2f}",
                            'Status': 'Out of Stock' if chem['stock'] <= 0 else 'Low Stock' if chem['stock'] <
                                                                                               st.session_state.settings[
                                                                                                   'low_stock_threshold'] else 'Adequate'
                        })

                    df = pd.DataFrame(chemical_data)
                    st.subheader("Chemical Stock Report")
                    st.dataframe(df, use_container_width=True)

                    if st.button("📄 Download Chemical Report PDF", use_container_width=True, key="dl_chem_pdf"):
                        with st.spinner("Generating PDF..."):
                            pdf_buffer = create_stock_pdf()
                            st.download_button(
                                label="⬇️ Download Chemical Report",
                                data=pdf_buffer,
                                file_name=f"Green_Chemical_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                key="dl_chem_report"
                            )
                else:
                    st.info("No chemicals available for report.")

        with col2:
            if st.button("🚚 Vendor Ledger Report", use_container_width=True, key="vendor_report"):
                if st.session_state.vendor_ledger:
                    vendor_data = []
                    for transaction in st.session_state.vendor_ledger[-50:]:
                        vendor_data.append({
                            'ID': transaction['id'],
                            'Date': transaction['date'],
                            'Vendor Name': transaction['vendor_name'],
                            'Vendor Type': transaction['vendor_type'],
                            'Item Name': transaction['item_name'],
                            'Quantity': transaction['quantity'],
                            'Rate': f"Rs. {transaction['rate']:.2f}",
                            'Total Amount': f"Rs. {transaction['total_amount']:,.2f}",
                            'Notes': transaction['notes']
                        })

                    df = pd.DataFrame(vendor_data)
                    st.subheader("Vendor Ledger Report")
                    st.dataframe(df, use_container_width=True)

                    if st.button("📄 Download Vendor Report PDF", use_container_width=True, key="dl_vendor_pdf"):
                        with st.spinner("Generating PDF..."):
                            pdf_buffer = create_vendor_ledger_pdf()
                            st.download_button(
                                label="⬇️ Download Vendor Report",
                                data=pdf_buffer,
                                file_name=f"Green_Vendor_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                key="dl_vendor_report"
                            )
                else:
                    st.info("No vendor transactions available for report.")

    # Settings
    elif choice == "Settings":
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.title("⚙️ System Settings")
        st.markdown('</div>', unsafe_allow_html=True)

        with st.form("settings_form"):
            st.subheader("Company Settings")
            company_name = st.text_input("Company Name", value=st.session_state.settings['company_name'],
                                         key="comp_name")

            st.subheader("Production Settings")
            default_batch_size = st.number_input("Default Batch Size",
                                                 min_value=1,
                                                 value=st.session_state.settings['default_batch_size'],
                                                 key="def_batch_size")

            st.subheader("Stock Alert Thresholds")
            col1, col2 = st.columns(2)
            with col1:
                low_stock_threshold = st.number_input("Low Stock Threshold (KG)",
                                                      min_value=0.1,
                                                      step=0.1,
                                                      value=float(st.session_state.settings['low_stock_threshold']),
                                                      key="low_stock_thresh")
            with col2:
                packaging_low_stock = st.number_input("Packaging Low Stock Threshold",
                                                      min_value=1,
                                                      value=st.session_state.settings['packaging_low_stock'],
                                                      key="pack_low_stock")

            st.markdown('<div class="green-button">', unsafe_allow_html=True)
            save_settings = st.form_submit_button("Save Settings", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if save_settings:
            st.session_state.settings = {
                'company_name': company_name,
                'default_batch_size': int(default_batch_size),
                'low_stock_threshold': float(low_stock_threshold),
                'packaging_low_stock': int(packaging_low_stock)
            }
            auto_save()
            show_alert("Settings saved successfully!", "success")
            st.rerun()

    # Data Import/Export Section
    elif choice == "Data Import/Export":
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.title("📊 Data Import/Export")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📤 Export Data")

            if st.button("📊 Export to CSV", use_container_width=True, key="export_csv"):
                with st.spinner("Exporting data to CSV..."):
                    csv_buffer = export_to_csv()
                    st.download_button(
                        label="⬇️ Download CSV Files (ZIP)",
                        data=csv_buffer,
                        file_name=f"Green_Data_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
                        mime="application/zip",
                        use_container_width=True,
                        key="download_csv"
                    )

            st.subheader("📋 Sample Template")
            if st.button("📝 Download Sample CSV Template", use_container_width=True, key="sample_template"):
                with st.spinner("Creating sample template..."):
                    sample_buffer = create_sample_csv()
                    st.download_button(
                        label="⬇️ Download Sample Template (ZIP)",
                        data=sample_buffer,
                        file_name="Green_Data_Import_Template.zip",
                        mime="application/zip",
                        use_container_width=True,
                        key="download_sample"
                    )

        with col2:
            st.subheader("📥 Import Data")

            uploaded_file = st.file_uploader("Choose ZIP File with CSV files", type=['zip'], key="import_zip")

            if uploaded_file is not None:
                st.info("📋 File uploaded successfully! Click import to load the data.")

                try:
                    with zipfile.ZipFile(uploaded_file) as z:
                        file_list = z.namelist()
                        st.write("Files found in ZIP:")
                        for file in file_list:
                            st.write(f"- {file}")

                    st.markdown('<div class="green-button">', unsafe_allow_html=True)
                    if st.button("🚀 Import Data", type="primary", use_container_width=True, key="import_data_btn"):
                        with st.spinner("Importing data..."):
                            imported_data = import_from_csv(uploaded_file)

                            if 'chemicals' in imported_data:
                                st.session_state.chemicals = imported_data['chemicals']
                            if 'packaging_materials' in imported_data:
                                st.session_state.packaging_materials = imported_data['packaging_materials']

                            auto_save()
                            show_alert("Data imported successfully!", "success")
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                except Exception as e:
                    show_alert(f"Error reading ZIP file: {str(e)}", "error")

        # Data Management
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.subheader("🗃️ Data Management")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 Export to JSON", use_container_width=True, key="export_json"):
                data = {
                    'chemicals': st.session_state.chemicals,
                    'packaging_materials': st.session_state.packaging_materials,
                    'vendor_ledger': st.session_state.vendor_ledger,
                    'vendor_payments': st.session_state.vendor_payments,
                    'production_history': st.session_state.production_history,
                    'settings': st.session_state.settings
                }
                json_data = json.dumps(data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"{st.session_state.settings['company_name'].replace(' ', '_')}_backup_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="dl_data"
                )

        with col2:
            uploaded_json = st.file_uploader("Import JSON", type="json", key="import_json")
            if uploaded_json is not None:
                try:
                    data = json.load(uploaded_json)
                    st.markdown('<div class="green-button">', unsafe_allow_html=True)
                    if st.button("Import JSON Data", type="primary", use_container_width=True, key="import_json_btn"):
                        st.session_state.chemicals = data.get('chemicals', [])
                        st.session_state.packaging_materials = data.get('packaging_materials', {})
                        st.session_state.vendor_ledger = data.get('vendor_ledger', [])
                        st.session_state.vendor_payments = data.get('vendor_payments', [])
                        st.session_state.production_history = data.get('production_history', [])
                        st.session_state.settings = data.get('settings', st.session_state.settings)
                        auto_save()
                        show_alert("Data imported successfully!", "success")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    show_alert(f"Error importing data: {str(e)}", "error")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; background-color: #004e92; padding: 20px; border-radius: 10px; color: white; border: 2px solid #004e92;'>
            <h3>Green Chemical Management System</h3>
            <p>Professional Inventory & Production Management Solution</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
