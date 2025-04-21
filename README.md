# SMART CVD Risk Reduction App

This Streamlit app estimates cardiovascular risk using clinical inputs and therapy scenarios, designed for post-MI patients as part of the PRIME clinic (King's College Hospital).

## Features
- SMART Risk Score–based 5-year, 10-year, and lifetime CVD risk
- LDL-C lowering projection based on evidence-based therapies
- Visual display of ARR and RRR
- Designed for ease of use in clinic settings

## Setup

### 1. Clone or download the repository

```bash
git clone https://github.com/yourusername/smart-risk-app.git
cd smart-risk-app
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app_final_fixed.py
```

Make sure `logo.png` is in the same directory to display the PRIME logo.

## Deployment

To deploy on [Streamlit Cloud](https://streamlit.io/cloud):
- Upload the repo
- Include `app_final_fixed.py`, `requirements.txt`, and `.streamlit/config.toml`
- Set `app_final_fixed.py` as the entry point

---
Created by **Dr Samuel Panday**  
PRIME Clinic, King's College Hospital
