import streamlit as st
import pandas as pd
import json
import os
import time
import uuid

# Page setup
st.set_page_config(page_title="Excel-Style Triage Spreadsheet", layout="wide")

# Initialize session state for DataFrame
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        "id",
        "Name", 
        "Band ID", 
        "ESI", 
        "HR (bpm)", 
        "SpO2 (%)", 
        "Temp (°C)", 
        "Watch Status"
    ])

# Initialize background storage for initial values keyed by patient ID
if "initial_vitals" not in st.session_state:
    st.session_state.initial_vitals = {}

st.title("Patient List")

# --- POPUP DIALOG: PROMPTS FOR INITIAL VALUES BEFORE ADDING ROW ---
@st.dialog("➕ Add New Patient & Configure Initial Vitals")
def add_patient_dialog():
    st.write("Enter patient information and initial baseline vitals before adding them to the spreadsheet.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        p_name = st.text_input("Patient Name", autocomplete="off")
    with c2:
        p_band = st.text_input("Band ID", autocomplete="off")
    with c3:
        p_esi = st.selectbox("ESI Priority", options=["1", "2", "3", "4", "5"])

    st.markdown("---")
    st.markdown("**Initial Baseline Vitals (Stored securely in background):**")
    
    t1, t2, t3 = st.columns(3)
    with t1:
        init_hr = st.text_input("Initial HR (bpm)", autocomplete="off")
    with t2:
        init_spo2 = st.text_input("Initial SpO2 (%)", autocomplete="off")
    with t3:
        init_temp = st.text_input("Initial Temp (°C)", autocomplete="off")

    if st.button("Confirm & Insert Row", type="primary", use_container_width=True):
        patient_id = str(uuid.uuid4())
        new_row = {
            "id": patient_id,
            "Name": p_name if p_name else f"Patient {len(st.session_state.df) + 1}",
            "Band ID": p_band if p_band else "--",
            "ESI": p_esi,
            "HR (bpm)": init_hr if init_hr else "--",
            "SpO2 (%)": init_spo2 if init_spo2 else "--",
            "Temp (°C)": init_temp if init_temp else "--",
            "Watch Status": "🔴 Disconnected"
        }
        
        # Store initial values securely in background
        st.session_state.initial_vitals[patient_id] = {
            "hr": init_hr if init_hr else "--",
            "spo2": init_spo2 if init_spo2 else "--",
            "temp": init_temp if init_temp else "--"
        }

        # Append row to DataFrame
        st.session_state.df.loc[len(st.session_state.df)] = new_row
        
        # Clear the data_editor widget cache so it forces a refresh with the new row
        if "excel_spreadsheet_grid" in st.session_state:
            del st.session_state["excel_spreadsheet_grid"]
            
        st.rerun()

# --- TOP ACTION BAR ---
col_spacer, col_btn = st.columns([5, 1.2])
with col_btn:
    if st.button("➕ Add Patient", type="primary"):
        add_patient_dialog()

st.write("")

# --- LIVE SPREADSHEET GRID FRAGMENT (Updates every 1s) ---
@st.fragment(run_every=1)
def render_excel_grid():
    live = None
    is_connected = False
    
    if os.path.exists("live_vitals.json"):
        try:
            file_age = time.time() - os.path.getmtime("live_vitals.json")
            if file_age < 3:
                is_connected = True
            
            with open("live_vitals.json", "r") as f:
                live = json.load(f)
        except Exception:
            is_connected = False

    df_display = st.session_state.df.copy()
    
    if len(df_display) > 0:
        for idx, row in df_display.iterrows():
            p_id = row.get("id")
            # Row 0 connects to active wristband
            if idx == 0:
                if is_connected:
                    df_display.loc[idx, "Watch Status"] = "🟢 Connected"
                    if live:
                        current_hr = live.get("heart_rate", "--")
                        current_spo2 = live.get("spo2", "--")
                        current_temp = live.get("temperature", "--")

                        df_display.loc[idx, "HR (bpm)"] = current_hr
                        df_display.loc[idx, "SpO2 (%)"] = current_spo2
                        df_display.loc[idx, "Temp (°C)"] = current_temp
                else:
                    df_display.loc[idx, "Watch Status"] = "🔴 Disconnected"
            else:
                df_display.loc[idx, "Watch Status"] = "🔴 Disconnected"

    # Display spreadsheet excluding the internal 'id' tracking column
    display_cols = [c for c in df_display.columns if c != "id"]
    
    edited_view = st.data_editor(
        df_display[display_cols],
        num_rows="fixed",         # Disables internal grid row additions
        hide_index=True,          # Removes the empty row index column on the left
        use_container_width=True,
        key="excel_spreadsheet_grid",
        column_config={
            "Watch Status": st.column_config.TextColumn("Watch Status", disabled=True)
        }
    )

    # Sync user edits back to session state dataframe
    for idx in range(len(edited_view)):
        if idx < len(st.session_state.df):
            p_id = st.session_state.df.loc[idx, "id"]
            for col in display_cols:
                st.session_state.df.loc[idx, col] = edited_view.loc[idx, col]
            st.session_state.df.loc[idx, "id"] = p_id

render_excel_grid()