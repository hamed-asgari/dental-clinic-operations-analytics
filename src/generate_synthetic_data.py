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


def generate_procedure_catalog() -> pd.DataFrame:
    records = [
        (
            "D001",
            "Comprehensive examination",
            "diagnostic",
            45,
            35.00,
            4.00,
            True,
        ),
        (
            "D002",
            "Recall examination",
            "diagnostic",
            30,
            25.00,
            3.00,
            True,
        ),
        (
            "D003",
            "Emergency examination",
            "diagnostic",
            30,
            45.00,
            5.00,
            True,
        ),
        (
            "D004",
            "Periapical radiograph",
            "diagnostic",
            10,
            12.00,
            2.00,
            True,
        ),
        (
            "PV001",
            "Dental prophylaxis",
            "preventive",
            45,
            55.00,
            12.00,
            True,
        ),
        (
            "PV002",
            "Fluoride application",
            "preventive",
            15,
            25.00,
            5.00,
            True,
        ),
        (
            "R001",
            "Composite restoration one surface",
            "restorative",
            45,
            85.00,
            20.00,
            True,
        ),
        (
            "R002",
            "Composite restoration multiple surfaces",
            "restorative",
            60,
            125.00,
            32.00,
            True,
        ),
        (
            "R003",
            "Core build-up",
            "restorative",
            45,
            110.00,
            28.00,
            True,
        ),
        (
            "R004",
            "Amalgam restoration",
            "restorative",
            45,
            70.00,
            18.00,
            False,
        ),
        (
            "E001",
            "Root canal treatment anterior tooth",
            "endodontic",
            75,
            220.00,
            48.00,
            True,
        ),
        (
            "E002",
            "Root canal treatment premolar",
            "endodontic",
            90,
            280.00,
            62.00,
            True,
        ),
        (
            "E003",
            "Root canal treatment molar",
            "endodontic",
            120,
            380.00,
            90.00,
            True,
        ),
        (
            "PER001",
            "Scaling and root planing one quadrant",
            "periodontal",
            60,
            140.00,
            40.00,
            True,
        ),
        (
            "PER002",
            "Periodontal maintenance",
            "periodontal",
            45,
            75.00,
            20.00,
            True,
        ),
        (
            "S001",
            "Simple extraction",
            "surgical",
            45,
            120.00,
            25.00,
            True,
        ),
        (
            "S002",
            "Surgical extraction",
            "surgical",
            75,
            250.00,
            70.00,
            True,
        ),
        (
            "PR001",
            "Full ceramic crown",
            "prosthodontic",
            90,
            520.00,
            210.00,
            True,
        ),
        (
            "PR002",
            "Removable partial denture",
            "prosthodontic",
            120,
            780.00,
            330.00,
            True,
        ),
        (
            "PR003",
            "Complete denture",
            "prosthodontic",
            180,
            1100.00,
            480.00,
            True,
        ),
        (
            "O001",
            "Orthodontic consultation",
            "orthodontic",
            45,
            50.00,
            5.00,
            True,
        ),
        (
            "O002",
            "Fixed appliance adjustment",
            "orthodontic",
            30,
            85.00,
            15.00,
            True,
        ),
        (
            "PD001",
            "Pediatric composite restoration",
            "pediatric",
            45,
            70.00,
            18.00,
            True,
        ),
        (
            "PD002",
            "Pulpotomy of primary tooth",
            "pediatric",
            60,
            150.00,
            35.00,
            True,
        ),
    ]

    columns = [
        "procedure_code",
        "procedure_name",
        "procedure_group",
        "default_planned_duration_min",
        "standard_fee_amount",
        "standard_direct_cost",
        "active",
    ]

    return pd.DataFrame(
        records,
        columns=columns,
    )


def generate_appointment_procedures(
        appointments: pd.DataFrame,
        dentists: pd.DataFrame,
        procedure_catalog: pd.DataFrame,
) -> pd.DataFrame:
    completed_appointments = appointments.loc[
        appointments["status"] == "completed"
        ].copy()

    dentist_role_by_id = dentists.set_index(
        "dentist_id"
    )["dentist_role"].to_dict()

    catalog_by_code = procedure_catalog.set_index(
        "procedure_code"
    )

    active_codes = set(
        procedure_catalog.loc[
            procedure_catalog["active"],
            "procedure_code",
        ]
    )

    adult_tooth_codes = [
        f"{quadrant}{tooth}"
        for quadrant in [1, 2, 3, 4]
        for tooth in range(1, 9)
    ]

    tooth_specific_codes = {
        "D004",
        "R001",
        "R002",
        "R003",
        "E001",
        "E002",
        "E003",
        "S001",
        "S002",
        "PR001",
    }

    treatment_codes_by_role = {
        "general_dentist": [
            "PV001",
            "PV002",
            "R001",
            "R002",
            "R003",
            "E001",
            "E002",
            "S001",
        ],
        "endodontist": [
            "E001",
            "E002",
            "E003",
        ],
        "oral_surgeon": [
            "S001",
            "S002",
        ],
        "orthodontist": [
            "O002",
        ],
        "prosthodontist": [
            "R003",
            "PR001",
            "PR002",
            "PR003",
        ],
        "periodontist": [
            "PER001",
            "PER002",
        ],
    }

    emergency_codes_by_role = {
        "general_dentist": [
            "R001",
            "R002",
            "E001",
            "E002",
            "S001",
        ],
        "endodontist": [
            "E001",
            "E002",
            "E003",
        ],
        "oral_surgeon": [
            "S001",
            "S002",
        ],
        "orthodontist": [],
        "prosthodontist": [
            "R003",
            "PR001",
        ],
        "periodontist": [
            "PER001",
            "S001",
        ],
    }

    follow_up_code_by_role = {
        "general_dentist": "D002",
        "endodontist": "D002",
        "oral_surgeon": "D002",
        "orthodontist": "O002",
        "prosthodontist": "D002",
        "periodontist": "PER002",
    }

    rows: list[dict[str, object]] = []
    appointment_procedure_id = 1

    for appointment in completed_appointments.itertuples(
            index=False
    ):
        dentist_role = dentist_role_by_id[
            int(appointment.dentist_id)
        ]

        visit_type = appointment.visit_type
        selected_codes: list[str] = []

        if visit_type == "new_patient_examination":
            selected_codes.append("D001")

            if RNG.random() < 0.35:
                selected_codes.append("D004")

        elif visit_type == "recall_examination":
            selected_codes.append("D002")

            if RNG.random() < 0.45:
                selected_codes.append("PV001")

            if RNG.random() < 0.20:
                selected_codes.append("D004")

        elif visit_type == "consultation":
            if dentist_role == "orthodontist":
                selected_codes.append("O001")
            else:
                selected_codes.append("D001")

            if RNG.random() < 0.20:
                selected_codes.append("D004")

        elif visit_type == "follow_up":
            selected_codes.append(
                follow_up_code_by_role.get(
                    dentist_role,
                    "D002",
                )
            )

        elif visit_type == "emergency":
            selected_codes.append("D003")

            if RNG.random() < 0.50:
                selected_codes.append("D004")

            emergency_candidates = (
                emergency_codes_by_role.get(
                    dentist_role,
                    [],
                )
            )

            if (
                    emergency_candidates
                    and RNG.random() < 0.60
            ):
                selected_codes.append(
                    str(
                        RNG.choice(
                            emergency_candidates
                        )
                    )
                )

        elif visit_type == "treatment":
            treatment_candidates = (
                treatment_codes_by_role.get(
                    dentist_role,
                    treatment_codes_by_role[
                        "general_dentist"
                    ],
                )
            )

            procedure_count = int(
                RNG.choice(
                    [1, 2],
                    p=[0.82, 0.18],
                )
            )

            procedure_count = min(
                procedure_count,
                len(treatment_candidates),
            )

            selected_codes.extend(
                [
                    str(code)
                    for code in RNG.choice(
                    treatment_candidates,
                    size=procedure_count,
                    replace=False,
                )
                ]
            )

            if RNG.random() < 0.18:
                selected_codes.insert(
                    0,
                    "D004",
                )

        selected_codes = list(
            dict.fromkeys(selected_codes)
        )

        for procedure_code in selected_codes:
            if procedure_code not in active_codes:
                raise ValueError(
                    "Inactive or unknown procedure "
                    f"code selected: {procedure_code}"
                )

            catalog_record = catalog_by_code.loc[
                procedure_code
            ]

            completion_status = str(
                RNG.choice(
                    [
                        "completed",
                        "partially_completed",
                        "discontinued",
                    ],
                    p=[0.96, 0.03, 0.01],
                )
            )

            fee_factor_by_status = {
                "completed": 1.00,
                "partially_completed": 0.65,
                "discontinued": 0.25,
            }

            cost_factor_by_status = {
                "completed": 1.00,
                "partially_completed": 0.70,
                "discontinued": 0.25,
            }

            fee_amount = float(
                np.round(
                    catalog_record[
                        "standard_fee_amount"
                    ]
                    * RNG.uniform(0.92, 1.12)
                    * fee_factor_by_status[
                        completion_status
                    ],
                    2,
                )
            )

            discount_rate = float(
                RNG.choice(
                    [0.00, 0.05, 0.10, 0.15],
                    p=[0.70, 0.15, 0.10, 0.05],
                )
            )

            discount_amount = float(
                np.round(
                    fee_amount * discount_rate,
                    2,
                )
            )

            direct_cost = float(
                np.round(
                    catalog_record[
                        "standard_direct_cost"
                    ]
                    * RNG.uniform(0.90, 1.15)
                    * cost_factor_by_status[
                        completion_status
                    ],
                    2,
                )
            )

            if procedure_code in tooth_specific_codes:
                tooth_code: object = str(
                    RNG.choice(adult_tooth_codes)
                )
            else:
                tooth_code = pd.NA

            rows.append(
                {
                    "appointment_procedure_id": (
                        appointment_procedure_id
                    ),
                    "appointment_id": int(
                        appointment.appointment_id
                    ),
                    "plan_item_id": pd.NA,
                    "procedure_code": procedure_code,
                    "tooth_code": tooth_code,
                    "quantity": 1,
                    "completion_status": (
                        completion_status
                    ),
                    "fee_amount": fee_amount,
                    "discount_amount": (
                        discount_amount
                    ),
                    "direct_cost": direct_cost,
                }
            )

            appointment_procedure_id += 1

    columns = [
        "appointment_procedure_id",
        "appointment_id",
        "plan_item_id",
        "procedure_code",
        "tooth_code",
        "quantity",
        "completion_status",
        "fee_amount",
        "discount_amount",
        "direct_cost",
    ]

    appointment_procedures = pd.DataFrame(
        rows,
        columns=columns,
    )

    appointment_procedures[
        "plan_item_id"
    ] = appointment_procedures[
        "plan_item_id"
    ].astype("Int64")

    return appointment_procedures


def generate_treatment_plans(
        appointments: pd.DataFrame,
        dentists: pd.DataFrame,
        procedure_catalog: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    eligible_sources = appointments.loc[
        appointments["status"].eq("completed")
        & appointments["visit_type"].isin(
            [
                "new_patient_examination",
                "recall_examination",
                "consultation",
                "emergency",
            ]
        )
        ].copy()

    selected_mask = (
            RNG.random(len(eligible_sources))
            < 0.58
    )

    selected_sources = eligible_sources.loc[
        selected_mask
    ].copy()

    if selected_sources.empty:
        selected_sources = eligible_sources.head(
            1
        ).copy()

    dentist_role_by_id = dentists.set_index(
        "dentist_id"
    )["dentist_role"].to_dict()

    catalog_by_code = procedure_catalog.set_index(
        "procedure_code"
    )

    treatment_codes_by_role = {
        "general_dentist": [
            "PV001",
            "R001",
            "R002",
            "R003",
            "E001",
            "E002",
            "S001",
            "PR001",
        ],
        "endodontist": [
            "E001",
            "E002",
            "E003",
        ],
        "oral_surgeon": [
            "S001",
            "S002",
        ],
        "orthodontist": [
            "O002",
        ],
        "prosthodontist": [
            "R003",
            "PR001",
            "PR002",
            "PR003",
        ],
        "periodontist": [
            "PER001",
            "PER002",
        ],
    }

    adult_tooth_codes = [
        f"{quadrant}{tooth}"
        for quadrant in [1, 2, 3, 4]
        for tooth in range(1, 9)
    ]

    tooth_specific_codes = {
        "R001",
        "R002",
        "R003",
        "E001",
        "E002",
        "E003",
        "S001",
        "S002",
        "PR001",
    }

    plan_rows: list[dict[str, object]] = []
    item_rows: list[dict[str, object]] = []

    plan_id = 1
    plan_item_id = 1

    for source in selected_sources.itertuples(
            index=False
    ):
        dentist_id = int(source.dentist_id)
        dentist_role = dentist_role_by_id[
            dentist_id
        ]

        candidate_codes = (
            treatment_codes_by_role.get(
                dentist_role,
                treatment_codes_by_role[
                    "general_dentist"
                ],
            )
        )

        maximum_items = min(
            4,
            len(candidate_codes),
        )

        item_count = int(
            RNG.choice(
                np.arange(
                    1,
                    maximum_items + 1,
                ),
                p=(
                    [1.0]
                    if maximum_items == 1
                    else (
                        [0.55, 0.45]
                        if maximum_items == 2
                        else (
                            [0.40, 0.35, 0.25]
                            if maximum_items == 3
                            else [
                                0.32,
                                0.30,
                                0.23,
                                0.15,
                            ]
                        )
                    )
                ),
            )
        )

        selected_codes = [
            str(code)
            for code in RNG.choice(
                candidate_codes,
                size=item_count,
                replace=False,
            )
        ]

        proposed_at = (
                pd.Timestamp(source.chair_end_at)
                + pd.to_timedelta(
            int(
                RNG.integers(
                    5,
                    46,
                )
            ),
            unit="m",
        )
        )

        valid_until = (
                proposed_at.normalize()
                + pd.to_timedelta(
            int(
                RNG.integers(
                    30,
                    91,
                )
            ),
            unit="D",
        )
        )

        plan_status = str(
            RNG.choice(
                [
                    "presented",
                    "partially_accepted",
                    "fully_accepted",
                    "declined",
                    "expired",
                ],
                p=[
                    0.14,
                    0.30,
                    0.38,
                    0.13,
                    0.05,
                ],
            )
        )

        if (
                plan_status
                == "partially_accepted"
                and item_count == 1
        ):
            plan_status = str(
                RNG.choice(
                    [
                        "fully_accepted",
                        "declined",
                    ],
                    p=[0.70, 0.30],
                )
            )

        plan_rows.append(
            {
                "plan_id": plan_id,
                "patient_id": int(
                    source.patient_id
                ),
                "proposed_by_dentist_id": (
                    dentist_id
                ),
                "source_appointment_id": int(
                    source.appointment_id
                ),
                "proposed_at": proposed_at,
                "plan_status": plan_status,
                "valid_until": (
                    valid_until.date()
                ),
            }
        )

        if plan_status == "fully_accepted":
            decisions = [
                            "accepted"
                        ] * item_count

        elif plan_status == "declined":
            decisions = [
                            "declined"
                        ] * item_count

        elif plan_status in {
            "presented",
            "expired",
        }:
            decisions = [
                            "pending"
                        ] * item_count

        else:
            accepted_count = int(
                RNG.integers(
                    1,
                    item_count,
                )
            )

            decisions = (
                    ["accepted"] * accepted_count
                    + [
                        str(
                            RNG.choice(
                                [
                                    "declined",
                                    "deferred",
                                ],
                                p=[0.65, 0.35],
                            )
                        )
                        for _ in range(
                    item_count
                    - accepted_count
                )
                    ]
            )

            RNG.shuffle(decisions)

        for sequence_order, (
                procedure_code,
                decision_status,
        ) in enumerate(
            zip(
                selected_codes,
                decisions,
            ),
            start=1,
        ):
            catalog_record = (
                catalog_by_code.loc[
                    procedure_code
                ]
            )

            procedure_group = str(
                catalog_record[
                    "procedure_group"
                ]
            )

            if procedure_group in {
                "endodontic",
                "surgical",
            }:
                priority_level = str(
                    RNG.choice(
                        [
                            "urgent",
                            "short_term",
                            "elective",
                        ],
                        p=[0.35, 0.50, 0.15],
                    )
                )
            elif procedure_group in {
                "preventive",
                "periodontal",
            }:
                priority_level = str(
                    RNG.choice(
                        [
                            "short_term",
                            "elective",
                            "maintenance",
                        ],
                        p=[0.35, 0.35, 0.30],
                    )
                )
            else:
                priority_level = str(
                    RNG.choice(
                        [
                            "short_term",
                            "elective",
                            "maintenance",
                        ],
                        p=[0.35, 0.55, 0.10],
                    )
                )

            proposed_quantity = 1

            if procedure_code == "PER001":
                proposed_quantity = int(
                    RNG.integers(
                        1,
                        5,
                    )
                )

            proposed_fee_amount = float(
                np.round(
                    catalog_record[
                        "standard_fee_amount"
                    ]
                    * proposed_quantity
                    * RNG.uniform(
                        0.95,
                        1.15,
                    ),
                    2,
                )
            )

            discount_rate = float(
                RNG.choice(
                    [
                        0.00,
                        0.05,
                        0.10,
                        0.15,
                    ],
                    p=[
                        0.68,
                        0.17,
                        0.10,
                        0.05,
                    ],
                )
            )

            proposed_discount_amount = float(
                np.round(
                    proposed_fee_amount
                    * discount_rate,
                    2,
                )
            )

            if (
                    procedure_code
                    in tooth_specific_codes
            ):
                tooth_code: object = str(
                    RNG.choice(
                        adult_tooth_codes
                    )
                )
            else:
                tooth_code = pd.NA

            if decision_status == "pending":
                decision_at: object = pd.NaT
            else:
                maximum_decision_days = max(
                    1,
                    (
                            pd.Timestamp(
                                valid_until
                            )
                            - proposed_at.normalize()
                    ).days,
                )

                decision_days = int(
                    RNG.integers(
                        0,
                        min(
                            maximum_decision_days,
                            30,
                        )
                        + 1,
                    )
                )

                decision_minutes = int(
                    RNG.integers(
                        9 * 60,
                        19 * 60,
                    )
                )

                decision_at = (
                        proposed_at.normalize()
                        + pd.to_timedelta(
                    decision_days,
                    unit="D",
                )
                        + pd.to_timedelta(
                    decision_minutes,
                    unit="m",
                )
                )

                if decision_at < proposed_at:
                    decision_at = (
                            proposed_at
                            + pd.Timedelta(
                        minutes=30
                    )
                    )

            item_rows.append(
                {
                    "plan_item_id": (
                        plan_item_id
                    ),
                    "plan_id": plan_id,
                    "procedure_code": (
                        procedure_code
                    ),
                    "tooth_code": tooth_code,
                    "sequence_order": (
                        sequence_order
                    ),
                    "priority_level": (
                        priority_level
                    ),
                    "proposed_quantity": (
                        proposed_quantity
                    ),
                    "proposed_fee_amount": (
                        proposed_fee_amount
                    ),
                    "proposed_discount_amount": (
                        proposed_discount_amount
                    ),
                    "decision_status": (
                        decision_status
                    ),
                    "decision_at": decision_at,
                }
            )

            plan_item_id += 1

        plan_id += 1

    treatment_plans = pd.DataFrame(
        plan_rows
    )

    treatment_plan_items = pd.DataFrame(
        item_rows
    )

    return (
        treatment_plans,
        treatment_plan_items,
    )

def link_accepted_plan_items_to_procedures(
    appointments: pd.DataFrame,
    appointment_procedures: pd.DataFrame,
    treatment_plans: pd.DataFrame,
    treatment_plan_items: pd.DataFrame,
) -> pd.DataFrame:
    linked_procedures = (
        appointment_procedures.copy()
    )

    procedure_context = linked_procedures.merge(
        appointments[
            [
                "appointment_id",
                "patient_id",
                "scheduled_start_at",
            ]
        ],
        on="appointment_id",
        how="left",
        validate="many_to_one",
    )

    accepted_items = (
        treatment_plan_items.loc[
            treatment_plan_items[
                "decision_status"
            ].eq("accepted")
        ]
        .merge(
            treatment_plans[
                [
                    "plan_id",
                    "patient_id",
                ]
            ],
            on="plan_id",
            how="left",
            validate="many_to_one",
        )
        .sort_values(
            [
                "decision_at",
                "plan_item_id",
            ]
        )
    )

    used_procedure_ids = set(
        linked_procedures.loc[
            linked_procedures[
                "plan_item_id"
            ].notna(),
            "appointment_procedure_id",
        ].astype(int)
    )

    for item in accepted_items.itertuples(
        index=False
    ):
        decision_at = pd.Timestamp(
            item.decision_at
        )

        candidates = procedure_context.loc[
            procedure_context[
                "patient_id"
            ].eq(int(item.patient_id))
            & procedure_context[
                "procedure_code"
            ].eq(item.procedure_code)
            & procedure_context[
                "completion_status"
            ].eq("completed")
            & procedure_context[
                "scheduled_start_at"
            ].gt(decision_at)
            & ~procedure_context[
                "appointment_procedure_id"
            ].isin(used_procedure_ids)
        ].sort_values(
            "scheduled_start_at"
        )

        if candidates.empty:
            continue

        planned_tooth_code = (
            item.tooth_code
        )

        if pd.notna(planned_tooth_code):
            exact_tooth_candidates = (
                candidates.loc[
                    candidates[
                        "tooth_code"
                    ].eq(
                        str(
                            planned_tooth_code
                        )
                    )
                ]
            )

            if not exact_tooth_candidates.empty:
                candidates = (
                    exact_tooth_candidates
                )

        selected = candidates.iloc[0]

        selected_procedure_id = int(
            selected[
                "appointment_procedure_id"
            ]
        )

        selected_mask = linked_procedures[
            "appointment_procedure_id"
        ].eq(selected_procedure_id)

        linked_procedures.loc[
            selected_mask,
            "plan_item_id",
        ] = int(item.plan_item_id)

        if pd.notna(planned_tooth_code):
            linked_procedures.loc[
                selected_mask,
                "tooth_code",
            ] = str(planned_tooth_code)

        used_procedure_ids.add(
            selected_procedure_id
        )

    linked_procedures[
        "plan_item_id"
    ] = linked_procedures[
        "plan_item_id"
    ].astype("Int64")

    return linked_procedures

def generate_payments(
        appointments: pd.DataFrame,
        appointment_procedures: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    procedure_finance = appointment_procedures.merge(
        appointments[
            [
                "appointment_id",
                "patient_id",
                "scheduled_start_at",
                "chair_end_at",
            ]
        ],
        on="appointment_id",
        how="left",
        validate="many_to_one",
    ).copy()

    procedure_finance["net_procedure_amount"] = (
            procedure_finance["fee_amount"]
            - procedure_finance["discount_amount"]
    ).round(2)

    payment_rows: list[dict[str, object]] = []
    allocation_rows: list[dict[str, object]] = []

    payment_id = 1
    allocation_id = 1

    for _, group in procedure_finance.groupby(
            "appointment_id",
            sort=True,
    ):
        patient_id = int(
            group["patient_id"].iloc[0]
        )

        scheduled_start_at = pd.Timestamp(
            group["scheduled_start_at"].iloc[0]
        )

        chair_end_at = pd.Timestamp(
            group["chair_end_at"].iloc[0]
        )

        balances = {
            int(row.appointment_procedure_id): float(
                row.net_procedure_amount
            )
            for row in group.itertuples(
                index=False
            )
        }

        total_due = float(
            np.round(
                sum(balances.values()),
                2,
            )
        )

        arrangement = str(
            RNG.choice(
                [
                    "full_payment",
                    "partial_payment",
                    "installment",
                ],
                p=[0.58, 0.24, 0.18],
            )
        )

        if arrangement == "full_payment":
            collection_ratio = float(
                RNG.uniform(0.98, 1.00)
            )
            transaction_count = 1

        elif arrangement == "partial_payment":
            collection_ratio = float(
                RNG.uniform(0.55, 0.90)
            )
            transaction_count = 1

        else:
            collection_ratio = float(
                RNG.uniform(0.82, 1.00)
            )
            transaction_count = int(
                RNG.choice(
                    [2, 3],
                    p=[0.72, 0.28],
                )
            )

        collected_target = float(
            np.round(
                total_due * collection_ratio,
                2,
            )
        )

        if transaction_count == 1:
            transaction_amounts = [
                collected_target
            ]

        else:
            split_weights = RNG.dirichlet(
                np.ones(transaction_count)
            )

            transaction_amounts = list(
                np.round(
                    collected_target
                    * split_weights,
                    2,
                )
            )

            rounding_difference = float(
                np.round(
                    collected_target
                    - sum(transaction_amounts),
                    2,
                )
            )

            transaction_amounts[-1] = float(
                np.round(
                    transaction_amounts[-1]
                    + rounding_difference,
                    2,
                )
            )

        for transaction_number, amount in enumerate(
                transaction_amounts,
                start=1,
        ):
            if amount <= 0:
                continue

            is_deposit = (
                    transaction_number == 1
                    and arrangement == "installment"
                    and RNG.random() < 0.40
            )

            transaction_type = (
                "deposit"
                if is_deposit
                else "payment"
            )

            if is_deposit:
                received_at = (
                        scheduled_start_at
                        - pd.to_timedelta(
                    int(
                        RNG.integers(
                            1,
                            15,
                        )
                    ),
                    unit="D",
                )
                        + pd.to_timedelta(
                    int(
                        RNG.integers(
                            -120,
                            121,
                        )
                    ),
                    unit="m",
                )
                )

            else:
                minimum_days = (
                    0
                    if transaction_number == 1
                    else 7
                         * (transaction_number - 1)
                )

                maximum_days = (
                    7
                    if transaction_number == 1
                    else minimum_days + 21
                )

                received_at = (
                        chair_end_at
                        + pd.to_timedelta(
                    int(
                        RNG.integers(
                            minimum_days,
                            maximum_days + 1,
                        )
                    ),
                    unit="D",
                )
                        + pd.to_timedelta(
                    int(
                        RNG.integers(
                            5,
                            241,
                        )
                    ),
                    unit="m",
                )
                )

            payment_rows.append(
                {
                    "payment_id": payment_id,
                    "patient_id": patient_id,
                    "received_at": received_at,
                    "transaction_type": (
                        transaction_type
                    ),
                    "payment_arrangement": (
                        arrangement
                    ),
                    "payment_method": str(
                        RNG.choice(
                            [
                                "cash",
                                "card",
                                "bank_transfer",
                                "online_payment",
                                "other",
                            ],
                            p=[
                                0.10,
                                0.55,
                                0.20,
                                0.12,
                                0.03,
                            ],
                        )
                    ),
                    "amount": float(
                        np.round(
                            amount,
                            2,
                        )
                    ),
                    "payment_status": "completed",
                    "reference_code": (
                        f"PAY{payment_id:07d}"
                    ),
                    "notes": pd.NA,
                }
            )

            allocatable_amount = float(
                np.round(
                    amount,
                    2,
                )
            )

            if (
                    transaction_type == "deposit"
                    and RNG.random() < 0.35
            ):
                allocatable_amount = float(
                    np.round(
                        allocatable_amount
                        * RNG.uniform(
                            0.60,
                            0.90,
                        ),
                        2,
                    )
                )

            for procedure_id in balances:
                if allocatable_amount <= 0:
                    break

                outstanding = balances[
                    procedure_id
                ]

                if outstanding <= 0:
                    continue

                allocated_amount = float(
                    np.round(
                        min(
                            outstanding,
                            allocatable_amount,
                        ),
                        2,
                    )
                )

                if allocated_amount <= 0:
                    continue

                allocation_rows.append(
                    {
                        "allocation_id": (
                            allocation_id
                        ),
                        "payment_id": payment_id,
                        "appointment_procedure_id": (
                            procedure_id
                        ),
                        "allocated_amount": (
                            allocated_amount
                        ),
                    }
                )

                balances[procedure_id] = float(
                    np.round(
                        outstanding
                        - allocated_amount,
                        2,
                    )
                )

                allocatable_amount = float(
                    np.round(
                        allocatable_amount
                        - allocated_amount,
                        2,
                    )
                )

                allocation_id += 1

            payment_id += 1

        if RNG.random() < 0.08:
            attempted_amount = float(
                np.round(
                    total_due
                    * RNG.uniform(
                        0.20,
                        0.70,
                    ),
                    2,
                )
            )

            payment_rows.append(
                {
                    "payment_id": payment_id,
                    "patient_id": patient_id,
                    "received_at": (
                            chair_end_at
                            + pd.to_timedelta(
                        int(
                            RNG.integers(
                                0,
                                15,
                            )
                        ),
                        unit="D",
                    )
                    ),
                    "transaction_type": "payment",
                    "payment_arrangement": (
                        arrangement
                    ),
                    "payment_method": str(
                        RNG.choice(
                            [
                                "card",
                                "bank_transfer",
                                "online_payment",
                            ]
                        )
                    ),
                    "amount": attempted_amount,
                    "payment_status": str(
                        RNG.choice(
                            [
                                "pending",
                                "failed",
                                "cancelled",
                                "reversed",
                            ],
                            p=[
                                0.25,
                                0.45,
                                0.20,
                                0.10,
                            ],
                        )
                    ),
                    "reference_code": (
                        f"PAY{payment_id:07d}"
                    ),
                    "notes": pd.NA,
                }
            )

            payment_id += 1

        if RNG.random() < 0.03:
            refund_amount = float(
                np.round(
                    min(
                        collected_target,
                        total_due
                        * RNG.uniform(
                            0.05,
                            0.20,
                        ),
                    ),
                    2,
                )
            )

            if refund_amount > 0:
                payment_rows.append(
                    {
                        "payment_id": payment_id,
                        "patient_id": patient_id,
                        "received_at": (
                                chair_end_at
                                + pd.to_timedelta(
                            int(
                                RNG.integers(
                                    7,
                                    46,
                                )
                            ),
                            unit="D",
                        )
                        ),
                        "transaction_type": (
                            "refund"
                        ),
                        "payment_arrangement": (
                            "not_applicable"
                        ),
                        "payment_method": str(
                            RNG.choice(
                                [
                                    "card",
                                    "bank_transfer",
                                    "online_payment",
                                ]
                            )
                        ),
                        "amount": refund_amount,
                        "payment_status": (
                            "completed"
                        ),
                        "reference_code": (
                            f"PAY{payment_id:07d}"
                        ),
                        "notes": (
                            "Synthetic refund"
                        ),
                    }
                )

                payment_id += 1

    payments = pd.DataFrame(
        payment_rows,
        columns=[
            "payment_id",
            "patient_id",
            "received_at",
            "transaction_type",
            "payment_arrangement",
            "payment_method",
            "amount",
            "payment_status",
            "reference_code",
            "notes",
        ],
    )

    payment_allocations = pd.DataFrame(
        allocation_rows,
        columns=[
            "allocation_id",
            "payment_id",
            "appointment_procedure_id",
            "allocated_amount",
        ],
    )

    return payments, payment_allocations


def validate(
        patients: pd.DataFrame,
        dentists: pd.DataFrame,
        appointments: pd.DataFrame,
        procedure_catalog: pd.DataFrame,
        appointment_procedures: pd.DataFrame,
        treatment_plans: pd.DataFrame,
        treatment_plan_items: pd.DataFrame,
        payments: pd.DataFrame,
        payment_allocations: pd.DataFrame,
) -> None:
    assert patients["patient_id"].is_unique
    assert dentists["dentist_id"].is_unique
    assert appointments["appointment_id"].is_unique
    assert procedure_catalog["procedure_code"].is_unique

    assert appointment_procedures[
        "appointment_procedure_id"
    ].is_unique

    assert treatment_plans["plan_id"].is_unique
    assert treatment_plan_items["plan_item_id"].is_unique
    assert payments["payment_id"].is_unique
    assert payment_allocations["allocation_id"].is_unique

    assert appointments["patient_id"].isin(
        patients["patient_id"]
    ).all()

    assert appointments["dentist_id"].isin(
        dentists["dentist_id"]
    ).all()

    assert appointments["booked_at"].lt(
        appointments["scheduled_start_at"]
    ).all()

    completed_mask = appointments[
        "status"
    ].eq("completed")

    completed_times = appointments.loc[
        completed_mask,
        [
            "check_in_at",
            "chair_start_at",
            "chair_end_at",
            "checkout_at",
        ],
    ]

    assert completed_times.notna().all().all()

    assert (
            completed_times["check_in_at"]
            <= completed_times["chair_start_at"]
    ).all()

    assert (
            completed_times["chair_start_at"]
            < completed_times["chair_end_at"]
    ).all()

    assert (
            completed_times["chair_end_at"]
            <= completed_times["checkout_at"]
    ).all()

    changed_mask = appointments["status"].isin(
        [
            "cancelled",
            "rescheduled",
        ]
    )

    assert appointments.loc[
        changed_mask,
        "status_updated_at",
    ].notna().all()

    assert appointments.loc[
        changed_mask,
        "status_change_reason",
    ].notna().all()

    linked_reschedules = appointments[
        "rescheduled_from_appointment_id"
    ].dropna()

    assert linked_reschedules.isin(
        appointments["appointment_id"]
    ).all()

    completed_appointment_ids = appointments.loc[
        completed_mask,
        "appointment_id",
    ]

    assert appointment_procedures[
        "appointment_id"
    ].isin(
        completed_appointment_ids
    ).all()

    active_procedure_codes = procedure_catalog.loc[
        procedure_catalog["active"],
        "procedure_code",
    ]

    assert appointment_procedures[
        "procedure_code"
    ].isin(
        active_procedure_codes
    ).all()

    assert appointment_procedures[
        "fee_amount"
    ].gt(0).all()

    assert appointment_procedures[
        "discount_amount"
    ].ge(0).all()

    assert (
            appointment_procedures["discount_amount"]
            <= appointment_procedures["fee_amount"]
    ).all()

    assert appointment_procedures[
        "direct_cost"
    ].ge(0).all()

    assert treatment_plans["patient_id"].isin(
        patients["patient_id"]
    ).all()

    assert treatment_plans[
        "proposed_by_dentist_id"
    ].isin(
        dentists["dentist_id"]
    ).all()

    assert treatment_plans[
        "source_appointment_id"
    ].isin(
        appointments["appointment_id"]
    ).all()

    assert treatment_plan_items["plan_id"].isin(
        treatment_plans["plan_id"]
    ).all()

    assert treatment_plan_items[
        "procedure_code"
    ].isin(
        procedure_catalog["procedure_code"]
    ).all()

    pending_mask = treatment_plan_items[
        "decision_status"
    ].eq("pending")

    assert treatment_plan_items.loc[
        pending_mask,
        "decision_at",
    ].isna().all()

    assert treatment_plan_items.loc[
        ~pending_mask,
        "decision_at",
    ].notna().all()

    decision_check = treatment_plan_items.merge(
        treatment_plans[
            [
                "plan_id",
                "proposed_at",
            ]
        ],
        on="plan_id",
        how="left",
        validate="many_to_one",
    )

    decided_mask = decision_check[
        "decision_status"
    ].ne("pending")

    assert decision_check.loc[
        decided_mask,
        "decision_at",
    ].ge(
        decision_check.loc[
            decided_mask,
            "proposed_at",
        ]
    ).all()

    linked_plan_items = appointment_procedures[
        "plan_item_id"
    ].notna()

    if linked_plan_items.any():
        plan_link_check = (
            appointment_procedures.loc[
                linked_plan_items,
                [
                    "plan_item_id",
                    "procedure_code",
                ],
            ]
            .merge(
                treatment_plan_items[
                    [
                        "plan_item_id",
                        "procedure_code",
                    ]
                ],
                on="plan_item_id",
                how="left",
                suffixes=(
                    "_performed",
                    "_planned",
                ),
                validate="many_to_one",
            )
        )

        assert plan_link_check[
            "procedure_code_planned"
        ].notna().all()

        assert (
                plan_link_check[
                    "procedure_code_performed"
                ]
                == plan_link_check[
                    "procedure_code_planned"
                ]
        ).all()

    assert payments["patient_id"].isin(
        patients["patient_id"]
    ).all()

    assert payments["amount"].gt(0).all()

    completed_payment_ids = payments.loc[
        payments["payment_status"].eq(
            "completed"
        ),
        "payment_id",
    ]

    assert payment_allocations[
        "payment_id"
    ].isin(
        completed_payment_ids
    ).all()

    assert payment_allocations[
        "appointment_procedure_id"
    ].isin(
        appointment_procedures[
            "appointment_procedure_id"
        ]
    ).all()

    assert payment_allocations[
        "allocated_amount"
    ].gt(0).all()

    allocated_totals = (
        payment_allocations.groupby(
            "payment_id"
        )["allocated_amount"]
        .sum()
    )

    payment_amounts = payments.set_index(
        "payment_id"
    )["amount"]

    assert allocated_totals.le(
        payment_amounts.loc[
            allocated_totals.index
        ]
        + 0.01
    ).all()


def main() -> None:
    args = parse_args()
    args.output.mkdir(
        parents=True,
        exist_ok=True,
    )

    patients = generate_patients(
        args.patients
    )

    dentists = generate_dentists()

    appointments = generate_appointments(
        args.appointments,
        patients,
        dentists,
    )

    procedure_catalog = (
        generate_procedure_catalog()
    )

    appointment_procedures = (
        generate_appointment_procedures(
            appointments,
            dentists,
            procedure_catalog,
        )
    )

    (
        treatment_plans,
        treatment_plan_items,
    ) = generate_treatment_plans(
        appointments,
        dentists,
        procedure_catalog,
    )

    appointment_procedures = (
        link_accepted_plan_items_to_procedures(
            appointments,
            appointment_procedures,
            treatment_plans,
            treatment_plan_items,
        )
    )

    (
        payments,
        payment_allocations,
    ) = generate_payments(
        appointments,
        appointment_procedures,
    )

    validate(
        patients,
        dentists,
        appointments,
        procedure_catalog,
        appointment_procedures,
        treatment_plans,
        treatment_plan_items,
        payments,
        payment_allocations,
    )

    datasets = {
        "patients.csv": patients,
        "dentists.csv": dentists,
        "appointments.csv": appointments,
        "procedure_catalog.csv": (
            procedure_catalog
        ),
        "appointment_procedures.csv": (
            appointment_procedures
        ),
        "treatment_plans.csv": (
            treatment_plans
        ),
        "treatment_plan_items.csv": (
            treatment_plan_items
        ),
        "payments.csv": payments,
        "payment_allocations.csv": (
            payment_allocations
        ),
    }

    for name, dataframe in datasets.items():
        dataframe.to_csv(
            args.output / name,
            index=False,
        )

        print(
            f"Wrote {name}: "
            f"{len(dataframe):,} rows"
        )


if __name__ == "__main__":
    main()
