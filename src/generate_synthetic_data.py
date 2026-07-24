"""Generate reproducible synthetic data for a dental clinic analytics portfolio.

The generated records are artificial and must not be interpreted as real clinical data.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--patients", type=int, default=2000)
    parser.add_argument("--appointments", type=int, default=8000)
    parser.add_argument("--output", type=Path, default=Path("data/raw"))
    return parser.parse_args()


def generate_patients(n: int) -> pd.DataFrame:
    registration = pd.to_datetime("2023-01-01") + pd.to_timedelta(
        RNG.integers(0, 1095, n), unit="D"
    )
    return pd.DataFrame({
        "patient_id": np.arange(1, n + 1),
        "birth_year": RNG.integers(1945, 2019, n),
        "sex": RNG.choice(["female", "male"], n, p=[0.54, 0.46]),
        "city": RNG.choice(["Fardis", "Karaj", "Tehran", "Other"], n, p=[0.40, 0.30, 0.20, 0.10]),
        "registration_date": registration.date,
        "insurance_type": RNG.choice(["self_pay", "basic", "supplementary"], n, p=[0.45, 0.35, 0.20]),
        "referral_source": RNG.choice(["patient_referral", "search", "social_media", "walk_in", "other"], n, p=[0.36, 0.24, 0.17, 0.13, 0.10]),
    })


def generate_dentists() -> pd.DataFrame:
    return pd.DataFrame([
        {"dentist_id": 1, "dentist_role": "general_dentist", "start_date": "2023-01-01", "scheduled_hours_weekly": 18},
        {"dentist_id": 2, "dentist_role": "general_dentist", "start_date": "2023-04-01", "scheduled_hours_weekly": 24},
        {"dentist_id": 3, "dentist_role": "visiting_specialist", "start_date": "2023-07-01", "scheduled_hours_weekly": 8},
    ])


def generate_appointments(n: int, patient_count: int) -> pd.DataFrame:
    dates = pd.to_datetime("2024-01-01") + pd.to_timedelta(RNG.integers(0, 730, n), unit="D")
    hours = RNG.choice([9, 10, 11, 12, 14, 15, 16, 17, 18], n)
    minutes = RNG.choice([0, 30], n)
    dt = dates + pd.to_timedelta(hours, unit="h") + pd.to_timedelta(minutes, unit="m")
    appointment_type = RNG.choice(
        ["examination", "restorative", "endodontic", "surgery", "hygiene", "prosthetic"],
        n,
        p=[0.26, 0.27, 0.12, 0.09, 0.16, 0.10],
    )
    duration_map = {"examination": 30, "restorative": 60, "endodontic": 90, "surgery": 75, "hygiene": 45, "prosthetic": 60}
    planned_duration = np.array([duration_map[x] for x in appointment_type])
    reminder = RNG.choice([True, False], n, p=[0.78, 0.22])
    lead_days = RNG.integers(1, 45, n)
    booked = (dt - pd.to_timedelta(lead_days, unit="D")).normalize()

    # Create plausible status probabilities. These are synthetic assumptions, not clinical estimates.
    base_no_show = 0.11 + (~reminder) * 0.07 + (lead_days > 21) * 0.04
    no_show = RNG.random(n) < np.clip(base_no_show, 0, 0.35)
    cancelled = (~no_show) & (RNG.random(n) < 0.12)
    rescheduled = (~no_show) & (~cancelled) & (RNG.random(n) < 0.05)
    status = np.where(no_show, "no_show", np.where(cancelled, "cancelled", np.where(rescheduled, "rescheduled", "completed")))
    wait_time = np.where(status == "completed", np.maximum(0, RNG.normal(14, 10, n)).round().astype(int), np.nan)

    return pd.DataFrame({
        "appointment_id": np.arange(1, n + 1),
        "patient_id": RNG.integers(1, patient_count + 1, n),
        "dentist_id": RNG.choice([1, 2, 3], n, p=[0.42, 0.46, 0.12]),
        "appointment_datetime": dt,
        "booked_date": booked.date,
        "appointment_type": appointment_type,
        "planned_duration_min": planned_duration,
        "status": status,
        "reminder_sent": reminder,
        "wait_time_min": wait_time,
    }).sort_values("appointment_datetime").reset_index(drop=True)


def generate_procedures(appointments: pd.DataFrame) -> pd.DataFrame:
    completed = appointments.loc[appointments["status"] == "completed"].copy()
    groups = completed["appointment_type"].replace({"examination": "diagnostic", "hygiene": "preventive"})
    fee_ranges = {
        "diagnostic": (10, 35), "preventive": (25, 65), "restorative": (45, 150),
        "endodontic": (100, 280), "surgery": (80, 300), "prosthetic": (120, 550),
    }
    fees = []
    costs = []
    actual = []
    for group, planned in zip(groups, completed["planned_duration_min"]):
        low, high = fee_ranges[group]
        fee = float(np.round(RNG.uniform(low, high), 2))
        fees.append(fee)
        costs.append(float(np.round(fee * RNG.uniform(0.12, 0.38), 2)))
        actual.append(int(max(15, RNG.normal(planned, planned * 0.18))))
    return pd.DataFrame({
        "procedure_id": np.arange(1, len(completed) + 1),
        "appointment_id": completed["appointment_id"].to_numpy(),
        "procedure_code": [f"P{1000+i}" for i in range(len(completed))],
        "procedure_group": groups.to_numpy(),
        "actual_duration_min": actual,
        "fee_amount": fees,
        "direct_cost": costs,
    })


def generate_treatment_plans(patients: pd.DataFrame) -> pd.DataFrame:
    n = int(len(patients) * 0.72)
    patient_ids = RNG.choice(patients["patient_id"], n, replace=False)
    proposed = pd.to_datetime("2024-01-01") + pd.to_timedelta(RNG.integers(0, 730, n), unit="D")
    values = np.round(RNG.lognormal(mean=5.0, sigma=0.65, size=n), 2)
    status = RNG.choice(["fully_accepted", "partially_accepted", "declined", "pending"], n, p=[0.43, 0.27, 0.20, 0.10])
    accepted_ratio = np.select(
        [status == "fully_accepted", status == "partially_accepted", status == "declined", status == "pending"],
        [1.0, RNG.uniform(0.25, 0.75, n), 0.0, 0.0],
    )
    return pd.DataFrame({
        "plan_id": np.arange(1, n + 1),
        "patient_id": patient_ids,
        "proposed_date": proposed.date,
        "total_value": values,
        "accepted_value": np.round(values * accepted_ratio, 2),
        "plan_status": status,
    })


def generate_payments(appointments: pd.DataFrame, procedures: pd.DataFrame) -> pd.DataFrame:
    merged = procedures.merge(appointments[["appointment_id", "patient_id", "appointment_datetime"]], on="appointment_id", how="left")
    collection_ratio = RNG.uniform(0.82, 1.0, len(merged))
    payment_date = pd.to_datetime(merged["appointment_datetime"]).dt.normalize() + pd.to_timedelta(RNG.integers(0, 21, len(merged)), unit="D")
    return pd.DataFrame({
        "payment_id": np.arange(1, len(merged) + 1),
        "patient_id": merged["patient_id"],
        "appointment_id": merged["appointment_id"],
        "payment_date": payment_date.dt.date,
        "amount": np.round(merged["fee_amount"] * collection_ratio, 2),
        "payment_method": RNG.choice(["card", "cash", "transfer", "installment"], len(merged), p=[0.55, 0.12, 0.18, 0.15]),
    })


def validate(patients, dentists, appointments, procedures, plans, payments) -> None:
    assert appointments["patient_id"].isin(patients["patient_id"]).all()
    assert appointments["dentist_id"].isin(dentists["dentist_id"]).all()
    assert procedures["appointment_id"].isin(appointments["appointment_id"]).all()
    assert plans["patient_id"].isin(patients["patient_id"]).all()
    assert payments["appointment_id"].isin(appointments["appointment_id"]).all()


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    patients = generate_patients(args.patients)
    dentists = generate_dentists()
    appointments = generate_appointments(args.appointments, args.patients)
    procedures = generate_procedures(appointments)
    plans = generate_treatment_plans(patients)
    payments = generate_payments(appointments, procedures)
    validate(patients, dentists, appointments, procedures, plans, payments)

    datasets = {
        "patients.csv": patients,
        "dentists.csv": dentists,
        "appointments.csv": appointments,
        "procedures.csv": procedures,
        "treatment_plans.csv": plans,
        "payments.csv": payments,
    }
    for name, df in datasets.items():
        df.to_csv(args.output / name, index=False)
        print(f"Wrote {name}: {len(df):,} rows")


if __name__ == "__main__":
    main()
