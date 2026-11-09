import json
import os
import time
import uuid
import pandas as pd
import streamlit as st

# Import patient monitoring engine
from patient_monitoring import PatientMonitoring

st.set_page_config(
    page_title="Excel-Style Triage & Alert System", layout="wide"
)

# Initialize Session State
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        columns=[
            "id",
            "Name",
            "Band ID",
            "ESI",
            "HR (bpm)",
            "SpO2 (%)",
            "Temp (°C)",
            "Watch Status",
            "Alert Status",
        ]
    )

if "monitors" not in st.session_state:
    st.session_state.monitors = {}

if "active_patient_id" not in st.session_state:
    st.session_state.active_patient_id = None

if "sorted_patient_ids" not in st.session_state:
    st.session_state.sorted_patient_ids = []

st.title("Patient Triage & Real-Time Alert System")


def close_patient_dialog():
    """Closes modal dialog and clears grid selection state in session state."""
    st.session_state.active_patient_id = None
    if "triage_dataframe_grid" in st.session_state:
        del st.session_state["triage_dataframe_grid"]
    st.rerun()


# --- DIALOG: PATIENT ACTION MENU ---
@st.dialog("📋 Patient Action Menu")
def manage_patient_dialog():
    patient_id = st.session_state.active_patient_id
    patient_row = st.session_state.df[st.session_state.df["id"] == patient_id]

    if patient_row.empty:
        st.warning("Patient record not found.")
        if st.button("Close"):
            close_patient_dialog()
        return

    patient_data = patient_row.iloc[0]
    p_index = patient_row.index[0]

    st.markdown(
        f"### **Patient:** {patient_data['Name']} &nbsp;|&nbsp; **Band ID:**"
        f" `{patient_data['Band ID']}`"
    )
    st.markdown(f"**Current Alert Status:** {patient_data['Alert Status']}")
    st.markdown("---")

    # Option 1: Change ESI Level
    st.markdown("#### 1️⃣ Change ESI Priority Level")
    current_esi = str(patient_data["ESI"])
    esi_options = ["1", "2", "3", "4", "5"]
    default_idx = (
        esi_options.index(current_esi) if current_esi in esi_options else 0
    )

    new_esi = st.selectbox(
        "Select New ESI Level",
        options=esi_options,
        index=default_idx,
        key=f"esi_select_{patient_id}",
    )
    if st.button(
        "Update ESI Level", use_container_width=True, type="secondary"
    ):
        st.session_state.df.loc[p_index, "ESI"] = new_esi
        close_patient_dialog()

    st.markdown("---")

    # Option 2: Put Status Back to Normal
    st.markdown("#### 2️⃣ Reset Patient Status to Normal")
    if st.button("🟢 Reset Status to Normal", use_container_width=True):
        monitor = st.session_state.monitors.get(patient_id)
        if monitor:
            monitor.reset_all_alerts()

        st.session_state.df.loc[p_index, "Alert Status"] = "🟢 Normal"
        close_patient_dialog()

    st.markdown("---")

    # Option 3: Check In Patient (Delete Record)
    st.markdown("#### 3️⃣ Check In Patient")
    st.caption(
        "Checking in the patient will process their admission and remove them"
        " from active triage."
    )
    if st.button(
        "✅ Check In Patient (Remove)", type="primary", use_container_width=True
    ):
        st.session_state.df = st.session_state.df[
            st.session_state.df["id"] != patient_id
        ].reset_index(drop=True)
        st.session_state.monitors.pop(patient_id, None)
        close_patient_dialog()

    st.markdown("---")
    if st.button("Cancel / Close", use_container_width=True):
        close_patient_dialog()


if st.session_state.active_patient_id:
    manage_patient_dialog()


# --- DIALOG: ADD PATIENT ---
@st.dialog("➕ Add New Patient & Baseline Vitals")
def add_patient_dialog():
    st.write("Enter patient details and initial vitals baseline.")

    c1, c2, c3 = st.columns(3)
    with c1:
        p_name = st.text_input("Patient Name", autocomplete="off")
    with c2:
        p_band = st.text_input(
            "Band ID (e.g. BAND-1, BAND-2)", autocomplete="off"
        )
    with c3:
        p_esi = st.selectbox("ESI Priority", options=["1", "2", "3", "4", "5"])

    st.markdown("---")
    t1, t2, t3 = st.columns(3)
    with t1:
        init_hr = st.number_input("Baseline HR (bpm)", value=75, step=1)
    with t2:
        init_spo2 = st.number_input("Baseline SpO2 (%)", value=98, step=1)
    with t3:
        init_temp = st.number_input(
            "Baseline Temp (°C)", value=37.0, step=0.1, format="%.1f"
        )

    if st.button("Confirm & Insert Row", type="primary", use_container_width=True):
        patient_id = str(uuid.uuid4())
        name = (
            p_name
            if p_name
            else f"Patient {len(st.session_state.df) + 1}"
        )
        band = p_band if p_band else f"BAND-{len(st.session_state.df) + 1}"

        baseline = {
            "bpm": float(init_hr),
            "temperature": float(init_temp),
            "spo2": float(init_spo2),
        }

        st.session_state.monitors[patient_id] = PatientMonitoring(
            patientId=patient_id, baseline=baseline, alert_callback=None
        )

        new_row = {
            "id": patient_id,
            "Name": name,
            "Band ID": band,
            "ESI": p_esi,
            "HR (bpm)": init_hr,
            "SpO2 (%)": init_spo2,
            "Temp (°C)": init_temp,
            "Watch Status": "🔴 Disconnected",
            "Alert Status": "🟢 Normal",
        }

        st.session_state.df.loc[len(st.session_state.df)] = new_row
        close_patient_dialog()


# --- LIVE TELEMETRY & SPREADSHEET FRAGMENT (1s Interval) ---
@st.fragment(run_every=1)
def render_excel_grid():
    live_data = {}

    if os.path.exists("live_vitals.json"):
        try:
            with open("live_vitals.json", "r") as f:
                live_data = json.load(f)
        except Exception:
            live_data = {}

    now = time.time()

    if len(st.session_state.df) > 0:
        for idx, row in st.session_state.df.iterrows():
            p_id = row.get("id")
            band_id = row.get("Band ID")
            monitor = st.session_state.monitors.get(p_id)

            patient_telemetry = live_data.get(band_id)
            if patient_telemetry and (
                now - patient_telemetry.get("timestamp", 0) < 5
            ):
                st.session_state.df.loc[idx, "Watch Status"] = "🟢 Connected"

                try:
                    c_hr = float(patient_telemetry["heart_rate"])
                    c_spo2 = float(patient_telemetry["spo2"])
                    c_temp = float(patient_telemetry["temperature"])

                    st.session_state.df.loc[idx, "HR (bpm)"] = c_hr
                    st.session_state.df.loc[idx, "SpO2 (%)"] = c_spo2
                    st.session_state.df.loc[idx, "Temp (°C)"] = c_temp

                    if monitor:
                        monitor.receive_reading(
                            bpm=c_hr, temperature=c_temp, spo2=c_spo2
                        )
                except (ValueError, TypeError, KeyError):
                    pass
            else:
                st.session_state.df.loc[idx, "Watch Status"] = "🔴 Disconnected"

            if monitor and monitor.activeAlerts:
                reasons = [a["reason"] for a in monitor.activeAlerts.values()]
                st.session_state.df.loc[idx, "Alert Status"] = (
                    f"⚠️ ALERT: {', '.join(reasons)}"
                )
            else:
                st.session_state.df.loc[idx, "Alert Status"] = "🟢 Normal"

    df_display = st.session_state.df.copy()

    # Priority Sorting: Active alerts float to top, then sorted by ESI level
    if len(df_display) > 0:
        df_display["is_alert"] = df_display["Alert Status"].apply(
            lambda x: 0 if "⚠️" in str(x) else 1
        )
        df_display["esi_rank"] = pd.to_numeric(
            df_display["ESI"], errors="coerce"
        ).fillna(99)
        df_display = df_display.sort_values(
            by=["is_alert", "esi_rank"]
        ).reset_index(drop=True)

    # Store ordered IDs for row selection mapping
    st.session_state.sorted_patient_ids = (
        df_display["id"].tolist() if len(df_display) > 0 else []
    )

    # --- CONTROL TOOLBAR (INSIDE FRAGMENT FOR INSTANT SELECTION SYNC) ---
    c_spacer, c_manage, c_add = st.columns([3.5, 1.5, 1.2])

    grid_state = st.session_state.get("triage_dataframe_grid", {})
    selected_rows = grid_state.get("selection", {}).get("rows", [])
    has_selection = (
        len(selected_rows) > 0
        and selected_rows[0] < len(st.session_state.sorted_patient_ids)
    )

    with c_manage:
        if st.button(
            "⚙️ Manage Selected Patient",
            use_container_width=True,
            disabled=not has_selection,
        ):
            selected_idx = selected_rows[0]
            st.session_state.active_patient_id = (
                st.session_state.sorted_patient_ids[selected_idx]
            )
            st.rerun()

    with c_add:
        if st.button("➕ Add Patient", type="primary", use_container_width=True):
            st.session_state.active_patient_id = None
            if "triage_dataframe_grid" in st.session_state:
                del st.session_state["triage_dataframe_grid"]
            add_patient_dialog()

    st.write("")

    display_cols = [
        c
        for c in df_display.columns
        if c not in ["id", "is_alert", "esi_rank"]
    ]

    st.dataframe(
        df_display[display_cols],
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
        key="triage_dataframe_grid",
        column_config={
            "Watch Status": st.column_config.TextColumn("Watch Status"),
            "Alert Status": st.column_config.TextColumn("Alert Status"),
        },
    )


render_excel_grid()