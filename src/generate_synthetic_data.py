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
    registration_days = RNG.integers(0, 365, n)
    registration_minutes = RNG.integers(8 * 60, 20 * 60, n)

    registered_at = (
        pd.Timestamp("2023-01-01")
        + pd.to_timedelta(registration_days, unit="D")
        + pd.to_timedelta(registration_minutes, unit="m")
    )

    return pd.DataFrame(
        {
            "patient_id": np.arange(1, n + 1),
            "birth_year": RNG.integers(1945, 2020, n),
            "sex": RNG.choice(
                ["female", "male", "other_unknown"],
                n,
                p=[0.53, 0.46, 0.01],
            ),
            "city_area": RNG.choice(
                [
                    "fardis",
                    "karaj",
                    "west_tehran",
                    "central_tehran",
                    "other",
                ],
                n,
                p=[0.35, 0.30, 0.15, 0.10, 0.10],
            ),
            "registered_at": registered_at,
            "insurance_type": RNG.choice(
                [
                    "self_pay",
                    "basic_insurance",
                    "supplementary_insurance",
                    "mixed",
                ],
                n,
                p=[0.38, 0.30, 0.12, 0.20],
            ),
            "referral_source": RNG.choice(
                [
                    "existing_patient_referral",
                    "dentist_referral",
                    "online_search",
                    "social_media",
                    "walk_in",
                    "advertising",
                    "other",
                ],
                n,
                p=[0.32, 0.12, 0.18, 0.16, 0.10, 0.07, 0.05],
            ),
            "preferred_contact_channel": RNG.choice(
                [
                    "phone_call",
                    "sms",
                    "messaging_application",
                    "email",
                    "other",
                ],
                n,
                p=[0.28, 0.20, 0.44, 0.05, 0.03],
            ),
            "patient_status": RNG.choice(
                ["active", "inactive", "archived"],
                n,
                p=[0.78, 0.20, 0.02],
            ),
        }
    )


def generate_dentists() -> pd.DataFrame:
    dentists = pd.DataFrame(
        [
            {
                "dentist_id": 1,
                "dentist_role": "general_dentist",
                "engagement_type": "employee",
                "start_date": "2023-01-01",
                "end_date": None,
                "scheduled_hours_weekly": 30,
                "active": True,
            },
            {
                "dentist_id": 2,
                "dentist_role": "general_dentist",
                "engagement_type": "contractor",
                "start_date": "2023-03-15",
                "end_date": None,
                "scheduled_hours_weekly": 24,
                "active": True,
            },
            {
                "dentist_id": 3,
                "dentist_role": "endodontist",
                "engagement_type": "visiting_specialist",
                "start_date": "2023-06-01",
                "end_date": None,
                "scheduled_hours_weekly": 8,
                "active": True,
            },
            {
                "dentist_id": 4,
                "dentist_role": "oral_surgeon",
                "engagement_type": "visiting_specialist",
                "start_date": "2023-07-01",
                "end_date": None,
                "scheduled_hours_weekly": 6,
                "active": True,
            },
            {
                "dentist_id": 5,
                "dentist_role": "orthodontist",
                "engagement_type": "visiting_specialist",
                "start_date": "2023-09-01",
                "end_date": None,
                "scheduled_hours_weekly": 8,
                "active": True,
            },
            {
                "dentist_id": 6,
                "dentist_role": "prosthodontist",
                "engagement_type": "contractor",
                "start_date": "2023-05-01",
                "end_date": None,
                "scheduled_hours_weekly": 12,
                "active": True,
            },
            {
                "dentist_id": 7,
                "dentist_role": "periodontist",
                "engagement_type": "visiting_specialist",
                "start_date": "2023-02-01",
                "end_date": "2024-08-31",
                "scheduled_hours_weekly": 6,
                "active": False,
            },
        ]
    )

    dentists["start_date"] = pd.to_datetime(
        dentists["start_date"]
    ).dt.date

    dentists["end_date"] = pd.to_datetime(
        dentists["end_date"]
    ).dt.date

    return dentists


def generate_appointments(
    n: int,
    patients: pd.DataFrame,
    dentists: pd.DataFrame,
) -> pd.DataFrame:
    # The synthetic clinic operates six days per week and is closed on Fridays.
    clinic_dates = pd.date_range(
        "2024-03-01",
        "2025-12-31",
        freq="D",
    )
    clinic_dates = clinic_dates[clinic_dates.dayofweek != 4]

    appointment_days = pd.to_datetime(
        RNG.choice(
            clinic_dates.to_numpy(),
            size=n,
            replace=True,
        )
    )

    appointment_hours = RNG.choice(
        [9, 10, 11, 12, 14, 15, 16, 17, 18],
        n,
        p=[
            0.08,
            0.12,
            0.13,
            0.10,
            0.11,
            0.13,
            0.13,
            0.12,
            0.08,
        ],
    )
    appointment_minutes = RNG.choice([0, 30], n)

    scheduled_start_at = (
        appointment_days
        + pd.to_timedelta(appointment_hours, unit="h")
        + pd.to_timedelta(appointment_minutes, unit="m")
    )

    lead_days = RNG.integers(1, 61, n)
    booking_minutes = RNG.integers(
        8 * 60,
        20 * 60,
        n,
    )

    booked_at = (
        (
            scheduled_start_at
            - pd.to_timedelta(lead_days, unit="D")
        ).normalize()
        + pd.to_timedelta(booking_minutes, unit="m")
    )

    patient_id = RNG.choice(
        patients["patient_id"].to_numpy(),
        size=n,
        replace=True,
    )

    dentist_start = pd.to_datetime(
        dentists["start_date"]
    )
    dentist_end = pd.to_datetime(
        dentists["end_date"]
    )
    dentist_weights = dentists[
        "scheduled_hours_weekly"
    ].to_numpy(dtype=float)

    dentist_id: list[int] = []

    for appointment_time in scheduled_start_at:
        eligible = (
            (dentist_start <= appointment_time)
            & (
                dentist_end.isna()
                | (dentist_end >= appointment_time)
            )
        )

        eligible_ids = dentists.loc[
            eligible,
            "dentist_id",
        ].to_numpy()

        eligible_weights = dentist_weights[
            eligible.to_numpy()
        ]
        eligible_weights = (
            eligible_weights
            / eligible_weights.sum()
        )

        dentist_id.append(
            int(
                RNG.choice(
                    eligible_ids,
                    p=eligible_weights,
                )
            )
        )

    visit_type = RNG.choice(
        [
            "new_patient_examination",
            "recall_examination",
            "consultation",
            "treatment",
            "emergency",
            "follow_up",
        ],
        n,
        p=[
            0.15,
            0.17,
            0.10,
            0.42,
            0.08,
            0.08,
        ],
    )

    duration_map = {
        "new_patient_examination": 45,
        "recall_examination": 30,
        "consultation": 30,
        "treatment": 60,
        "emergency": 45,
        "follow_up": 30,
    }

    planned_duration_min = np.array(
        [
            duration_map[value]
            for value in visit_type
        ],
        dtype=int,
    )

    booking_channel = RNG.choice(
        [
            "phone",
            "in_person",
            "online",
            "referral",
            "other",
        ],
        n,
        p=[
            0.46,
            0.18,
            0.20,
            0.12,
            0.04,
        ],
    )

    reminder_sent = RNG.choice(
        [True, False],
        n,
        p=[0.82, 0.18],
    )

    # These probabilities are synthetic assumptions.
    base_no_show = (
        0.07
        + (~reminder_sent) * 0.09
        + (lead_days > 30) * 0.04
    )

    no_show = (
        RNG.random(n)
        < np.clip(
            base_no_show,
            0.0,
            0.30,
        )
    )

    cancelled = (
        (~no_show)
        & (RNG.random(n) < 0.11)
    )

    rescheduled = (
        (~no_show)
        & (~cancelled)
        & (RNG.random(n) < 0.06)
    )

    status = np.where(
        no_show,
        "no_show",
        np.where(
            cancelled,
            "cancelled",
            np.where(
                rescheduled,
                "rescheduled",
                "completed",
            ),
        ),
    )

    empty_datetime = pd.Series(
        pd.NaT,
        index=np.arange(n),
        dtype="datetime64[ns]",
    )

    check_in_at = empty_datetime.copy()
    chair_start_at = empty_datetime.copy()
    chair_end_at = empty_datetime.copy()
    checkout_at = empty_datetime.copy()
    status_updated_at = empty_datetime.copy()

    status_change_reason = pd.Series(
        pd.NA,
        index=np.arange(n),
        dtype="string",
    )

    completed_mask = status == "completed"
    completed_count = int(
        completed_mask.sum()
    )

    arrival_offset_min = np.clip(
        np.rint(
            RNG.normal(
                -5,
                10,
                completed_count,
            )
        ).astype(int),
        -30,
        30,
    )

    waiting_min = np.clip(
        np.rint(
            RNG.gamma(
                2.0,
                6.0,
                completed_count,
            )
        ).astype(int),
        0,
        60,
    )

    completed_schedule = pd.Series(
        scheduled_start_at[completed_mask]
    ).reset_index(drop=True)

    completed_check_in = (
        completed_schedule
        + pd.to_timedelta(
            arrival_offset_min,
            unit="m",
        )
    )

    start_candidate = (
        completed_check_in
        + pd.to_timedelta(
            waiting_min,
            unit="m",
        )
    )

    earliest_start = (
        completed_schedule
        - pd.Timedelta(minutes=10)
    )

    completed_chair_start = (
        start_candidate.where(
            start_candidate >= earliest_start,
            earliest_start,
        )
    )

    duration_multiplier = RNG.lognormal(
        mean=0.0,
        sigma=0.18,
        size=completed_count,
    )

    completed_planned_duration = (
        planned_duration_min[completed_mask]
    )

    actual_duration_min = np.clip(
        np.rint(
            completed_planned_duration
            * duration_multiplier
        ).astype(int),
        15,
        180,
    )

    completed_chair_end = (
        completed_chair_start
        + pd.to_timedelta(
            actual_duration_min,
            unit="m",
        )
    )

    completed_checkout = (
        completed_chair_end
        + pd.to_timedelta(
            RNG.integers(
                5,
                21,
                completed_count,
            ),
            unit="m",
        )
    )

    completed_indices = np.flatnonzero(
        completed_mask
    )

    check_in_at.iloc[
        completed_indices
    ] = completed_check_in.to_numpy()

    chair_start_at.iloc[
        completed_indices
    ] = completed_chair_start.to_numpy()

    chair_end_at.iloc[
        completed_indices
    ] = completed_chair_end.to_numpy()

    checkout_at.iloc[
        completed_indices
    ] = completed_checkout.to_numpy()

    status_updated_at.iloc[
        completed_indices
    ] = completed_checkout.to_numpy()

    no_show_indices = np.flatnonzero(
        no_show
    )

    status_updated_at.iloc[
        no_show_indices
    ] = (
        scheduled_start_at[no_show]
        + pd.Timedelta(minutes=15)
    ).to_numpy()

    changed_mask = cancelled | rescheduled
    changed_count = int(
        changed_mask.sum()
    )

    notice_hours = RNG.integers(
        2,
        14 * 24 + 1,
        changed_count,
    )

    changed_schedule = pd.Series(
        scheduled_start_at[changed_mask]
    ).reset_index(drop=True)

    changed_booked = pd.Series(
        booked_at[changed_mask]
    ).reset_index(drop=True)

    changed_at = (
        changed_schedule
        - pd.to_timedelta(
            notice_hours,
            unit="h",
        )
    )

    earliest_change = (
        changed_booked
        + pd.Timedelta(minutes=15)
    )

    changed_at = changed_at.where(
        changed_at >= earliest_change,
        earliest_change,
    )

    changed_indices = np.flatnonzero(
        changed_mask
    )

    status_updated_at.iloc[
        changed_indices
    ] = changed_at.to_numpy()

    status_change_reason.iloc[
        changed_indices
    ] = RNG.choice(
        [
            "patient_related",
            "clinic_related",
            "financial",
            "illness",
            "scheduling_conflict",
            "other",
        ],
        changed_count,
        p=[
            0.30,
            0.08,
            0.12,
            0.16,
            0.28,
            0.06,
        ],
    )

    appointments = pd.DataFrame(
        {
            "patient_id": patient_id,
            "dentist_id": dentist_id,
            "booked_at": booked_at,
            "scheduled_start_at": (
                scheduled_start_at
            ),
            "planned_duration_min": (
                planned_duration_min
            ),
            "visit_type": visit_type,
            "booking_channel": booking_channel,
            "status": status,
            "status_updated_at": (
                status_updated_at
            ),
            "reminder_sent": reminder_sent,
            "check_in_at": check_in_at,
            "chair_start_at": chair_start_at,
            "chair_end_at": chair_end_at,
            "checkout_at": checkout_at,
            "status_change_reason": (
                status_change_reason
            ),
        }
    )

    appointments = (
        appointments.sort_values(
            "scheduled_start_at"
        )
        .reset_index(drop=True)
    )

    appointments.insert(
        0,
        "appointment_id",
        np.arange(1, n + 1),
    )

    appointments[
        "rescheduled_from_appointment_id"
    ] = pd.Series(
        pd.NA,
        index=appointments.index,
        dtype="Int64",
    )

    rescheduled_indices = appointments.index[
        appointments["status"]
        == "rescheduled"
    ].to_numpy()

    used_replacements: set[int] = set()

    for original_index in rescheduled_indices:
        future_candidates = appointments.index[
            (
                appointments.index
                > original_index
            )
            & (
                appointments["status"]
                == "completed"
            )
            & (
                appointments[
                    "scheduled_start_at"
                ]
                > appointments.at[
                    original_index,
                    "scheduled_start_at",
                ]
                + pd.Timedelta(days=1)
            )
        ].difference(
            list(used_replacements)
        )

        if len(future_candidates) == 0:
            continue

        replacement_index = int(
            RNG.choice(
                future_candidates.to_numpy()
            )
        )

        used_replacements.add(
            replacement_index
        )

        appointments.at[
            replacement_index,
            "patient_id",
        ] = appointments.at[
            original_index,
            "patient_id",
        ]

        appointments.at[
            replacement_index,
            "booked_at",
        ] = appointments.at[
            original_index,
            "status_updated_at",
        ]

        appointments.at[
            replacement_index,
            "rescheduled_from_appointment_id",
        ] = appointments.at[
            original_index,
            "appointment_id",
        ]

    return appointments

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
    appointments = generate_appointments(
        args.appointments,
        patients,
        dentists,
    )
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
