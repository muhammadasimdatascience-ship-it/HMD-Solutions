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

# Page configuration with updated settings
st.set_page_config(
    page_title="Green - Chemical Management System",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with WHITE background and BLUE theme
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
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 2px solid #1E90FF; /* BLUE outline */
    }

    /* Header with BLUE theme */
    .main-header {
        background: linear-gradient(135deg, #1E90FF 0%, #0047AB 100%); /* BLUE gradient */
        color: #FFFFFF;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(30, 144, 255, 0.3);
        border: 2px solid #1E90FF; /* BLUE outline */
    }

    /* Section header with BLUE theme */
    .section-header {
        background: linear-gradient(135deg, #1E90FF 0%, #0047AB 100%); /* BLUE gradient */
        color: #FFFFFF;
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 6px 20px rgba(30, 144, 255, 0.2);
        border: 2px solid #1E90FF; /* BLUE outline */
    }

    /* Cards with BLUE outline */
    .card {
        background: #FFFFFF;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border: 2px solid #1E90FF; /* BLUE outline */
        transition: transform 0.2s ease;
    }

    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(30, 144, 255, 0.15);
    }

    /* Metric cards with BLUE theme */
    .metric-card {
        background: linear-gradient(135deg, #1E90FF 0%, #0047AB 100%); /* BLUE gradient */
        color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(30, 144, 255, 0.25);
        margin: 8px;
        border: 2px solid #1E90FF; /* BLUE outline */
    }

    /* Vendor & Payment Cards with BLUE/GREEN themes */
    .vendor-card {
        background: linear-gradient(135deg, #1E90FF 0%, #0047AB 100%); /* BLUE gradient */
        color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        margin: 8px 0;
        box-shadow: 0 4px 12px rgba(30, 144, 255, 0.2);
        border: 2px solid #1E90FF; /* BLUE outline */
    }

    .payment-card {
        background: linear-gradient(135deg, #00FF00 0%, #008000 100%); /* GREEN gradient */
        color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        margin: 8px 0;
        box-shadow: 0 4px 12px rgba(0, 255, 0, 0.2);
        border: 2px solid #00FF00; /* GREEN outline */
    }

    /* BUTTONS - BLUE and GREEN with WHITE BOLD text */
    .stButton>button {
        background: linear-gradient(135deg, #1E90FF 0%, #0047AB 100%); /* BLUE gradient */
        color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 700 !important; /* BOLD text */
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(30, 144, 255, 0.3);
        border: 2px solid #1E90FF; /* BLUE outline */
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 144, 255, 0.4);
        background: linear-gradient(135deg, #0047AB 0%, #1E90FF 100%);
    }

    /* GREEN buttons */
    .green-button>button {
        background: linear-gradient(135deg, #00FF00 0%, #008000 100%) !important; /* GREEN gradient */
        border: 2px solid #00FF00 !important; /* GREEN outline */
    }

    .green-button>button:hover {
        background: linear-gradient(135deg, #008000 0%, #00FF00 100%) !important;
    }

    /* Sidebar with BLUE theme */
    .css-1d391kg, .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0047AB 0%, #1E90FF 100%);
    }

    /* DataFrame */
    .stDataFrame {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border: 2px solid #1E90FF; /* BLUE outline */
    }

    /* Forms */
    .stForm {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        margin: 15px 0;
        border: 2px solid #1E90FF; /* BLUE outline */
    }

    /* Input fields with BLUE outline */
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #FFFFFF !important;
        border-radius: 8px;
        color: #000000 !important;
        border: 2px solid #1E90FF !important; /* BLUE outline */
        font-weight: 500;
    }

    /* Metric container */
    [data-testid="metric-container"] {
        background: #FFFFFF;
        border: 2px solid #1E90FF; /* BLUE outline */
        padding: 12px;
        border-radius: 8px;
    }

    /* Expander with BLUE outline */
    .streamlit-expanderHeader {
        background: #FFFFFF !important;
        border: 2px solid #1E90FF !important; /* BLUE outline */
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    /* Success message with GREEN theme */
    .stSuccess {
        background: linear-gradient(135deg, #00FF00 0%, #008000 100%);
        color: #FFFFFF;
        border-radius: 8px;
        padding: 12px;
        border: 2px solid #00FF00;
        font-weight: 600;
    }

    /* Info message with BLUE theme */
    .stInfo {
        background: linear-gradient(135deg, #1E90FF 0%, #0047AB 100%);
        color: #FFFFFF;
        border-radius: 8px;
        padding: 12px;
        border: 2px solid #1E90FF;
        font-weight: 600;
    }

    /* Warning message */
    .stWarning {
        background: linear-gradient(135deg, #FFA500 0%, #FF8C00 100%);
        color: #FFFFFF;
        border-radius: 8px;
        padding: 12px;
        border: 2px solid #FFA500;
        font-weight: 600;
    }

    /* Error message */
    .stError {
        background: linear-gradient(135deg, #FF0000 0%, #8B0000 100%);
        color: #FFFFFF;
        border-radius: 8px;
        padding: 12px;
        border: 2px solid #FF0000;
        font-weight: 600;
    }

    /* Sidebar text color */
    .css-1d391kg p, .css-1d391kg label {
        color: #FFFFFF !important;
        font-weight: 500;
    }

    /* Selectbox dropdown */
    .stSelectbox [data-baseweb="select"] {
        border: 2px solid #1E90FF !important;
        border-radius: 8px;
    }

    /* Number input focus */
    .stNumberInput input:focus {
        border-color: #1E90FF !important;
        box-shadow: 0 0 0 2px rgba(30, 144, 255, 0.2) !important;
    }

    /* Text input focus */
    .stTextInput input:focus {
        border-color: #1E90FF !important;
        box-shadow: 0 0 0 2px rgba(30, 144, 255, 0.2) !important;
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
            'product_details': st.session_state.product_details,
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
            st.session_state.product_details = data.get('product_details', {})
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

if 'product_details' not in st.session_state:
    st.session_state.product_details = {}

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

if 'current_product_details' not in st.session_state:
    st.session_state.current_product_details = {}

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

def convert_grams_to_kg(amount_in_grams):
    """Convert grams to kilograms"""
    return amount_in_grams / 1000.0

def convert_kg_to_grams(amount_in_kg):
    """Convert kilograms to grams"""
    return amount_in_kg * 1000.0

# PDF creation functions with professional watermark and signature
def add_watermark(canvas, doc):
    """Add professional watermark to PDF pages"""
    try:
        if os.path.exists("logo.png"):
            # Set watermark with very low opacity for professional look
            canvas.saveState()
            canvas.setFillAlpha(0.03)  # Reduced opacity for professional look
            # Center the watermark
            watermark = ImageReader("logo.png")
            img_width, img_height = watermark.getSize()
            aspect = img_height / float(img_width)

            # Adjust size to cover most of the page but not too prominent
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
    """Create professional PDF for vendor ledger with detailed transaction history and summary"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40, bottomMargin=40)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        textColor=colors.HexColor('#1E90FF'),
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

        # Prepare data for table
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

        # Create table
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E90FF')),
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

        # Add transaction totals
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

        # Create payment table
        payment_table = Table(payment_data, repeatRows=1)
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0047AB')),
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

        # Add payment totals
        elements.append(Spacer(1, 10))
        total_payments = sum(payment['amount'] for payment in filtered_payments)
        payment_text = Paragraph(f"<b>Total Payments: Rs. {total_payments:,.2f}</b>", styles['Normal'])
        elements.append(payment_text)

    # Summary Section
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("<b>FINANCIAL SUMMARY</b>", styles['Heading2']))

    if vendor_name:
        # For specific vendor
        total_debit = sum(v['total_amount'] for v in filtered_data)
        total_credit = sum(p['amount'] for p in filtered_payments)
        balance = total_debit - total_credit

        summary_data = [
            ["Total Debit (Purchases)", f"Rs. {total_debit:,.2f}"],
            ["Total Credit (Payments)", f"Rs. {total_credit:,.2f}"],
            ["Outstanding Balance", f"Rs. {balance:,.2f}"]
        ]
    else:
        # For all vendors
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E90FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#bdc3c7')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(summary_table)

    # Add signature section
    elements.append(Spacer(1, 25))

    # Signature with smaller image and text above
    try:
        if os.path.exists("Asim Siganture.jpg"):
            signature_img = Image("Asim Siganture.jpg", width=120, height=40)  # Smaller signature
            elements.append(signature_img)
    except:
        pass

    signature_text = Paragraph("Accountant Signature<br/><b>Green</b>",
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
    """Create PDF for chemical stock with professional watermark and signature"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40, bottomMargin=40)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        textColor=colors.HexColor('#1E90FF'),
        alignment=1
    )

    # Title Section
    title = Paragraph("GREEN - CHEMICAL STOCK REPORT", title_style)
    elements.append(title)
    elements.append(Spacer(1, 15))

    # Add chemical stock data
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

        # Create table
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E90FF')),
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

        # Add summary
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
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0047AB')),
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

    # Add signature section
    elements.append(Spacer(1, 25))

    # Signature with smaller image and text above
    try:
        if os.path.exists("Asim Siganture.jpg"):
            signature_img = Image("Asim Siganture.jpg", width=120, height=40)
            elements.append(signature_img)
    except:
        pass

    signature_text = Paragraph("Accountant Signature<br/><b>Green</b>",
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

# PDF creation functions for production details
def create_production_details_pdf(product_name, production_data):
    """Create PDF for product production details"""
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40, bottomMargin=40)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        textColor=colors.HexColor('#1E90FF'),
        alignment=1
    )
    
    # Title Section
    title = Paragraph(f"GREEN - {product_name} PRODUCTION DETAILS", title_style)
    elements.append(title)
    
    # Product Information
    elements.append(Paragraph(f"<b>Product Name:</b> {product_name}", styles['Normal']))
    elements.append(Paragraph(f"<b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 15))
    
    # Production Details Table
    if production_data:
        data = [['Chemical Name', 'Amount Required (KG)', 'Stock Available (KG)', 'Status']]
        
        for item in production_data.get('chemical_requirements', []):
            status = "✅ Adequate" if item.get('stock_adequate', False) else "⚠️ Low Stock"
            data.append([
                item['chemical_name'],
                f"{item['amount_required_kg']:.3f}",
                f"{item['stock_available']:.3f}",
                status
            ])
        
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E90FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)
    
    # Cost Breakdown
    if production_data.get('cost_breakdown'):
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("<b>COST BREAKDOWN</b>", styles['Heading2']))
        
        cost_data = [['Cost Item', 'Amount']]
        for cost_item, amount in production_data['cost_breakdown'].items():
            cost_data.append([cost_item, amount])
        
        cost_table = Table(cost_data, colWidths=[300, 100])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0047AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        elements.append(cost_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# CSV Export/Import Functions
def export_to_csv():
    """Export all data to separate CSV files in a zip"""
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        # Chemicals CSV
        if st.session_state.chemicals:
            chem_df = pd.DataFrame(st.session_state.chemicals)
            chem_csv = chem_df.to_csv(index=False)
            zip_file.writestr('chemicals.csv', chem_csv)

        # Packaging materials CSV
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

        # Vendor ledger CSV
        if st.session_state.vendor_ledger:
            vendor_df = pd.DataFrame(st.session_state.vendor_ledger)
            vendor_csv = vendor_df.to_csv(index=False)
            zip_file.writestr('vendor_ledger.csv', vendor_csv)

        # Vendor payments CSV
        if st.session_state.vendor_payments:
            payments_df = pd.DataFrame(st.session_state.vendor_payments)
            payments_csv = payments_df.to_csv(index=False)
            zip_file.writestr('vendor_payments.csv', payments_csv)

        # Production history CSV
        if st.session_state.production_history:
            production_df = pd.DataFrame(st.session_state.production_history)
            production_csv = production_df.to_csv(index=False)
            zip_file.writestr('production_history.csv', production_csv)

        # Product details CSV
        if st.session_state.product_details:
            product_data = []
            for product_name, details in st.session_state.product_details.items():
                product_data.append({
                    'Product Name': product_name,
                    'Description': details.get('description', ''),
                    'Web Link': details.get('web_link', ''),
                    'Category': details.get('category', '')
                })
            product_df = pd.DataFrame(product_data)
            product_csv = product_df.to_csv(index=False)
            zip_file.writestr('product_details.csv', product_csv)

    buffer.seek(0)
    return buffer

def create_sample_csv():
    """Create sample CSV files for import template"""
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        # Sample Chemicals CSV
        sample_chemicals = pd.DataFrame({
            'id': [1, 2],
            'name': ['Chemical A', 'Chemical B'],
            'stock': [100.0, 50.0],
            'rate': [500.0, 750.0]
        })
        chem_csv = sample_chemicals.to_csv(index=False)
        zip_file.writestr('chemicals.csv', chem_csv)

        # Sample Packaging CSV
        sample_packaging = pd.DataFrame({
            'Type': ['bottle', 'carton'],
            'Name': ['Bottles (1L)', 'Cartons (12 bottles)'],
            'Stock': [100, 50],
            'Rate': [25.0, 120.0]
        })
        pack_csv = sample_packaging.to_csv(index=False)
        zip_file.writestr('packaging.csv', pack_csv)

        # Sample Vendor Ledger CSV
        sample_vendor_ledger = pd.DataFrame({
            'id': [1, 2],
            'date': ['2024-01-15', '2024-01-16'],
            'vendor_name': ['Vendor A', 'Vendor B'],
            'vendor_type': ['chemical', 'bottle'],
            'item_name': ['Chemical A', 'Bottles (1L)'],
            'quantity': [50.0, 100.0],
            'rate': [500.0, 25.0],
            'total_amount': [25000.0, 2500.0],
            'notes': ['Monthly purchase', 'Bulk order']
        })
        vendor_csv = sample_vendor_ledger.to_csv(index=False)
        zip_file.writestr('vendor_ledger.csv', vendor_csv)

        # Sample Vendor Payments CSV
        sample_vendor_payments = pd.DataFrame({
            'id': [1, 2],
            'date': ['2024-01-20', '2024-01-25'],
            'vendor_name': ['Vendor A', 'Vendor B'],
            'amount': [15000.0, 2000.0],
            'method': ['Bank Transfer', 'Cash'],
            'notes': ['Partial payment', 'Full payment']
        })
        payments_csv = sample_vendor_payments.to_csv(index=False)
        zip_file.writestr('vendor_payments.csv', payments_csv)

    buffer.seek(0)
    return buffer

def import_from_csv(uploaded_zip):
    """Import data from CSV zip file"""
    try:
        with zipfile.ZipFile(uploaded_zip) as z:
            imported_data = {}

            # Read each CSV file if it exists
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

            if 'vendor_ledger.csv' in z.namelist():
                with z.open('vendor_ledger.csv') as f:
                    vendor_df = pd.read_csv(f)
                    imported_data['vendor_ledger'] = vendor_df.to_dict('records')

            if 'vendor_payments.csv' in z.namelist():
                with z.open('vendor_payments.csv') as f:
                    payments_df = pd.read_csv(f)
                    imported_data['vendor_payments'] = payments_df.to_dict('records')

            if 'production_history.csv' in z.namelist():
                with z.open('production_history.csv') as f:
                    production_df = pd.read_csv(f)
                    imported_data['production_history'] = production_df.to_dict('records')

            if 'product_details.csv' in z.namelist():
                with z.open('product_details.csv') as f:
                    product_df = pd.read_csv(f)
                    product_details = {}
                    for _, row in product_df.iterrows():
                        product_details[row['Product Name']] = {
                            'description': row['Description'],
                            'web_link': row['Web Link'],
                            'category': row['Category']
                        }
                    imported_data['product_details'] = product_details

            return imported_data
    except Exception as e:
        raise Exception(f"Error importing CSV files: {str(e)}")

# Product Details Management Functions
def manage_product_details():
    """Manage product details and web links"""
    st.markdown('<div class="section-header">', unsafe_allow_html=True)
    st.title("📋 Product Details Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add/Edit Product Details
    with st.form("product_details_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Product Name", key="product_name")
            product_description = st.text_area("Product Description", key="product_desc")
        
        with col2:
            product_web_link = st.text_input("Web Link", key="product_web_link")
            product_category = st.selectbox("Category", ["Liquid", "Powder", "Tablet", "Capsule", "Other"], key="product_category")
        
        # Chemical composition
        st.subheader("Chemical Composition")
        composition_data = st.session_state.current_product_details.get('composition', [])
        
        if composition_data:
            for i, comp in enumerate(composition_data):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text_input(f"Chemical {i+1}", value=comp['name'], key=f"chem_{i}_name", disabled=True)
                with col2:
                    # Handle both grams and kg inputs
                    amount = comp['amount']
                    unit = comp.get('unit', 'kg')
                    if unit == 'g':
                        amount_display = amount * 1000  # Convert kg to grams for display
                    else:
                        amount_display = amount
                    st.number_input(f"Amount {i+1}", value=amount_display, key=f"chem_{i}_amount", disabled=True)
                with col3:
                    st.text_input(f"Unit {i+1}", value=unit.upper(), key=f"chem_{i}_unit", disabled=True)
        
        # File upload for product image
        product_image = st.file_uploader("Product Image", type=['png', 'jpg', 'jpeg'], key="product_image")
        
        submitted = st.form_submit_button("💾 Save Product Details", use_container_width=True)
        
        if submitted and product_name:
            # Save product details
            product_data = {
                'name': product_name,
                'description': product_description,
                'web_link': product_web_link,
                'category': product_category,
                'composition': composition_data,
                'image_uploaded': product_image is not None
            }
            
            st.session_state.product_details[product_name] = product_data
            auto_save()
            show_alert(f"Product details for '{product_name}' saved successfully!", "success")
    
    # Product List and Management
    st.markdown("---")
    st.subheader("📦 Product List")
    
    if st.session_state.product_details:
        for product_name, details in st.session_state.product_details.items():
            with st.expander(f"📄 {product_name}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Description:** {details.get('description', 'N/A')}")
                    st.write(f"**Category:** {details.get('category', 'N/A')}")
                    st.write(f"**Web Link:** {details.get('web_link', 'N/A')}")
                    
                    # Show composition
                    if details.get('composition'):
                        st.write("**Composition:**")
                        for comp in details['composition']:
                            unit = comp.get('unit', 'kg')
                            amount_display = comp['amount'] * 1000 if unit == 'g' else comp['amount']
                            st.write(f"  - {comp['name']}: {amount_display:.3f} {unit}")
                
                with col2:
                    # Download PDF button
                    production_data = {
                        'chemical_requirements': [],
                        'cost_breakdown': {}
                    }
                    pdf_buffer = create_production_details_pdf(product_name, production_data)
                    
                    st.download_button(
                        label="📄 Download PDF",
                        data=pdf_buffer,
                        file_name=f"Green_{product_name}_Details_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        key=f"download_{product_name}"
                    )
                    
                    # Delete button
                    if st.button("🗑️ Delete", key=f"delete_{product_name}"):
                        del st.session_state.product_details[product_name]
                        auto_save()
                        show_alert(f"Product '{product_name}' deleted successfully!", "success")
                        st.rerun()
    else:
        st.info("No product details added yet. Use the form above to add product details.")

# Enhanced Production Management with Template Support
def enhanced_production_management():
    """Enhanced production management with template support"""
    st.markdown('<div class="section-header">', unsafe_allow_html=True)
    st.title("🏭 Production Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Template-based Production
    with st.expander("📋 Template-Based Production", expanded=True):
        PRODUCT_FORMULAS = get_product_formulas()
        PRODUCT_PACKAGING = get_product_packaging()
        
        with st.form("template_production_form", clear_on_submit=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                product_select = st.selectbox("Select Product", [""] + list(PRODUCT_FORMULAS.keys()), key="prod_select")
            with col2:
                batch_size = st.number_input("Batch Size", min_value=1,
                                             value=st.session_state.settings['default_batch_size'], key="batch_size")
            with col3:
                packaging_unit = st.selectbox("Packaging Unit", ["bottle", "can", "box"], key="pack_unit")

            calculate_requirements = st.form_submit_button("🧮 Calculate Requirements", type="primary",
                                                           use_container_width=True)

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
                # Calculate requirements
                st.subheader("🧪 Chemical Requirements")
                requirements_data = []
                total_price = 0
                chemical_requirements = []

                for item in formula:
                    chemical = next(
                        chem for chem in st.session_state.chemicals if chem['name'] == item['chemical_name'])
                    
                    # Handle both grams and kg - convert to kg for calculations
                    amount_in_formula = item[f'amount_per_{base_batch_size}']
                    if amount_in_formula < 1:  # Likely in grams
                        required_kg = convert_grams_to_kg(amount_in_formula) * batch_size
                    else:
                        required_kg = (amount_in_formula / base_batch_size) * batch_size
                    
                    purchasing = max(0, required_kg - chemical['stock'])
                    remaining = max(0, chemical['stock'] - required_kg)
                    price = purchasing * chemical['rate']
                    total_price += price

                    requirements_data.append({
                        'Chemical Name': chemical['name'],
                        'Stock In-Hand (KG)': f"{chemical['stock']:.3f}",
                        'Required (KG)': f"{required_kg:.3f}",
                        'To Purchase (KG)': f"{purchasing:.3f}",
                        'Remaining (KG)': f"{remaining:.3f}",
                        'Rate Per Kg': f"Rs. {chemical['rate']:.2f}",
                        'Total Price': f"Rs. {price:.2f}"
                    })
                    
                    chemical_requirements.append({
                        'chemical_name': chemical['name'],
                        'amount_required_kg': required_kg,
                        'stock_available': chemical['stock'],
                        'stock_adequate': chemical['stock'] >= required_kg
                    })

                df_requirements = pd.DataFrame(requirements_data)
                st.dataframe(df_requirements, use_container_width=True)

                # Cost breakdown
                st.subheader("💰 Cost Breakdown")
                per_unit_cost = total_price / batch_size if batch_size > 0 else 0
                packing_material_cost = 125
                total_packing_cost = per_unit_cost + packing_material_cost
                percentage_cost = total_packing_cost * 0.2
                ali_hassan_cost = 100 if PRODUCT_PACKAGING[product_select]['type'] == 'can' else 50
                total_product_cost = total_packing_cost + percentage_cost + ali_hassan_cost

                cost_data = {
                    'Cost Item': [
                        f'Per {PRODUCT_PACKAGING[product_select]["type"].title()} Cost',
                        f'Packing Material Cost Per {PRODUCT_PACKAGING[product_select]["type"].title()}',
                        '20% Percent',
                        'Ali Hassan Cost',
                        'TOTAL COST OF PRODUCT'
                    ],
                    'Amount': [
                        f"Rs. {per_unit_cost:.3f}",
                        f"Rs. {total_packing_cost:.3f}",
                        f"Rs. {percentage_cost:.2f}",
                        f"Rs. {ali_hassan_cost}",
                        f"Rs. {total_product_cost:.2f}"
                    ]
                }

                st.dataframe(pd.DataFrame(cost_data), use_container_width=True)

                # Save production data for PDF download
                production_data = {
                    'chemical_requirements': chemical_requirements,
                    'cost_breakdown': {
                        'Per Unit Cost': f"Rs. {per_unit_cost:.3f}",
                        'Packing Material Cost': f"Rs. {total_packing_cost:.3f}",
                        '20% Percentage': f"Rs. {percentage_cost:.2f}",
                        'Ali Hassan Cost': f"Rs. {ali_hassan_cost}",
                        'Total Product Cost': f"Rs. {total_product_cost:.2f}"
                    }
                }

                # Download PDF button
                pdf_buffer = create_production_details_pdf(product_select, production_data)
                st.download_button(
                    label="📄 Download Production Report PDF",
                    data=pdf_buffer,
                    file_name=f"Green_{product_select}_Production_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_production_pdf"
                )

                # Update stock after production
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Update Stock After Production", type="primary", use_container_width=True,
                                 key="update_stock"):
                        # Update chemical stock
                        for item in formula:
                            chemical = next(
                                chem for chem in st.session_state.chemicals if chem['name'] == item['chemical_name'])
                            amount_in_formula = item[f'amount_per_{base_batch_size}']
                            if amount_in_formula < 1:  # Likely in grams
                                required_kg = convert_grams_to_kg(amount_in_formula) * batch_size
                            else:
                                required_kg = (amount_in_formula / base_batch_size) * batch_size
                            chemical['stock'] = max(0, chemical['stock'] - required_kg)

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

                        # Update cartons if using bottles
                        if packaging_type == 'bottle':
                            cartons_required = (packaging_required + 11) // 12
                            if 'carton' in st.session_state.packaging_materials:
                                st.session_state.packaging_materials['carton']['stock'] = max(
                                    0, st.session_state.packaging_materials['carton']['stock'] - cartons_required
                                )

                        # Add to production history
                        production_record = {
                            'date': datetime.now().strftime("%Y-%m-%d"),
                            'product': product_select,
                            'batch_size': batch_size,
                            'status': 'Completed',
                            'type': 'Template'
                        }
                        st.session_state.production_history.append(production_record)

                        auto_save()
                        show_alert("Stock updated after production successfully!", "success")
                        st.rerun()
    
    # Custom Production Template
    with st.expander("🎨 Custom Production Template", expanded=False):
        st.subheader("Create Custom Production Template")
        
        with st.form("custom_template_form", clear_on_submit=True):
            template_name = st.text_input("Template Name", key="template_name")
            
            # Dynamic chemical composition
            st.subheader("Chemical Composition")
            composition = []
            
            num_chemicals = st.number_input("Number of Chemicals", min_value=1, max_value=20, value=1, key="num_chems")
            
            for i in range(num_chemicals):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    chem_name = st.selectbox(f"Chemical {i+1}", 
                                           [chem['name'] for chem in st.session_state.chemicals] if st.session_state.chemicals else [""],
                                           key=f"template_chem_{i}")
                with col2:
                    chem_amount = st.number_input(f"Amount {i+1}", min_value=0.0, step=0.001, value=0.0, key=f"template_amount_{i}")
                with col3:
                    chem_unit = st.selectbox(f"Unit {i+1}", ["kg", "g"], key=f"template_unit_{i}")
                
                if chem_name:
                    composition.append({
                        'name': chem_name,
                        'amount': chem_amount,
                        'unit': chem_unit
                    })
            
            save_template = st.form_submit_button("💾 Save Custom Template", use_container_width=True)
            
            if save_template and template_name:
                # Convert all to kg for storage
                for comp in composition:
                    if comp['unit'] == 'g':
                        comp['amount'] = convert_grams_to_kg(comp['amount'])
                        comp['unit'] = 'kg'  # Store in kg
                
                st.session_state.current_product_details = {
                    'composition': composition
                }
                show_alert(f"Custom template '{template_name}' saved successfully!", "success")

# Main application
def main():
    # Header with updated design
    st.markdown(
        """
        <div class="main-header">
            <h1>🧪 Green Chemical Management System</h1>
            <p>Professional Inventory & Vendor Management | Streamlined Production</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sidebar navigation
    with st.sidebar:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #1E90FF 0%, #0047AB 100%); padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px; border: 2px solid #1E90FF;">
                <h3>📊 Navigation</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        menu = ["Dashboard", "Chemical Stock", "Packaging", "Production", "Product Details", 
                "Vendor Ledger", "Vendor Payments", "Reports", "Settings", "Data Import/Export"]
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

        # Auto-save button with GREEN theme
        st.markdown("---")
        if st.button("💾 Save Data", use_container_width=True, key="save_data_btn"):
            auto_save()

    # Dashboard
    if choice == "Dashboard":
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.title("📊 Dashboard Overview")
        st.markdown('</div>', unsafe_allow_html=True)

        # Welcome section
        if not st.session_state.chemicals and not st.session_state.packaging_materials:
            st.info(
                "👋 Welcome to Green Chemical Management System! Start by adding chemicals and packaging materials.")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🧪 Add Chemicals", use_container_width=True, key="add_chem_btn"):
                    st.session_state.current_page = "Chemical Stock"
            with col2:
                if st.button("📦 Add Packaging", use_container_width=True, key="add_pack_btn"):
                    st.session_state.current_page = "Packaging"
            with col3:
                if st.button("⚙️ Setup Wizard", use_container_width=True, key="setup_btn"):
                    st.session_state.current_page = "Settings"

        # Quick actions with BLUE buttons
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
            if st.button("🏭 Production", use_container_width=True, key="prod_btn"):
                st.session_state.current_page = "Production"
        with col4:
            if st.button("📋 Product Details", use_container_width=True, key="product_details_btn"):
                st.session_state.current_page = "Product Details"

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

        # Vendor financial overview
        if st.session_state.vendor_ledger:
            st.markdown('<div class="section-header">', unsafe_allow_html=True)
            st.subheader("💰 Vendor Financial Overview")
            st.markdown('</div>', unsafe_allow_html=True)

            total_purchases = sum(vendor['total_amount'] for vendor in st.session_state.vendor_ledger)
            total_payments = sum(payment['amount'] for payment in st.session_state.vendor_payments)
            outstanding_balance = total_purchases - total_payments

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Total Purchases", f"Rs. {total_purchases:,.2f}")
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Total Payments", f"Rs. {total_payments:,.2f}")
                st.markdown('</div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Outstanding Balance", f"Rs. {outstanding_balance:,.2f}",
                          delta=f"{-outstanding_balance:,.2f}" if outstanding_balance > 0 else None,
                          delta_color="inverse" if outstanding_balance > 0 else "normal")
                st.markdown('</div>', unsafe_allow_html=True)

        # Recent vendor transactions
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

        # Recent activity
        if st.session_state.production_history:
            st.markdown('<div class="section-header">', unsafe_allow_html=True)
            st.subheader("📋 Recent Production")
            st.markdown('</div>', unsafe_allow_html=True)
            
            recent_production = st.session_state.production_history[-5:][::-1]
            for prod in recent_production:
                st.markdown(f"""
                <div class="card">
                    <b>{prod['product']}</b> - Batch Size: {prod['batch_size']}<br>
                    <small>Date: {prod['date']} | Status: {prod['status']}</small>
                </div>
                """, unsafe_allow_html=True)

    # Product Details Management
    elif choice == "Product Details":
        manage_product_details()

    # Production Management
    elif choice == "Production":
        enhanced_production_management()

    # Chemical Stock Management
    elif choice == "Chemical Stock":
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.title("🧪 Chemical Stock Management")
        st.markdown('</div>', unsafe_allow_html=True)

        # Add new chemical with unit selection
        with st.expander("➕ Add New Chemical", expanded=False):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                new_chemical_name = st.text_input("Chemical Name", key="new_chem_name")
            with col2:
                initial_stock = st.number_input("Initial Stock", min_value=0.0, step=0.001, value=0.0, key="init_stock")
            with col3:
                stock_unit = st.selectbox("Unit", ["kg", "g"], key="stock_unit")
            with col4:
                chemical_rate = st.number_input("Rate (Per KG)", min_value=0.0, step=0.1, value=0.0, key="chem_rate")

            if st.button("Add Chemical", type="primary", key="add_chem_btn2"):
                if new_chemical_name:
                    if any(chem['name'].lower() == new_chemical_name.lower() for chem in st.session_state.chemicals):
                        show_alert("Chemical already exists!", "warning")
                    else:
                        # Convert to kg for storage
                        if stock_unit == "g":
                            initial_stock_kg = convert_grams_to_kg(initial_stock)
                        else:
                            initial_stock_kg = initial_stock
                            
                        new_chemical = {
                            'id': get_next_chemical_id(),
                            'name': new_chemical_name,
                            'stock': initial_stock_kg,
                            'rate': chemical_rate,
                            'original_unit': stock_unit
                        }
                        st.session_state.chemicals.append(new_chemical)
                        auto_save()
                        show_alert(f"Chemical '{new_chemical_name}' added successfully!", "success")
                        st.rerun()
                else:
                    show_alert("Please enter a chemical name", "error")

        # Add stock to existing chemical
        with st.expander("📥 Add Stock to Existing Chemical", expanded=False):
            if st.session_state.chemicals:
                chemical_names = [chem['name'] for chem in st.session_state.chemicals]
                selected_chemical = st.selectbox("Select Chemical", chemical_names, key="select_chem")

                col1, col2, col3 = st.columns(3)
                with col1:
                    stock_to_add = st.number_input("Stock to Add", min_value=0.0, step=0.001, key="stock_add")
                with col2:
                    add_unit = st.selectbox("Unit", ["kg", "g"], key="add_unit")
                with col3:
                    new_rate = st.number_input("New Rate (Optional)", min_value=0.0, step=0.1, key="new_rate")

                if st.button("Add Stock", key="add_stock_btn"):
                    chemical = next(chem for chem in st.session_state.chemicals if chem['name'] == selected_chemical)
                    # Convert to kg for storage
                    if add_unit == "g":
                        stock_to_add_kg = convert_grams_to_kg(stock_to_add)
                    else:
                        stock_to_add_kg = stock_to_add
                        
                    chemical['stock'] += stock_to_add_kg
                    if new_rate > 0:
                        chemical['rate'] = new_rate
                    auto_save()
                    show_alert(f"Added {stock_to_add} {add_unit} to {selected_chemical}", "success")
                    st.rerun()
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
                            update_chemical = st.button("🔄 Update Chemical", use_container_width=True)
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
                        'Stock (KG)': f"{chem['stock']:.3f}",
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

        # Edit Packaging Section
        if st.session_state.packaging_materials:
            with st.expander("✏️ Edit Packaging Materials", expanded=False):
                packaging_types = list(st.session_state.packaging_materials.keys())
                selected_packaging = st.selectbox("Select Packaging to Edit", packaging_types, key="edit_pack_select")

                if selected_packaging:
                    material = st.session_state.packaging_materials[selected_packaging]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        edit_pack_name = st.text_input("Description", value=material['name'], key="edit_pack_name")
                    with col2:
                        edit_pack_stock = st.number_input("Stock", value=material['stock'], key="edit_pack_stock")
                    with col3:
                        edit_pack_rate = st.number_input("Rate", value=material['rate'], key="edit_pack_rate")

                    col1, col2 = st.columns(2)
                    with col1:
                        update_packaging = st.button("🔄 Update Packaging", use_container_width=True)
                    with col2:
                        delete_packaging = st.button("🗑️ Delete Packaging", type="secondary", use_container_width=True)

                    if update_packaging:
                        material['name'] = edit_pack_name
                        material['stock'] = edit_pack_stock
                        material['rate'] = edit_pack_rate
                        auto_save()
                        show_alert("Packaging material updated successfully!", "success")
                        st.rerun()

                    if delete_packaging:
                        del st.session_state.packaging_materials[selected_packaging]
                        auto_save()
                        show_alert("Packaging material deleted successfully!", "success")
                        st.rerun()

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

            # Item name based on vendor type
            if vendor_type == "chemical" and st.session_state.chemicals:
                item_name = st.selectbox("Item Name", [chem['name'] for chem in st.session_state.chemicals],
                                         key="chem_item")
            else:
                item_name = st.text_input("Item Name", key="other_item", placeholder="Enter item name...")

            transaction_date = st.date_input("Transaction Date", value=datetime.now(), key="trans_date")
            transaction_notes = st.text_area("Notes", key="trans_notes", placeholder="Enter transaction details...")

            add_transaction = st.form_submit_button("💾 Add Transaction", type="primary", use_container_width=True)

        if add_transaction:
            if vendor_name and vendor_type and item_name and item_quantity > 0 and item_rate > 0:
                total_amount = item_quantity * item_rate

                # Add to vendor ledger
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
                elif vendor_type in ["bottle", "carton", "can", "box"]:
                    if vendor_type not in st.session_state.packaging_materials:
                        packaging_names = {
                            "bottle": "Bottles (1L)",
                            "carton": "Cartons (12 bottles)",
                            "can": "Cans (25L)",
                            "box": "Boxes (1KG)"
                        }
                        st.session_state.packaging_materials[vendor_type] = {
                            'name': packaging_names[vendor_type],
                            'stock': 0,
                            'rate': 0
                        }
                    st.session_state.packaging_materials[vendor_type]['stock'] += item_quantity
                    st.session_state.packaging_materials[vendor_type]['rate'] = item_rate

                auto_save()
                show_alert(f"Vendor transaction added successfully! Total amount: Rs. {total_amount:,.2f}", "success")
                st.rerun()
            else:
                show_alert("Please fill all required fields with valid values", "error")

        # Edit Vendor Transaction Section
        if st.session_state.vendor_ledger:
            st.markdown('<div class="section-header">', unsafe_allow_html=True)
            st.subheader("✏️ Edit Vendor Transaction")
            st.markdown('</div>', unsafe_allow_html=True)

            vendor_to_edit = st.selectbox("Select Transaction to Edit", 
                                        [f"{v['id']} - {v['vendor_name']} - {v['item_name']} - Rs. {v['total_amount']}" 
                                         for v in st.session_state.vendor_ledger],
                                        key="edit_vendor_select")

            if vendor_to_edit:
                vendor_id = int(vendor_to_edit.split(" - ")[0])
                vendor = next((v for v in st.session_state.vendor_ledger if v['id'] == vendor_id), None)

                if vendor:
                    with st.form("edit_vendor_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            edit_vendor_name = st.text_input("Vendor Name", value=vendor['vendor_name'], key="edit_vendor_name")
                            edit_vendor_type = st.selectbox("Vendor Type", ["chemical", "bottle", "carton", "can", "shipper", "other"],
                                                          index=["chemical", "bottle", "carton", "can", "shipper", "other"].index(vendor['vendor_type']),
                                                          key="edit_vendor_type")
                        with col2:
                            edit_quantity = st.number_input("Quantity", value=vendor['quantity'], key="edit_vendor_qty")
                            edit_rate = st.number_input("Rate", value=vendor['rate'], key="edit_vendor_rate")

                        edit_item_name = st.text_input("Item Name", value=vendor['item_name'], key="edit_vendor_item")
                        edit_date = st.date_input("Date", value=datetime.strptime(vendor['date'], "%Y-%m-%d"), key="edit_vendor_date")
                        edit_notes = st.text_area("Notes", value=vendor['notes'], key="edit_vendor_notes")

                        col1, col2 = st.columns(2)
                        with col1:
                            update_vendor = st.form_submit_button("🔄 Update Transaction", use_container_width=True)
                        with col2:
                            delete_vendor = st.form_submit_button("🗑️ Delete Transaction", type="secondary", use_container_width=True)

                        if update_vendor:
                            vendor['vendor_name'] = edit_vendor_name
                            vendor['vendor_type'] = edit_vendor_type
                            vendor['item_name'] = edit_item_name
                            vendor['quantity'] = edit_quantity
                            vendor['rate'] = edit_rate
                            vendor['total_amount'] = edit_quantity * edit_rate
                            vendor['date'] = edit_date.strftime("%Y-%m-%d")
                            vendor['notes'] = edit_notes
                            auto_save()
                            show_alert("Vendor transaction updated successfully!", "success")
                            st.rerun()

                        if delete_vendor:
                            st.session_state.vendor_ledger = [v for v in st.session_state.vendor_ledger if v['id'] != vendor_id]
                            auto_save()
                            show_alert("Vendor transaction deleted successfully!", "success")
                            st.rerun()

        # Show vendor ledger
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.subheader("📋 Vendor Transaction History")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.vendor_ledger:
            display_ledger = st.session_state.vendor_ledger[-50:]  # Show last 50 records

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

            # PDF Download buttons for different vendor types
            st.markdown('<div class="section-header">', unsafe_allow_html=True)
            st.subheader("📄 Download Vendor Ledger Reports")
            st.markdown('</div>', unsafe_allow_html=True)

            # Get unique vendor types
            vendor_types = sorted(set([v['vendor_type'] for v in st.session_state.vendor_ledger]))

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

            with col2:
                if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_vendor"):
                    st.rerun()

            # Separate PDFs for each vendor type
            if vendor_types:
                st.markdown("### Vendor Type Specific Reports")
                cols = st.columns(3)
                for i, vendor_type in enumerate(vendor_types):
                    col_idx = i % 3
                    with cols[col_idx]:
                        if st.button(f"📄 {vendor_type.title()} Vendor PDF", use_container_width=True,
                                     key=f"{vendor_type}_pdf"):
                            with st.spinner(f"🔄 Generating {vendor_type} vendor PDF..."):
                                pdf_buffer = create_vendor_ledger_pdf(vendor_type=vendor_type)
                                st.download_button(
                                    label=f"⬇️ Download {vendor_type.title()} Vendor PDF",
                                    data=pdf_buffer,
                                    file_name=f"Green_{vendor_type.title()}_Vendor_Ledger_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True,
                                    key=f"download_{vendor_type}_pdf"
                                )

            # Vendor summary
            st.markdown('<div class="section-header">', unsafe_allow_html=True)
            st.subheader("📊 Vendor Summary")
            st.markdown('</div>', unsafe_allow_html=True)

            vendor_summary = {}
            for transaction in st.session_state.vendor_ledger:
                vendor = transaction['vendor_name']
                if vendor not in vendor_summary:
                    vendor_summary[vendor] = 0
                vendor_summary[vendor] += transaction['total_amount']

            for vendor, total in vendor_summary.items():
                balance = calculate_vendor_balance(vendor)
                st.metric(
                    label=f"{vendor}",
                    value=f"Rs. {total:,.2f}",
                    delta=f"Balance: Rs. {balance:,.2f}",
                    delta_color="inverse" if balance > 0 else "normal"
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
                # Get unique vendor names
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

            add_payment = st.form_submit_button("💾 Add Payment", type="primary", use_container_width=True)

        if add_payment:
            if selected_vendor and payment_amount > 0:
                # Add to vendor payments
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

        # Edit Payment Section
        if st.session_state.vendor_payments:
            st.markdown('<div class="section-header">', unsafe_allow_html=True)
            st.subheader("✏️ Edit Payment")
            st.markdown('</div>', unsafe_allow_html=True)

            payment_to_edit = st.selectbox("Select Payment to Edit", 
                                         [f"{p['id']} - {p['vendor_name']} - Rs. {p['amount']} - {p['date']}" 
                                          for p in st.session_state.vendor_payments],
                                         key="edit_payment_select")

            if payment_to_edit:
                payment_id = int(payment_to_edit.split(" - ")[0])
                payment = next((p for p in st.session_state.vendor_payments if p['id'] == payment_id), None)

                if payment:
                    with st.form("edit_payment_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            edit_vendor = st.text_input("Vendor Name", value=payment['vendor_name'], key="edit_payment_vendor")
                            edit_amount = st.number_input("Amount", value=payment['amount'], key="edit_payment_amount")
                        with col2:
                            edit_date = st.date_input("Date", value=datetime.strptime(payment['date'], "%Y-%m-%d"), key="edit_payment_date")
                            edit_method = st.selectbox("Method", ["Bank Transfer", "Cash", "Cheque", "Online"], 
                                                     index=["Bank Transfer", "Cash", "Cheque", "Online"].index(payment['method']),
                                                     key="edit_payment_method")
                        
                        edit_notes = st.text_area("Notes", value=payment['notes'], key="edit_payment_notes")

                        col1, col2 = st.columns(2)
                        with col1:
                            update_payment = st.form_submit_button("🔄 Update Payment", use_container_width=True)
                        with col2:
                            delete_payment = st.form_submit_button("🗑️ Delete Payment", type="secondary", use_container_width=True)

                        if update_payment:
                            payment['vendor_name'] = edit_vendor
                            payment['amount'] = edit_amount
                            payment['date'] = edit_date.strftime("%Y-%m-%d")
                            payment['method'] = edit_method
                            payment['notes'] = edit_notes
                            auto_save()
                            show_alert("Payment updated successfully!", "success")
                            st.rerun()

                        if delete_payment:
                            st.session_state.vendor_payments = [p for p in st.session_state.vendor_payments if p['id'] != payment_id]
                            auto_save()
                            show_alert("Payment deleted successfully!", "success")
                            st.rerun()

        # Vendor balances section
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.subheader("🏦 Vendor Balances")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.vendor_ledger:
            # Calculate balances for all vendors
            vendor_balances = {}
            for vendor in set([v['vendor_name'] for v in st.session_state.vendor_ledger]):
                vendor_balances[vendor] = calculate_vendor_balance(vendor)

            # Display vendor balances
            for vendor, balance in vendor_balances.items():
                balance_color = "🔴" if balance > 0 else "🟢"
                st.markdown(f"""
                <div class="vendor-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <b>{vendor}</b><br>
                            <small>Outstanding Balance</small>
                        </div>
                        <div style="text-align: right;">
                            <b style="color: {'#e74c3c' if balance > 0 else '#27ae60'}; font-size: 1.2em;">
                                {balance_color} Rs. {abs(balance):,.2f}
                            </b>
                            <br>
                            <small>{'Amount Due' if balance > 0 else 'No Dues'}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No vendor transactions available.")

        # Payment history
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.subheader("📋 Payment History")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.vendor_payments:
            for payment in st.session_state.vendor_payments[::-1]:  # Show latest first
                st.markdown(f"""
                <div class="payment-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <b>{payment['vendor_name']}</b><br>
                            <small>Date: {payment['date']} | Method: {payment['method']}</small>
                            {f"<br><small>Notes: {payment['notes']}</small>" if payment['notes'] else ""}
                        </div>
                        <div style="text-align: right;">
                            <b style="color: #27ae60; font-size: 1.2em;">Rs. {payment['amount']:,.2f}</b>
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

                    # PDF Download for chemical report
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

            if st.button("📦 Packaging Stock Report", use_container_width=True, key="pack_report"):
                if st.session_state.packaging_materials:
                    packaging_data = []
                    for p_type, material in st.session_state.packaging_materials.items():
                        packaging_data.append({
                            'Type': p_type,
                            'Description': material['name'],
                            'Current Stock': material['stock'],
                            'Rate (Per Unit)': f"Rs. {material['rate']:.2f}",
                            'Status': 'Out of Stock' if material['stock'] <= 0 else 'Low Stock' if material['stock'] <
                                                                                                   st.session_state.settings[
                                                                                                       'packaging_low_stock'] else 'Adequate'
                        })

                    df = pd.DataFrame(packaging_data)
                    st.subheader("Packaging Stock Report")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No packaging materials available for report.")

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

                    # PDF Download for vendor report
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

            if st.button("⚠️ Low Stock Alert Report", use_container_width=True, key="low_stock_report"):
                low_stock_chemicals = [chem for chem in st.session_state.chemicals if
                                       0 < chem['stock'] < st.session_state.settings['low_stock_threshold']]
                out_of_stock_chemicals = [chem for chem in st.session_state.chemicals if chem['stock'] <= 0]
                low_stock_packaging = [material for material in st.session_state.packaging_materials.values() if
                                       0 < material['stock'] < st.session_state.settings['packaging_low_stock']]
                out_of_stock_packaging = [material for material in st.session_state.packaging_materials.values() if
                                          material['stock'] <= 0]

                if any([low_stock_chemicals, out_of_stock_chemicals, low_stock_packaging, out_of_stock_packaging]):
                    st.subheader("Low Stock Alert Report")

                    if out_of_stock_chemicals:
                        st.error("🚨 OUT OF STOCK - CHEMICALS (IMMEDIATE ACTION REQUIRED)")
                        for chem in out_of_stock_chemicals:
                            st.write(f"- {chem['name']}: 0.00 KG")

                    if low_stock_chemicals:
                        st.warning("⚠️ LOW STOCK - CHEMICALS (NEEDS ATTENTION)")
                        for chem in low_stock_chemicals:
                            st.write(f"- {chem['name']}: {chem['stock']:.2f} KG")

                    if out_of_stock_packaging:
                        st.error("🚨 OUT OF STOCK - PACKAGING (IMMEDIATE ACTION REQUIRED)")
                        for material in out_of_stock_packaging:
                            st.write(f"- {material['name']}: 0 units")

                    if low_stock_packaging:
                        st.warning("⚠️ LOW STOCK - PACKAGING (NEEDS ATTENTION)")
                        for material in low_stock_packaging:
                            st.write(f"- {material['name']}: {material['stock']} units")
                else:
                    st.success("✅ No low stock items. All inventory levels are adequate.")

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

            save_settings = st.form_submit_button("Save Settings", type="primary", use_container_width=True)

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

        # Data Management
        st.subheader("Data Management")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 Export Data", use_container_width=True, key="export_data"):
                data = {
                    'chemicals': st.session_state.chemicals,
                    'packaging_materials': st.session_state.packaging_materials,
                    'vendor_ledger': st.session_state.vendor_ledger,
                    'vendor_payments': st.session_state.vendor_payments,
                    'production_history': st.session_state.production_history,
                    'product_details': st.session_state.product_details,
                    'settings': st.session_state.settings
                }

                json_data = json.dumps(data, indent=2)
                st.download_button(
                    label="Download Data",
                    data=json_data,
                    file_name=f"{st.session_state.settings['company_name'].replace(' ', '_')}_backup_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="dl_data"
                )

        with col2:
            uploaded_file = st.file_uploader("Import Data", type="json", key="import_data")
            if uploaded_file is not None:
                try:
                    data = json.load(uploaded_file)
                    if st.button("Import Data", type="primary", use_container_width=True, key="import_btn"):
                        st.session_state.chemicals = data.get('chemicals', [])
                        st.session_state.packaging_materials = data.get('packaging_materials', {})
                        st.session_state.vendor_ledger = data.get('vendor_ledger', [])
                        st.session_state.vendor_payments = data.get('vendor_payments', [])
                        st.session_state.production_history = data.get('production_history', [])
                        st.session_state.product_details = data.get('product_details', {})
                        st.session_state.settings = data.get('settings', st.session_state.settings)
                        auto_save()
                        show_alert("Data imported successfully!", "success")
                        st.rerun()
                except Exception as e:
                    show_alert(f"Error importing data: {str(e)}", "error")

        with col3:
            if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True, key="clear_data"):
                if st.checkbox("I understand this will delete all data permanently", key="confirm_clear"):
                    if st.button("Confirm Clear All Data", type="primary", use_container_width=True,
                                 key="confirm_clear_btn"):
                        st.session_state.chemicals = []
                        st.session_state.packaging_materials = {}
                        st.session_state.vendor_ledger = []
                        st.session_state.vendor_payments = []
                        st.session_state.production_history = []
                        st.session_state.product_details = {}
                        auto_save()
                        show_alert("All data cleared successfully!", "success")
                        st.rerun()

    # Data Import/Export Section
    elif choice == "Data Import/Export":
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.title("📊 Data Import/Export")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📤 Export Data")

            # Export to CSV
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

            # Download Sample CSV Template
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
                    # Preview available files
                    with zipfile.ZipFile(uploaded_file) as z:
                        file_list = z.namelist()
                        st.write("Files found in ZIP:")
                        for file in file_list:
                            st.write(f"- {file}")

                    if st.button("🚀 Import Data", type="primary", use_container_width=True, key="import_data_btn"):
                        with st.spinner("Importing data..."):
                            imported_data = import_from_csv(uploaded_file)

                            # Update session state with imported data
                            if 'chemicals' in imported_data:
                                st.session_state.chemicals = imported_data['chemicals']
                            if 'packaging_materials' in imported_data:
                                st.session_state.packaging_materials = imported_data['packaging_materials']
                            if 'vendor_ledger' in imported_data:
                                st.session_state.vendor_ledger = imported_data['vendor_ledger']
                            if 'vendor_payments' in imported_data:
                                st.session_state.vendor_payments = imported_data['vendor_payments']
                            if 'production_history' in imported_data:
                                st.session_state.production_history = imported_data['production_history']
                            if 'product_details' in imported_data:
                                st.session_state.product_details = imported_data['product_details']

                            auto_save()
                            show_alert("Data imported successfully!", "success")
                            st.rerun()

                except Exception as e:
                    show_alert(f"Error reading ZIP file: {str(e)}", "error")

        # Data Management
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.subheader("🗃️ Data Management")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            # Export to JSON (existing functionality)
            if st.button("💾 Export to JSON", use_container_width=True, key="export_json"):
                data = {
                    'chemicals': st.session_state.chemicals,
                    'packaging_materials': st.session_state.packaging_materials,
                    'vendor_ledger': st.session_state.vendor_ledger,
                    'vendor_payments': st.session_state.vendor_payments,
                    'production_history': st.session_state.production_history,
                    'product_details': st.session_state.product_details,
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
            # Import from JSON (existing functionality)
            uploaded_json = st.file_uploader("Import JSON", type="json", key="import_json")
            if uploaded_json is not None:
                try:
                    data = json.load(uploaded_json)
                    if st.button("Import JSON Data", type="primary", use_container_width=True, key="import_json_btn"):
                        st.session_state.chemicals = data.get('chemicals', [])
                        st.session_state.packaging_materials = data.get('packaging_materials', {})
                        st.session_state.vendor_ledger = data.get('vendor_ledger', [])
                        st.session_state.vendor_payments = data.get('vendor_payments', [])
                        st.session_state.production_history = data.get('production_history', [])
                        st.session_state.product_details = data.get('product_details', {})
                        st.session_state.settings = data.get('settings', st.session_state.settings)
                        auto_save()
                        show_alert("Data imported successfully!", "success")
                        st.rerun()
                except Exception as e:
                    show_alert(f"Error importing data: {str(e)}", "error")

        with col3:
            # Clear data (existing functionality)
            if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True, key="clear_data"):
                if st.checkbox("I understand this will delete all data permanently", key="confirm_clear"):
                    if st.button("Confirm Clear All Data", type="primary", use_container_width=True,
                                 key="confirm_clear_btn"):
                        st.session_state.chemicals = []
                        st.session_state.packaging_materials = {}
                        st.session_state.vendor_ledger = []
                        st.session_state.vendor_payments = []
                        st.session_state.production_history = []
                        st.session_state.product_details = {}
                        auto_save()
                        show_alert("All data cleared successfully!", "success")
                        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 2px solid #1E90FF;'>
            <h3 style='color: #1E90FF;'>Green<span style='color: #00FF00;'>Chemical</span>Solutions</h3>
            <p style='color: #000000;'>For any query please feel free to contact: <a href='tel:+923207429422' style='color: #1E90FF;'>+92-3207429422</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
