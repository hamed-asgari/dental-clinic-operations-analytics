# Dental Clinic Operations Analytics

A portfolio project that demonstrates how SQL, Python, and Power BI can support operational decision-making in a dental clinic.

## Project status
Version 0.1 - repository structure and synthetic data pipeline.

## Problem
Dental clinics often have fragmented information about appointments, cancellations, procedures, treatment plans, and payments. This project creates a synthetic dental-clinic database and analyzes operational performance without using real patient information.

## Objectives
- Design a relational data model for a dental clinic.
- Generate reproducible synthetic data.
- Load and query the data with SQL.
- Perform exploratory analysis with Python and pandas.
- Build a Power BI dashboard for clinic managers.
- Identify actionable opportunities to improve chair utilization, treatment acceptance, patient retention, and revenue per clinical hour.

## Planned KPIs
- Appointment no-show rate
- Cancellation rate
- Chair utilization
- Revenue per clinical hour
- Treatment-plan acceptance rate
- New-patient volume
- Patient retention
- Procedure mix
- Payment collection rate

## Repository structure
```text
.
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── data_dictionary.md
│   └── project_charter.md
├── images/
├── notebooks/
│   └── 01_eda.ipynb
├── powerbi/
│   └── README.md
├── sql/
│   ├── 01_schema.sql
│   └── 02_analytics_queries.sql
├── src/
│   └── generate_synthetic_data.py
├── .gitignore
├── LICENSE
└── requirements.txt
```

## Quick start
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python src/generate_synthetic_data.py
```

The script writes reproducible synthetic CSV files to `data/raw/`.

## Ethics and limitations
- All records in this repository are synthetic.
- The project is for education and portfolio demonstration only.
- It must not be used for clinical decisions.
- Results from synthetic data cannot be generalized to real clinics.

## Next milestones
- [ ] Review and finalize the data dictionary.
- [ ] Generate synthetic data and validate referential integrity.
- [ ] Create the SQL Server database.
- [ ] Write the first ten analytical queries.
- [ ] Complete exploratory data analysis.
- [ ] Build the first Power BI dashboard page.
