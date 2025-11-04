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

    # Chemical Stock Management (Updated with grams/kg handling)
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

        # Rest of the chemical management code remains the same...
        # [Previous chemical management code continues...]

    # The rest of the application code (Vendor Ledger, Vendor Payments, Reports, Settings, Data Import/Export)
    # remains largely the same but with the updated CSS styling...
    # [Previous code for other sections continues with the new styling...]

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
