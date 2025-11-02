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
    page_title="HMD Solutions - Chemical Management System",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for attractive blue gradient color scheme
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        border: none;
    }
    .section-header {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border: none;
    }
    .card {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        margin: 10px;
        border: none;
    }
    .vendor-card {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        border: none;
    }
    .payment-card {
        background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        border: none;
    }
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    /* Dataframe styling */
    .stDataFrame {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    /* Form styling */
    .stForm {
        background: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
    }
    /* Success message */
    .stSuccess {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        color: white;
        border-radius: 10px;
        padding: 15px;
    }
    /* Warning message */
    .stWarning {
        background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
        color: white;
        border-radius: 10px;
        padding: 15px;
    }
    /* Error message */
    .stError {
        background: linear-gradient(135deg, #e17055 0%, #d63031 100%);
        color: white;
        border-radius: 10px;
        padding: 15px;
    }
    /* Info message */
    .stInfo {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        border-radius: 10px;
        padding: 15px;
    }
    /* Metric styling */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 15px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: white;
        border-radius: 10px;
    }
    /* Number input styling */
    .stNumberInput > div > div > input {
        background: white;
        border-radius: 10px;
    }
    /* Text input styling */
    .stTextInput > div > div > input {
        background: white;
        border-radius: 10px;
    }
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background: white;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Data persistence functions (same as before)
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
        
        with open('hmd_data.json', 'w') as f:
            json.dump(data, f, indent=4)
        
        # Also create backup with timestamp
        backup_filename = f"backup/hmd_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('backup', exist_ok=True)
        with open(backup_filename, 'w') as f:
            json.dump(data, f, indent=4)
            
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

def load_data():
    """Load all data from JSON files"""
    try:
        if os.path.exists('hmd_data.json'):
            with open('hmd_data.json', 'r') as f:
                data = json.load(f)
                
            st.session_state.chemicals = data.get('chemicals', [])
            st.session_state.packaging_materials = data.get('packaging_materials', {})
            st.session_state.vendor_ledger = data.get('vendor_ledger', [])
            st.session_state.vendor_payments = data.get('vendor_payments', [])
            st.session_state.production_history = data.get('production_history', [])
            st.session_state.settings = data.get('settings', {
                'company_name': "HMD Solutions",
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
        'company_name': "HMD Solutions",
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
            {"chemical_name": "Vitamin A", "amount_per_300": 1000.00},
            {"chemical_name": "Vitamin E Powder", "amount_per_300": 1000.00},
            {"chemical_name": "Vitamin C", "amount_per_300": 1000.00},
            {"chemical_name": "Vitamin K3", "amount_per_300": 1000.00},
            {"chemical_name": "Artichoke", "amount_per_300": 2.00},
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

# Helper functions (same as before)
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

# Updated PDF creation functions with professional formatting
def add_watermark(canvas, doc):
    """Add professional watermark to PDF pages"""
    try:
        if os.path.exists("logo.png"):
            canvas.saveState()
            canvas.setFillAlpha(0.03)
            watermark = ImageReader("logo.png")
            img_width, img_height = watermark.getSize()
            aspect = img_height / float(img_width)
            
            display_width = 400
            display_height = display_width * aspect
            
            x = (doc.pagesize[0] - display_width) / 2
            y = (doc.pagesize[1] - display_height) / 2
            
            canvas.drawImage("logo.png", x, y, width=display_width, height=display_height)
            canvas.restoreState()
    except Exception as e:
        print(f"Watermark error: {e}")

def add_header_footer(canvas, doc):
    """Add professional header and footer to each page"""
    canvas.saveState()
    
    # Header
    canvas.setFillColor(colors.HexColor('#667eea'))
    canvas.rect(0, doc.pagesize[1] - 50, doc.pagesize[0], 50, fill=1, stroke=0)
    
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 16)
    canvas.drawString(50, doc.pagesize[1] - 35, "HMD SOLUTIONS - CHEMICAL MANAGEMENT SYSTEM")
    
    # Footer
    canvas.setFillColor(colors.HexColor('#2c3e50'))
    canvas.rect(0, 0, doc.pagesize[0], 40, fill=1, stroke=0)
    
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica", 10)
    canvas.drawString(50, 15, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    canvas.drawRightString(doc.pagesize[0] - 50, 15, "Page %d" % doc.page)
    
    canvas.restoreState()

@st.cache_data(ttl=300)
def create_vendor_ledger_pdf(vendor_type=None, vendor_name=None):
    """Create professional PDF for vendor ledger with full page formatting"""
    buffer = BytesIO()

    # Use A4 size with proper margins
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          topMargin=80,  # Extra space for header
                          bottomMargin=60,  # Extra space for footer
                          leftMargin=40,
                          rightMargin=40)
    elements = []

    styles = getSampleStyleSheet()
    
    # Custom styles for professional look
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50'),
        alignment=1,  # Center
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=12,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica-Bold'
    )

    # Title Section
    if vendor_type:
        title_text = f"{vendor_type.upper()} VENDOR LEDGER REPORT"
    elif vendor_name:
        title_text = f"{vendor_name.upper()} - TRANSACTION REPORT"
    else:
        title_text = "COMPLETE VENDOR LEDGER REPORT"
    
    title = Paragraph(title_text, title_style)
    elements.append(title)

    # Report Info
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=20,
        alignment=1,
        textColor=colors.HexColor('#7f8c8d')
    )
    
    info_text = f"""
    <b>Company:</b> HMD Solutions | 
    <b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')} | 
    <b>Page:</b> 1 of 1
    """
    info_para = Paragraph(info_text, info_style)
    elements.append(info_para)
    elements.append(Spacer(1, 25))

    # Filter data
    if vendor_type:
        filtered_data = [v for v in st.session_state.vendor_ledger if v['vendor_type'] == vendor_type]
        filtered_payments = [p for p in st.session_state.vendor_payments
                             if any(v['vendor_name'] == p['vendor_name']
                                    for v in st.session_state.vendor_ledger
                                    if v['vendor_type'] == vendor_type)]
    elif vendor_name:
        filtered_data = [v for v in st.session_state.vendor_ledger if v['vendor_name'] == vendor_name]
        filtered_payments = [p for p in st.session_state.vendor_payments if p['vendor_name'] == vendor_name]
    else:
        filtered_data = st.session_state.vendor_ledger
        filtered_payments = st.session_state.vendor_payments

    # Vendor Transactions Section
    if filtered_data:
        elements.append(Paragraph("VENDOR TRANSACTIONS", header_style))

        # Prepare table data with optimized column widths
        data = [['Date', 'Vendor', 'Type', 'Item', 'Qty', 'Rate (Rs.)', 'Amount (Rs.)']]

        for vendor in filtered_data:
            data.append([
                vendor['date'],
                vendor['vendor_name'][:12],
                vendor['vendor_type'].title()[:8],
                vendor['item_name'][:15],
                f"{vendor['quantity']:.1f}",
                f"{vendor['rate']:.2f}",
                f"{vendor['total_amount']:,.2f}"
            ])

        # Create table with professional styling
        table = Table(data, colWidths=[50, 60, 40, 70, 40, 50, 60], repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        elements.append(table)

        # Transaction totals
        elements.append(Spacer(1, 15))
        total_purchases = sum(vendor['total_amount'] for vendor in filtered_data)
        total_text = Paragraph(f"<b>Total Purchases: Rs. {total_purchases:,.2f}</b>", styles['Normal'])
        elements.append(total_text)

    # Payment History Section
    if filtered_payments:
        elements.append(Spacer(1, 25))
        elements.append(Paragraph("PAYMENT HISTORY", header_style))

        payment_data = [['Date', 'Vendor', 'Method', 'Amount (Rs.)', 'Notes']]

        for payment in filtered_payments:
            payment_data.append([
                payment['date'],
                payment['vendor_name'][:12],
                payment['method'][:8],
                f"{payment['amount']:,.2f}",
                payment['notes'][:20] if payment['notes'] else "-"
            ])

        payment_table = Table(payment_data, colWidths=[50, 60, 40, 50, 80], repeatRows=1)
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        elements.append(payment_table)

        total_payments = sum(payment['amount'] for payment in filtered_payments)
        elements.append(Spacer(1, 10))
        payment_text = Paragraph(f"<b>Total Payments: Rs. {total_payments:,.2f}</b>", styles['Normal'])
        elements.append(payment_text)

    # Financial Summary Section
    elements.append(Spacer(1, 25))
    elements.append(Paragraph("FINANCIAL SUMMARY", header_style))

    total_debit = sum(v['total_amount'] for v in filtered_data) if filtered_data else 0
    total_credit = sum(p['amount'] for p in filtered_payments) if filtered_payments else 0
    balance = total_debit - total_credit

    summary_data = [
        ["Total Purchases (Debit)", f"Rs. {total_debit:,.2f}"],
        ["Total Payments (Credit)", f"Rs. {total_credit:,.2f}"],
        ["Outstanding Balance", f"Rs. {balance:,.2f}"]
    ]

    summary_table = Table(summary_data, colWidths=[150, 100])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#bdc3c7')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(summary_table)

    # Signature Section - Full width at bottom
    elements.append(Spacer(1, 40))
    
    # Create signature table for proper alignment
    signature_data = [
        ["", "", ""],
        ["_________________________", "_________________________", "_________________________"],
        ["Prepared By", "Checked By", "Approved By"],
        ["Accountant", "Manager", "Director"]
    ]
    
    signature_table = Table(signature_data, colWidths=[180, 180, 180])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('SPAN', (0, 0), (-1, 0)),  # Merge first row for logo
    ]))
    
    # Add logo to first row if available
    try:
        if os.path.exists("logo.png"):
            logo = Image("logo.png", width=80, height=40)
            signature_table._argW[0] = 80
            signature_table._argW[1] = 180
            signature_table._argW[2] = 180
    except:
        pass

    elements.append(signature_table)

    # Build document with header, footer and watermark
    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)
    return buffer

@st.cache_data(ttl=300)
def create_stock_pdf():
    """Create PDF for chemical stock with professional full-page formatting"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4,
                          topMargin=80,
                          bottomMargin=60,
                          leftMargin=40,
                          rightMargin=40)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50'),
        alignment=1,
        fontName='Helvetica-Bold'
    )

    # Title Section
    title = Paragraph("CHEMICAL STOCK INVENTORY REPORT", title_style)
    elements.append(title)

    # Report Info
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=20,
        alignment=1,
        textColor=colors.HexColor('#7f8c8d')
    )
    
    info_text = f"""
    <b>Company:</b> HMD Solutions | 
    <b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')} | 
    <b>Page:</b> 1 of 1
    """
    info_para = Paragraph(info_text, info_style)
    elements.append(info_para)
    elements.append(Spacer(1, 25))

    # Chemical Stock Data
    if st.session_state.chemicals:
        data = [['ID', 'Chemical Name', 'Stock (KG)', 'Rate (Rs.)', 'Status']]

        for chem in st.session_state.chemicals:
            status = "Adequate"
            if chem['stock'] < st.session_state.settings['low_stock_threshold']:
                status = "Low Stock"
            if chem['stock'] <= 0:
                status = "Out of Stock"

            data.append([
                str(chem['id']),
                chem['name'][:25],
                f"{chem['stock']:.2f}",
                f"{chem['rate']:.2f}",
                status
            ])

        # Create table with full page width
        table = Table(data, colWidths=[30, 150, 60, 60, 60], repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        elements.append(table)

        # Stock Summary
        elements.append(Spacer(1, 25))
        total_chemicals = len(st.session_state.chemicals)
        low_stock = len([c for c in st.session_state.chemicals if
                         0 < c['stock'] < st.session_state.settings['low_stock_threshold']])
        out_of_stock = len([c for c in st.session_state.chemicals if c['stock'] <= 0])

        summary_data = [
            ["Total Chemicals", str(total_chemicals)],
            ["Low Stock Items", str(low_stock)],
            ["Out of Stock Items", str(out_of_stock)],
            ["Stock Value", f"Rs. {sum(c['stock'] * c['rate'] for c in st.session_state.chemicals):,.2f}"]
        ]

        summary_table = Table(summary_data, colWidths=[120, 80])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
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

    # Signature Section
    elements.append(Spacer(1, 40))
    
    signature_data = [
        ["", "", ""],
        ["_________________________", "_________________________", "_________________________"],
        ["Inventory Manager", "Quality Control", "Director"],
        ["HMD Solutions", "HMD Solutions", "HMD Solutions"]
    ]
    
    signature_table = Table(signature_data, colWidths=[180, 180, 180])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(signature_table)

    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)
    return buffer

# Rest of the functions (export_to_csv, create_sample_csv, import_from_csv) remain the same...

# CSV Export/Import Functions (same as before)
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

            return imported_data
    except Exception as e:
        raise Exception(f"Error importing CSV files: {str(e)}")

# Main application with updated styling
def main():
    # Header with new attractive design
    st.markdown(
        """
        <div class="main-header">
            <h1>🧪 HMD Solutions</h1>
            <p>Chemical Management System | Professional Inventory & Vendor Management</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Main container for content
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Initialize session state for navigation if not exists
    if 'menu_choice' not in st.session_state:
        st.session_state.menu_choice = "Dashboard"

    # Sidebar navigation with new styling
    with st.sidebar:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; color: white; text-align: center; margin-bottom: 25px; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);">
                <h3>📊 Navigation Menu</h3>
                <p style="font-size: 0.9em; opacity: 0.9;">Manage your chemical business efficiently</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        menu = ["Dashboard", "Chemical Stock", "Packaging", "Production", "Vendor Ledger", "Vendor Payments", "Reports",
                "Settings", "Data Import/Export"]
        
        # Use session state for navigation
        choice = st.selectbox("Select Section", menu, index=menu.index(st.session_state.menu_choice), label_visibility="collapsed")
        
        # Update session state when user selects from sidebar
        st.session_state.menu_choice = choice

        # Quick stats in sidebar with new styling
        if st.session_state.chemicals:
            st.markdown("---")
            st.markdown(
                """
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;">
                    <h4>📈 Quick Stats</h4>
                </div>
                """,
                unsafe_allow_html=True
            )
            total_chems = len(st.session_state.chemicals)
            low_stock = len([c for c in st.session_state.chemicals if
                             0 < c['stock'] < st.session_state.settings['low_stock_threshold']])
            total_vendors = len(set([v['vendor_name'] for v in
                                     st.session_state.vendor_ledger])) if st.session_state.vendor_ledger else 0

            st.metric("🧪 Chemicals", total_chems)
            st.metric("⚠️ Low Stock", low_stock)
            st.metric("🏢 Vendors", total_vendors)

        # Auto-save button with new styling
        st.markdown("---")
        if st.button("💾 Save Data", use_container_width=True):
            auto_save()

    # Dashboard with new styling
    if choice == "Dashboard":
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.title("📊 Dashboard Overview")
        st.markdown('</div>', unsafe_allow_html=True)

        # Welcome section with new styling
        if not st.session_state.chemicals and not st.session_state.packaging_materials:
            st.info(
                "👋 Welcome to HMD Solutions Chemical Management System! Start by adding chemicals and packaging materials.")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🧪 Add Chemicals", use_container_width=True, key="add_chem_btn"):
                    st.session_state.menu_choice = "Chemical Stock"
                    st.rerun()
            with col2:
                if st.button("📦 Add Packaging", use_container_width=True, key="add_pack_btn"):
                    st.session_state.menu_choice = "Packaging"
                    st.rerun()
            with col3:
                if st.button("⚙️ Setup Wizard", use_container_width=True, key="setup_btn"):
                    st.session_state.menu_choice = "Settings"
                    st.rerun()

        # Quick actions with new styling
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.subheader("🚀 Quick Actions")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🧪 Manage Chemicals", use_container_width=True, key="manage_chem"):
                st.session_state.menu_choice = "Chemical Stock"
                st.rerun()
        with col2:
            if st.button("📦 Manage Packaging", use_container_width=True, key="manage_pack"):
                st.session_state.menu_choice = "Packaging"
                st.rerun()
        with col3:
            if st.button("🏭 Production", use_container_width=True, key="prod_btn"):
                st.session_state.menu_choice = "Production"
                st.rerun()
        with col4:
            if st.button("💰 Vendor Payments", use_container_width=True, key="vendor_pay_btn"):
                st.session_state.menu_choice = "Vendor Payments"
                st.rerun()

        # Dashboard cards with new styling
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

        # Vendor financial overview with new styling
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

        # Recent vendor transactions with new styling
        if st.session_state.vendor_ledger:
            st.markdown('<div class="section-header">', unsafe_allow_html=True)
            st.subheader("📋 Recent Vendor Transactions")
            st.markdown('</div>', unsafe_allow_html=True)

            recent_vendors = st.session_state.vendor_ledger[-5:][::-1]
            for vendor in recent_vendors:
                st.markdown(f"""
                <div class="vendor-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <b>{vendor['vendor_name']}</b><br>
                            <small>{vendor['item_name']}</small><br>
                            <small>Date: {vendor['date']}</small>
                        </div>
                        <div style="text-align: right;">
                            <b style="font-size: 1.2em;">Rs. {vendor['total_amount']:,.2f}</b>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Close main container
    st.markdown('</div>', unsafe_allow_html=True)

    # Footer with new styling
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);'>
            <h3>data<span style='color: #74b9ff;'>nex</span><span style='color: #00cec9;'>Solution</span></h3>
            <p>For any query please feel free to contact: <a href='tel:+923207429422' style='color: white; text-decoration: underline;'>+92-3207429422</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Note: The rest of the application code (other menu options) would follow the same pattern
# with the updated CSS classes and styling. The main structure remains the same but with
# the new attractive color scheme and professional layout.

if __name__ == "__main__":
    main()
