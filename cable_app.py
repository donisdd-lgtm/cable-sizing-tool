"""
Electrical Cable Sizing App based on Indian Standards (IS 7098 Part 1)
XLPE Armoured Cables
"""

import streamlit as st
import math
from fpdf import FPDF
from datetime import datetime
import io

# Current Rating (Amps) for COPPER cables (Armoured, XLPE insulated)
COPPER_CURRENT_RATINGS = {
    1.5: {"ground": 17, "free_air": 24, "pipe_duct": 15},
    2.5: {"ground": 27, "free_air": 38, "pipe_duct": 24},
    4: {"ground": 36, "free_air": 51, "pipe_duct": 32},
    6: {"ground": 46, "free_air": 65, "pipe_duct": 41},
    10: {"ground": 63, "free_air": 89, "pipe_duct": 56},
    16: {"ground": 85, "free_air": 119, "pipe_duct": 76},
    25: {"ground": 111, "free_air": 155, "pipe_duct": 100},
    35: {"ground": 135, "free_air": 188, "pipe_duct": 122},
    50: {"ground": 163, "free_air": 227, "pipe_duct": 148},
    70: {"ground": 203, "free_air": 284, "pipe_duct": 184},
    95: {"ground": 244, "free_air": 340, "pipe_duct": 221},
    120: {"ground": 280, "free_air": 390, "pipe_duct": 254},
    150: {"ground": 315, "free_air": 438, "pipe_duct": 286},
    185: {"ground": 353, "free_air": 492, "pipe_duct": 320},
    240: {"ground": 406, "free_air": 565, "pipe_duct": 368},
    300: {"ground": 456, "free_air": 635, "pipe_duct": 414},
    400: {"ground": 545, "free_air": 760, "pipe_duct": 496},
}

# Current Rating (Amps) for ALUMINIUM cables (Armoured, XLPE insulated)
ALUMINIUM_CURRENT_RATINGS = {
    1.5: {"ground": 13, "free_air": 18, "pipe_duct": 11},
    2.5: {"ground": 20, "free_air": 28, "pipe_duct": 18},
    4: {"ground": 27, "free_air": 38, "pipe_duct": 24},
    6: {"ground": 34, "free_air": 48, "pipe_duct": 30},
    10: {"ground": 46, "free_air": 65, "pipe_duct": 41},
    16: {"ground": 63, "free_air": 88, "pipe_duct": 57},
    25: {"ground": 82, "free_air": 114, "pipe_duct": 73},
    35: {"ground": 100, "free_air": 139, "pipe_duct": 90},
    50: {"ground": 121, "free_air": 169, "pipe_duct": 109},
    70: {"ground": 151, "free_air": 211, "pipe_duct": 136},
    95: {"ground": 182, "free_air": 254, "pipe_duct": 163},
    120: {"ground": 209, "free_air": 292, "pipe_duct": 188},
    150: {"ground": 234, "free_air": 327, "pipe_duct": 210},
    185: {"ground": 263, "free_air": 368, "pipe_duct": 236},
    240: {"ground": 303, "free_air": 424, "pipe_duct": 272},
    300: {"ground": 340, "free_air": 475, "pipe_duct": 305},
    400: {"ground": 408, "free_air": 570, "pipe_duct": 366},
}

# Voltage Drop Factors (mV/A/m) for COPPER cables (Armoured, XLPE)
COPPER_VOLTAGE_DROP_FACTORS = {
    1.5: 29.50,
    2.5: 17.80,
    4: 11.00,
    6: 7.41,
    10: 4.40,
    16: 2.75,
    25: 1.75,
    35: 1.25,
    50: 0.89,
    70: 0.63,
    95: 0.47,
    120: 0.37,
    150: 0.30,
    185: 0.24,
    240: 0.18,
    300: 0.15,
    400: 0.11,
}

# Voltage Drop Factors (mV/A/m) for ALUMINIUM cables (Armoured, XLPE)
ALUMINIUM_VOLTAGE_DROP_FACTORS = {
    1.5: 47.20,
    2.5: 28.50,
    4: 17.60,
    6: 11.80,
    10: 7.04,
    16: 4.40,
    25: 2.80,
    35: 2.00,
    50: 1.42,
    70: 1.00,
    95: 0.75,
    120: 0.59,
    150: 0.47,
    185: 0.38,
    240: 0.29,
    300: 0.24,
    400: 0.18,
}

def calculate_current(load_value, load_type, voltage, power_factor):
    """
    Calculate Full Load Current (FLC) in Amps based on load and voltage.
    
    Parameters:
    -----------
    load_value : float
        The load value in the specified unit
    load_type : str
        Type of load: "kW", "HP", or "Amps"
    voltage : int or float
        Supply voltage: 230V (single-phase) or 415V (three-phase)
    power_factor : float
        Power factor (0 to 1)
    
    Returns:
    --------
    float
        Full Load Current in Amps
    
    Raises:
    -------
    ValueError
        If invalid load_type or voltage is provided
    """
    import math
    
    # Validate inputs
    if load_type not in ["kW", "HP", "Amps"]:
        raise ValueError("load_type must be 'kW', 'HP', or 'Amps'")
    
    if voltage not in [230, 415]:
        raise ValueError("voltage must be 230V (single-phase) or 415V (three-phase)")
    
    if not 0 < power_factor <= 1:
        raise ValueError("power_factor must be between 0 and 1")
    
    # If already in Amps, return as is
    if load_type == "Amps":
        return load_value
    
    # Convert HP to kW if needed
    if load_type == "HP":
        load_kw = load_value * 0.746
    else:  # load_type == "kW"
        load_kw = load_value
    
    # Calculate current based on voltage (single-phase or three-phase)
    if voltage == 230:
        # Single-phase: I = P / (V × PF)
        current = (load_kw * 1000) / (voltage * power_factor)
    else:  # voltage == 415
        # Three-phase: I = P / (√3 × V × PF)
        current = (load_kw * 1000) / (math.sqrt(3) * voltage * power_factor)
    
    return round(current, 2)


def select_cable(calculated_current, conductor_type, installation_method, length, 
                 derating_factor, max_voltage_drop_percent, voltage=415):
    """
    Select the appropriate cable size based on current and voltage drop criteria.
    
    Parameters:
    -----------
    calculated_current : float
        The full load current in Amps
    conductor_type : str
        Type of conductor: "Cu" (Copper) or "Al" (Aluminium)
    installation_method : str
        Installation method: "ground", "free_air", or "pipe_duct"
    length : float
        Cable length in meters
    derating_factor : float
        Derating factor to apply (0 to 1)
    max_voltage_drop_percent : float
        Maximum allowable voltage drop percentage (typically 3%)
    voltage : int or float
        Supply voltage: 230V or 415V (default: 415V)
    
    Returns:
    --------
    dict
        Dictionary containing:
        - 'size': Selected cable size (mm²)
        - 'actual_capacity': Derated cable capacity (Amps)
        - 'voltage_drop': Voltage drop (%)
        - 'voltage_drop_mv': Voltage drop (mV/m)
        - 'status': 'Selected' or error message
    
    Raises:
    -------
    ValueError
        If invalid conductor_type, installation_method, or no suitable cable found
    """
    
    # Select appropriate dictionaries
    if conductor_type.upper() == "CU":
        current_dict = COPPER_CURRENT_RATINGS
        vd_dict = COPPER_VOLTAGE_DROP_FACTORS
    elif conductor_type.upper() == "AL":
        current_dict = ALUMINIUM_CURRENT_RATINGS
        vd_dict = ALUMINIUM_VOLTAGE_DROP_FACTORS
    else:
        raise ValueError("conductor_type must be 'Cu' or 'Al'")
    
    # Validate installation method
    if installation_method.lower() not in ["ground", "free_air", "pipe_duct"]:
        raise ValueError("installation_method must be 'ground', 'free_air', or 'pipe_duct'")
    
    # Get the installation method key
    method_key = installation_method.lower()
    
    # Iterate through cable sizes
    for size in sorted(current_dict.keys()):
        base_capacity = current_dict[size][method_key]
        derated_capacity = base_capacity * derating_factor
        
        # Check if derated capacity is greater than load current
        if derated_capacity >= calculated_current:
            # Calculate voltage drop
            vd_factor = vd_dict[size]  # mV/A/m
            voltage_drop_mv = vd_factor * calculated_current * length  # mV
            voltage_drop_percent = (voltage_drop_mv / (voltage * 1000)) * 100
            
            # Check if voltage drop is within acceptable limits
            if voltage_drop_percent <= max_voltage_drop_percent:
                return {
                    'size': size,
                    'actual_capacity': round(derated_capacity, 2),
                    'voltage_drop': round(voltage_drop_percent, 2),
                    'voltage_drop_mv': round(voltage_drop_mv / length, 3),  # mV/m
                    'status': 'Selected'
                }
    
    # If no suitable cable found, return error
    return {
        'size': None,
        'actual_capacity': None,
        'voltage_drop': None,
        'voltage_drop_mv': None,
        'status': f'No suitable cable found. Max voltage drop of {max_voltage_drop_percent}% exceeded.'
    }


import streamlit as st
import pandas as pd
from fpdf import FPDF

# --- 1. CONFIGURATION & DATA ---
AL_DATA_3PH = {
    16: [74, 73, 58], 25: [96, 99, 76], 35: [115, 122, 92],
    50: [135, 148, 110], 70: [167, 188, 135], 95: [200, 233, 162],
    120: [228, 271, 185], 150: [258, 311, 210], 185: [295, 362, 240],
    240: [345, 437, 280], 300: [390, 499, 315], 400: [450, 586, 365]
}

CU_DATA_3PH = {
    2.5: [39, 36, 29], 4: [48, 49, 38], 6: [60, 62, 47],
    10: [77, 85, 63], 16: [100, 115, 82], 25: [130, 148, 105],
    35: [155, 185, 125], 50: [180, 220, 145], 70: [225, 280, 180],
    95: [270, 350, 215]
}

VD_FACTORS_AL = {
    16: 4.1, 25: 2.5, 35: 1.8, 50: 1.3, 70: 0.9, 95: 0.7,
    120: 0.55, 150: 0.46, 185: 0.36, 240: 0.28, 300: 0.23, 400: 0.19
}
VD_FACTORS_CU = {
    2.5: 15.0, 4: 9.5, 6: 6.4, 10: 3.8, 16: 2.4, 25: 1.5,
    35: 1.1, 50: 0.8, 70: 0.55, 95: 0.42
}

# --- 2. DEFINE FUNCTIONS (MUST BE AT THE TOP) ---

def generate_pdf(selected_size, current_load, voltage_drop_percent, load_val, volt_val, cond_type, install_type):
    """Generates the PDF report and returns the binary data."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.cell(200, 10, txt="Electrical Inspectorate - Cable Selection Report", ln=1, align='C')
    pdf.cell(200, 10, txt="------------------------------------------------", ln=1, align='C')
    
    # Body
    pdf.cell(200, 10, txt=f"Load: {str(load_val)} | Voltage: {str(volt_val)}V", ln=1)
    pdf.cell(200, 10, txt=f"Calculated Current: {current_load:.2f} Amps", ln=1)
    pdf.cell(200, 10, txt=f"Cable Material: {cond_type} | Install: {install_type}", ln=1)
    pdf.ln(5)
    
    # Result
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt=f"Selected Size: {str(selected_size)} sq.mm", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Voltage Drop: {voltage_drop_percent:.2f}%", ln=1)
    
    # Footer
    pdf.ln(10)
    pdf.cell(200, 10, txt="Standard: IS 7098 Part 1 (XLPE)", ln=1, align='R')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 3. PAGE SETUP ---
st.set_page_config(page_title="BIS Cable Sizer", page_icon="⚡")
st.title("⚡ IS 7098 Cable Selection Calculator")

# --- 4. INPUTS ---
st.sidebar.header("1. System Details")


# ============================================================================
# STREAMLIT APPLICATION
# ============================================================================

def main():
    """Main Streamlit application for Cable Sizing."""
    
    # Page configuration
    st.set_page_config(page_title="Cable Sizer - IS 7098", layout="wide")
    st.title("⚡ Electrical Cable Sizing Tool")
    st.markdown("**Based on Indian Standards (IS 7098 Part 1) - XLPE Armoured Cables**")
    
    # ========================================================================
    # SIDEBAR - Input Parameters
    # ========================================================================
    with st.sidebar:
        st.header("📋 Input Parameters")
        
        # System Voltage
        st.subheader("System Configuration")
        voltage_phase = st.radio(
            "System Voltage",
            options=["1-Phase (230V)", "3-Phase (415V)"],
            index=1,
            help="Select single-phase or three-phase system",
            key="voltage_radio"
        )
        voltage = 230 if "1-Phase" in voltage_phase else 415
        
        # Load Type
        st.subheader("Load Details")
        load_type = st.radio(
            "Load Type",
            options=["kW", "HP", "Amps"],
            index=0,
            help="Select the unit of load",
            key="load_type_radio"
        )
        
        # Load Value
        load_value = st.number_input(
            f"Load Value ({load_type})",
            min_value=0.1,
            value=10.0,
            step=0.5,
            help=f"Enter the load in {load_type}",
            key="load_value_input"
        )
        
        # Power Factor (for kW and HP)
        if load_type in ["kW", "HP"]:
            power_factor = st.slider(
                "Power Factor",
                min_value=0.70,
                max_value=1.0,
                value=0.9,
                step=0.05,
                help="Power factor of the load (0.70 to 1.0)",
                key="pf_slider"
            )
        else:
            power_factor = 1.0
        
        st.divider()
        
        # Cable Configuration
        st.subheader("Cable Configuration")
        conductor_type = st.selectbox(
            "Conductor Material",
            options=["Copper (Cu)", "Aluminium (Al)"],
            index=0,
            help="Select cable conductor material",
            key="conductor_select"
        )
        conductor = "Cu" if "Copper" in conductor_type else "Al"
        
        installation_method = st.selectbox(
            "Installation Method",
            options=["Ground", "Free Air", "Pipe/Duct"],
            index=0,
            help="Select the cable installation method",
            key="method_select"
        )
        method_map = {"Ground": "ground", "Free Air": "free_air", "Pipe/Duct": "pipe_duct"}
        method = method_map[installation_method]
        
        st.divider()
        
        # Cable Length and Voltage Drop
        st.subheader("Cable Route & Limits")
        cable_length = st.number_input(
            "Cable Length (meters)",
            min_value=1,
            value=100,
            step=5,
            help="Total length of the cable run",
            key="cable_length_input"
        )
        
        max_voltage_drop = st.slider(
            "Max Voltage Drop %",
            min_value=1.0,
            max_value=5.0,
            value=3.0,
            step=0.5,
            help="Maximum allowable voltage drop (typically 3%)",
            key="max_vd_slider"
        )
        
        st.divider()
        
        # Derating Factors
        st.subheader("Derating Factors")
        temperature_factor = st.slider(
            "Temperature Derating Factor",
            min_value=0.50,
            max_value=1.0,
            value=0.8,
            step=0.05,
            help="Derating factor for ambient temperature",
            key="temp_derating_slider"
        )
        
        grouping_factor = st.slider(
            "Grouping Factor",
            min_value=0.50,
            max_value=1.0,
            value=1.0,
            step=0.05,
            help="Derating factor for cable grouping",
            key="grouping_slider"
        )
        
        # Combined derating factor
        total_derating = temperature_factor * grouping_factor
        st.info(f"**Combined Derating Factor**: {total_derating:.2f}")
    
    # ========================================================================
    # MAIN AREA - Results
    # ========================================================================
    
    # Calculate Full Load Current
    try:
        flc = calculate_current(load_value, load_type, voltage, power_factor)
        
        # Display Results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="System Voltage",
                value=f"{voltage}V",
                delta="3-Phase" if voltage == 415 else "Single-Phase"
            )
        
        with col2:
            st.metric(
                label="Load Value",
                value=f"{load_value} {load_type}"
            )
        
        with col3:
            st.metric(
                label="Full Load Current",
                value=f"{flc} A",
                delta="Calculated"
            )
        
        st.divider()
        
        # Select Cable
        cable_result = select_cable(
            calculated_current=flc,
            conductor_type=conductor,
            installation_method=method,
            length=cable_length,
            derating_factor=total_derating,
            max_voltage_drop_percent=max_voltage_drop,
            voltage=voltage
        )
        
        # Display Recommended Cable Size
        if cable_result['status'] == 'Selected':
            st.markdown("### 🎯 Recommended Cable Size")
            
            # Large green box with cable size
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.success(f"### {cable_result['size']} mm²")
            
            st.divider()
            
            # Cable Details Table
            st.markdown("### 📊 Cable Specifications")
            
            table_data = {
                "Parameter": [
                    "Base Rating (from IS 7098)",
                    "Derating Factor",
                    "Actual Capacity",
                    "Load Current",
                    "Safety Margin",
                    "Voltage Drop",
                    "Voltage Drop (mV/m)"
                ],
                "Value": [
                    f"{COPPER_CURRENT_RATINGS[cable_result['size']][method] if conductor == 'Cu' else ALUMINIUM_CURRENT_RATINGS[cable_result['size']][method]} A",
                    f"{total_derating:.2f}",
                    f"{cable_result['actual_capacity']} A",
                    f"{flc} A",
                    f"{cable_result['actual_capacity'] - flc:.2f} A ({((cable_result['actual_capacity'] - flc) / flc * 100):.1f}%)",
                    f"{cable_result['voltage_drop']} %",
                    f"{cable_result['voltage_drop_mv']} mV/m"
                ]
            }
            
            st.dataframe(table_data, use_container_width=True, hide_index=True)
            
            # Voltage Drop Warning
            if cable_result['voltage_drop'] > 3.0:
                st.warning(
                    f"⚠️ **Voltage Drop Alert**: The voltage drop is {cable_result['voltage_drop']}%, "
                    f"which exceeds the recommended limit of 3%. "
                    f"Consider using a larger cable size or reducing cable length."
                )
            else:
                st.info(
                    f"✅ **Voltage Drop OK**: {cable_result['voltage_drop']}% is within "
                    f"the acceptable limit of {max_voltage_drop}%"
                )
            
            st.divider()
            
            # Summary Box
            st.markdown("### 📋 Summary")
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            
            with summary_col1:
                st.metric("Cable Size", f"{cable_result['size']} mm²")
            
            with summary_col2:
                st.metric("Actual Capacity", f"{cable_result['actual_capacity']} A")
            
            with summary_col3:
                st.metric("Voltage Drop", f"{cable_result['voltage_drop']} %")
            
            st.divider()
            
            # Download Report Button
            st.markdown("### 📥 Download Report")
            
            pdf_data = generate_pdf(
                cable_result['size'], 
                flc, 
                cable_result['voltage_drop'], 
                load_value, 
                voltage, 
                conductor_type,
                installation_method
            )
            
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_data,
                file_name=f"Cable_Sizing_Report_{datetime.now().strftime('%d-%m-%Y_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        else:
            st.error(f"❌ {cable_result['status']}")
            st.info(
                "Try one of the following:\n"
                "- Reduce the load\n"
                "- Reduce the cable length\n"
                "- Increase the maximum voltage drop limit\n"
                "- Reduce the derating factors"
            )
        
    except Exception as e:
        st.error(f"Error in calculation: {str(e)}")


if __name__ == "__main__":
    main()
