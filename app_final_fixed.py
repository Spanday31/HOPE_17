# Improved SMART CVD Risk Reduction Calculator with Enhanced UI

import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(layout="wide")
st.markdown("""
    <div style='background-color:#0e1117;padding:1rem;border-radius:10px'>
        <h1 style='color:#ffffff;text-align:center;'>SMART CVD Risk Reduction Calculator</h1>
        <p style='color:#cccccc;text-align:center;'>Developed by Samuel Panday — 21/04/2025</p>
    </div>
""", unsafe_allow_html=True)

# Intervention data
interventions = [
    {"name": "Smoking cessation", "arr_lifetime": 17, "arr_5yr": 5},
    {"name": "Antiplatelet (ASA or clopidogrel)", "arr_lifetime": 6, "arr_5yr": 2},
    {"name": "BP control (ACEi/ARB ± CCB)", "arr_lifetime": 12, "arr_5yr": 4},
    {"name": "Semaglutide 2.4 mg", "arr_lifetime": 4, "arr_5yr": 1},
    {"name": "Weight loss to ideal BMI", "arr_lifetime": 10, "arr_5yr": 3},
    {"name": "Empagliflozin", "arr_lifetime": 6, "arr_5yr": 2},
    {"name": "Icosapent ethyl (TG ≥1.5)", "arr_lifetime": 5, "arr_5yr": 2},
    {"name": "Mediterranean diet", "arr_lifetime": 9, "arr_5yr": 3},
    {"name": "Physical activity", "arr_lifetime": 9, "arr_5yr": 3},
    {"name": "Alcohol moderation", "arr_lifetime": 5, "arr_5yr": 2},
    {"name": "Stress reduction", "arr_lifetime": 3, "arr_5yr": 1}
]

ldl_therapies = {
    "Atorvastatin 20 mg": 40,
    "Atorvastatin 80 mg": 50,
    "Rosuvastatin 10 mg": 40,
    "Rosuvastatin 20–40 mg": 55,
    "Simvastatin 40 mg": 35,
    "Ezetimibe": 20,
    "PCSK9 inhibitor": 60,
    "Bempedoic acid": 18
}

# SMART Risk Score Calculation

def estimate_smart_risk(age, sex, sbp, total_chol, hdl, smoker, diabetes, egfr, crp, vasc_count):
    sex_val = 1 if sex == "Male" else 0
    smoking_val = 1 if smoker else 0
    diabetes_val = 1 if diabetes else 0
    crp_log = math.log(crp + 1) if crp else 0
    lp = (0.064*age + 0.34*sex_val + 0.02*sbp + 0.25*total_chol -
          0.25*hdl + 0.44*smoking_val + 0.51*diabetes_val -
          0.2*(egfr/10) + 0.25*crp_log + 0.4*vasc_count)
    risk10 = 1 - 0.900**math.exp(lp - 5.8)
    return round(risk10 * 100, 1)

def convert_5yr_from_10yr(risk10):
    p = risk10 / 100
    return round((1 - (1-p)**0.5) * 100, 1)

# Main Form
col_input, col_output = st.columns([1, 2])

with col_input:
    with st.form("risk_inputs"):
        st.header("🧾 Patient Profile")
        age = st.slider("Age", 30, 90, 60)
        sex = st.radio("Sex", ["Male", "Female"], horizontal=True)
        smoker = st.checkbox("Smoking")
        diabetes = st.checkbox("Diabetes")

        st.header("🧪 Labs & Vascular Disease")
        egfr = st.slider("eGFR (mL/min/1.73 m²)", 15, 120, 80)
        total_chol = st.number_input("Total Cholesterol (mmol/L)", 2.0, 10.0, 5.0, 0.1)
        hdl = st.number_input("HDL‑C (mmol/L)", 0.5, 3.0, 1.0, 0.1)
        crp = st.number_input("hs‑CRP (mg/L)", 0.1, 20.0, 2.0, 0.1)
        baseline_ldl = st.number_input("Baseline LDL‑C (mmol/L)", 0.5, 6.0, 3.5, 0.1)
        hba1c = st.number_input("Latest HbA₁c (%)", 5.0, 12.0, 7.0, 0.1)

        st.markdown("**Vascular disease (tick all that apply):**")
        vasc = [
            st.checkbox("Coronary artery disease"),
            st.checkbox("Cerebrovascular disease"),
            st.checkbox("Peripheral artery disease")
        ]
        vasc_count = sum(vasc)

        st.header("💊 Therapy")
        pre_tx = st.multiselect("Pre-admission lipid-lowering therapy",
                                [f"{k} (↓{v}%)" for k, v in ldl_therapies.items()])
        add_tx = st.multiselect("Add-on lipid-lowering therapy",
                                [f"{k} (↓{v}%)" for k, v in ldl_therapies.items() if k not in [pt.split(" (")[0] for pt in pre_tx]])

        sbp_current = st.number_input("Current SBP (mmHg)", 80, 220, 145)
        sbp_target = st.number_input("Target SBP (mmHg)", 80, 220, 120)

        st.markdown("**🏃 Lifestyle and Other Interventions**")
        ivs = [iv["name"] for iv in interventions if st.checkbox(iv["name"])]

        horizon = st.radio("Time horizon", ["5yr", "10yr", "lifetime"], index=1)
        patient_mode = st.checkbox("Patient-friendly view")
        submitted = st.form_submit_button("📉 Calculate Risk")

with col_output:
    if submitted:
        risk10 = estimate_smart_risk(age, sex, sbp_current, total_chol, hdl, smoker, diabetes, egfr, crp, vasc_count)
        risk5 = convert_5yr_from_10yr(risk10)
        baseline_risk = risk5 if horizon == "5yr" else risk10
        caps = {"5yr": 80, "10yr": 85, "lifetime": 90}
        baseline_risk_capped = min(baseline_risk, caps[horizon])

        # LDL logic
        adjusted_ldl = baseline_ldl
        for pt in pre_tx:
            name = pt.split(" (")[0]
            adjusted_ldl *= (1 - ldl_therapies[name] / 100)
        adjusted_ldl = max(adjusted_ldl, 1.0)

        final_ldl = adjusted_ldl
        for at in add_tx:
            name = at.split(" (")[0]
            final_ldl *= (1 - (ldl_therapies[name] / 100) * 0.5)
        final_ldl = max(final_ldl, 1.0)

        remaining = baseline_risk_capped / 100
        for iv in interventions:
            if iv["name"] in ivs:
                arr = iv["arr_5yr"] if horizon == "5yr" else iv["arr_lifetime"]
                remaining *= (1 - arr / 100)

        if final_ldl < baseline_ldl:
            drop = baseline_ldl - final_ldl
            rrr_ldl = min(22 * drop, 35)
            remaining *= (1 - rrr_ldl / 100)

        if sbp_target < sbp_current:
            rrr_bp = min(15 * ((sbp_current - sbp_target) / 10), 20)
            remaining *= (1 - rrr_bp / 100)

        if hba1c > 7.0:
            rrr_hba1c = min((hba1c - 7.0) * 9, 30)
            remaining *= (1 - rrr_hba1c / 100)

        final_risk = round(remaining * 100, 1)
        arr = round(baseline_risk_capped - final_risk, 1)
        rrr = round(min((arr / baseline_risk_capped * 100), 75), 1) if baseline_risk_capped else 0

        if patient_mode:
            st.markdown("### ✅ Patient-Friendly Summary")
            st.write(f"Your starting risk over {horizon} was **{baseline_risk_capped}%**.")
            st.write(f"With the treatments selected, your new risk is **{final_risk}%**.")
            st.write(f"This means a risk reduction of **{arr} percentage points**.")
        else:
            st.metric("Baseline Risk", f"{baseline_risk_capped}%")
            st.metric("Post-intervention Risk", f"{final_risk}%")
            st.metric("Absolute Risk Reduction (ARR)", f"{arr} pp")
            st.metric("Relative Risk Reduction (RRR)", f"{rrr}%")
            st.write(f"Expected LDL‑C at 3 months: **{final_ldl:.2f} mmol/L**")

        fig, ax = plt.subplots()
        ax.bar(["Baseline", "After"], [baseline_risk_capped, final_risk],
               color=["#CC4444", "#44CC44"], alpha=0.9)
        ax.set_title("CVD Risk Reduction")
        ax.set_ylabel(f"{horizon} CVD Risk (%)")
        for i, v in enumerate([baseline_risk_capped, final_risk]):
            ax.text(i, v + 1, f"{v:.1f}%", ha='center', fontweight='bold')
        st.pyplot(fig)

st.markdown("---")
st.markdown("Created by PRIME team — King's College Hospital, London")
