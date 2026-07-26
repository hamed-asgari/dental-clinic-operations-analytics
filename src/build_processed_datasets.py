"""Build validated analytical datasets for Power BI."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class RawDatasetSpec:
    name: str
    csv_name: str
    columns: tuple[str, ...]
    datetime_columns: tuple[str, ...] = ()


RAW_DATASET_SPECS = (
    RawDatasetSpec(
        name="patients",
        csv_name="patients.csv",
        columns=(
            "patient_id",
            "birth_year",
            "sex",
            "city_area",
            "registered_at",
            "insurance_type",
            "referral_source",
            "preferred_contact_channel",
            "patient_status",
        ),
        datetime_columns=("registered_at",),
    ),
    RawDatasetSpec(
        name="dentists",
        csv_name="dentists.csv",
        columns=(
            "dentist_id",
            "dentist_role",
            "engagement_type",
            "start_date",
            "end_date",
            "scheduled_hours_weekly",
            "active",
        ),
        datetime_columns=("start_date", "end_date"),
    ),
    RawDatasetSpec(
        name="appointments",
        csv_name="appointments.csv",
        columns=(
            "appointment_id",
            "patient_id",
            "dentist_id",
            "booked_at",
            "scheduled_start_at",
            "planned_duration_min",
            "visit_type",
            "booking_channel",
            "status",
            "status_updated_at",
            "reminder_sent",
            "check_in_at",
            "chair_start_at",
            "chair_end_at",
            "checkout_at",
            "status_change_reason",
            "rescheduled_from_appointment_id",
        ),
        datetime_columns=(
            "booked_at",
            "scheduled_start_at",
            "status_updated_at",
            "check_in_at",
            "chair_start_at",
            "chair_end_at",
            "checkout_at",
        ),
    ),
    RawDatasetSpec(
        name="procedure_catalog",
        csv_name="procedure_catalog.csv",
        columns=(
            "procedure_code",
            "procedure_name",
            "procedure_group",
            "default_planned_duration_min",
            "standard_fee_amount",
            "standard_direct_cost",
            "active",
        ),
    ),
    RawDatasetSpec(
        name="appointment_procedures",
        csv_name="appointment_procedures.csv",
        columns=(
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
        ),
    ),
    RawDatasetSpec(
        name="treatment_plans",
        csv_name="treatment_plans.csv",
        columns=(
            "plan_id",
            "patient_id",
            "proposed_by_dentist_id",
            "source_appointment_id",
            "proposed_at",
            "plan_status",
            "valid_until",
        ),
        datetime_columns=("proposed_at", "valid_until"),
    ),
    RawDatasetSpec(
        name="treatment_plan_items",
        csv_name="treatment_plan_items.csv",
        columns=(
            "plan_item_id",
            "plan_id",
            "procedure_code",
            "tooth_code",
            "sequence_order",
            "priority_level",
            "proposed_quantity",
            "proposed_fee_amount",
            "proposed_discount_amount",
            "decision_status",
            "decision_at",
        ),
        datetime_columns=("decision_at",),
    ),
    RawDatasetSpec(
        name="payments",
        csv_name="payments.csv",
        columns=(
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
        ),
        datetime_columns=("received_at",),
    ),
    RawDatasetSpec(
        name="payment_allocations",
        csv_name="payment_allocations.csv",
        columns=(
            "allocation_id",
            "payment_id",
            "appointment_procedure_id",
            "allocated_amount",
        ),
    ),
)

DATE_SOURCE_COLUMNS = (
    ("patients", "registered_at"),
    ("dentists", "start_date"),
    ("dentists", "end_date"),
    ("appointments", "booked_at"),
    ("appointments", "scheduled_start_at"),
    ("appointments", "status_updated_at"),
    ("appointments", "check_in_at"),
    ("appointments", "chair_start_at"),
    ("appointments", "chair_end_at"),
    ("appointments", "checkout_at"),
    ("treatment_plans", "proposed_at"),
    ("treatment_plans", "valid_until"),
    ("treatment_plan_items", "decision_at"),
    ("payments", "received_at"),
)

DIMENSION_FILE_NAMES = {
    "dim_date": "dim_date.csv",
    "dim_patients": "dim_patients.csv",
    "dim_dentists": "dim_dentists.csv",
    "dim_procedures": "dim_procedures.csv",
}

APPOINTMENT_FACT_FILE_NAMES = {
    "fact_appointments": "fact_appointments.csv",
}

PROCEDURE_FACT_FILE_NAMES = {
    "fact_procedures": "fact_procedures.csv",
}

TREATMENT_PLAN_ITEM_FACT_FILE_NAMES = {
    (
        "fact_treatment_plan_items"
    ): "fact_treatment_plan_items.csv",
}

PAYMENT_FACT_FILE_NAMES = {
    "fact_payments": "fact_payments.csv",
}

PAYMENT_ALLOCATION_FACT_FILE_NAMES = {
    (
        "fact_payment_allocations"
    ): "fact_payment_allocations.csv",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
    )

    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw"),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed"),
    )

    return parser.parse_args()


def read_raw_datasets(
        raw_dir: Path,
) -> dict[str, pd.DataFrame]:
    if not raw_dir.exists():
        raise FileNotFoundError(
            f"Raw data directory not found: {raw_dir}"
        )

    datasets: dict[str, pd.DataFrame] = {}

    for spec in RAW_DATASET_SPECS:
        csv_path = raw_dir / spec.csv_name

        if not csv_path.exists():
            raise FileNotFoundError(
                f"Raw CSV file not found: {csv_path}"
            )

        dataframe = pd.read_csv(
            csv_path,
            parse_dates=list(spec.datetime_columns),
        )

        expected_columns = list(spec.columns)
        actual_columns = dataframe.columns.tolist()

        if actual_columns != expected_columns:
            raise ValueError(
                f"Column mismatch in {spec.csv_name}. "
                f"Expected: {expected_columns}. "
                f"Found: {actual_columns}."
            )

        datasets[spec.name] = dataframe

    return datasets


def validate_primary_key(
        dataframe: pd.DataFrame,
        key_column: str,
        dataset_name: str,
) -> None:
    missing_key_count = int(
        dataframe[key_column].isna().sum()
    )

    duplicate_key_count = int(
        dataframe[key_column].duplicated().sum()
    )

    if missing_key_count or duplicate_key_count:
        raise ValueError(
            f"Invalid primary key in {dataset_name}. "
            f"Missing keys: {missing_key_count}. "
            f"Duplicate keys: {duplicate_key_count}."
        )


def validate_required_columns(
        dataframe: pd.DataFrame,
        required_columns: tuple[str, ...],
        dataset_name: str,
) -> None:
    missing_counts = {
        column_name: int(
            dataframe[column_name].isna().sum()
        )
        for column_name in required_columns
        if dataframe[column_name].isna().any()
    }

    if missing_counts:
        raise ValueError(
            f"Missing required values in "
            f"{dataset_name}: {missing_counts}."
        )


def validate_foreign_key(
        child_dataframe: pd.DataFrame,
        child_column: str,
        parent_dataframe: pd.DataFrame,
        parent_column: str,
        relationship_name: str,
) -> None:
    child_values = child_dataframe[
        child_column
    ].dropna()

    orphan_count = int(
        (
            ~child_values.isin(
                parent_dataframe[parent_column]
            )
        ).sum()
    )

    if orphan_count:
        raise ValueError(
            f"Orphan keys in {relationship_name}: "
            f"{orphan_count}."
        )


def datetime_to_date_key(
        series: pd.Series,
) -> pd.Series:
    return pd.to_numeric(
        series.dt.strftime("%Y%m%d"),
        errors="coerce",
    ).astype("Int64")


def minutes_between(
        end_series: pd.Series,
        start_series: pd.Series,
) -> pd.Series:
    return (
        (
            end_series
            - start_series
        ).dt.total_seconds()
        / 60
    ).round(2)


def build_dim_date(
        datasets: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    source_dates = pd.concat(
        [
            datasets[dataset_name][column_name]
            for dataset_name, column_name
            in DATE_SOURCE_COLUMNS
        ],
        ignore_index=True,
    ).dropna()

    if source_dates.empty:
        raise ValueError(
            "Cannot build dim_date without source dates."
        )

    start_date = source_dates.min().normalize()
    end_date = source_dates.max().normalize()
    date_values = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D",
    )

    iso_calendar = date_values.isocalendar()

    dim_date = pd.DataFrame(
        {
            "date": date_values,
        }
    )

    dim_date["date_key"] = (
        dim_date["date"].dt.strftime("%Y%m%d")
        .astype("int64")
    )
    dim_date["year"] = dim_date["date"].dt.year
    dim_date["quarter_number"] = (
        dim_date["date"].dt.quarter
    )
    dim_date["quarter"] = (
        "Q"
        + dim_date["quarter_number"].astype(str)
    )
    dim_date["month_number"] = (
        dim_date["date"].dt.month
    )
    dim_date["month_name"] = (
        dim_date["date"].dt.month_name()
    )
    dim_date["month_short_name"] = (
        dim_date["date"].dt.strftime("%b")
    )
    dim_date["year_month"] = (
        dim_date["date"].dt.strftime("%Y-%m")
    )
    dim_date["year_month_sort"] = (
        dim_date["date"].dt.strftime("%Y%m")
        .astype("int64")
    )
    dim_date["week_of_year"] = (
        iso_calendar["week"]
        .reset_index(drop=True)
        .astype("int64")
    )
    dim_date["day_of_month"] = (
        dim_date["date"].dt.day
    )
    dim_date["weekday_number"] = (
        dim_date["date"].dt.weekday + 1
    )
    dim_date["weekday_name"] = (
        dim_date["date"].dt.day_name()
    )
    dim_date["date"] = (
        dim_date["date"].dt.date
    )

    return dim_date[
        [
            "date_key",
            "date",
            "year",
            "quarter_number",
            "quarter",
            "month_number",
            "month_name",
            "month_short_name",
            "year_month",
            "year_month_sort",
            "week_of_year",
            "day_of_month",
            "weekday_number",
            "weekday_name",
        ]
    ].copy()


def build_dimensions(
        datasets: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    return {
        "dim_date": build_dim_date(datasets),
        "dim_patients": datasets["patients"].copy(),
        "dim_dentists": datasets["dentists"].copy(),
        "dim_procedures": (
            datasets["procedure_catalog"].copy()
        ),
    }


def validate_dimensions(
        datasets: dict[str, pd.DataFrame],
        dimensions: dict[str, pd.DataFrame],
) -> None:
    dimension_checks = (
        (
            "dim_date",
            "date_key",
            None,
        ),
        (
            "dim_patients",
            "patient_id",
            "patients",
        ),
        (
            "dim_dentists",
            "dentist_id",
            "dentists",
        ),
        (
            "dim_procedures",
            "procedure_code",
            "procedure_catalog",
        ),
    )
    required_columns = {
        "dim_date": tuple(
            dimensions["dim_date"].columns
        ),
        "dim_patients": tuple(
            dimensions["dim_patients"].columns
        ),
        "dim_dentists": tuple(
            column_name
            for column_name
            in dimensions["dim_dentists"].columns
            if column_name != "end_date"
        ),
        "dim_procedures": tuple(
            dimensions["dim_procedures"].columns
        ),
    }

    for (
        dimension_name,
        key_column,
        raw_dataset_name,
    ) in dimension_checks:
        dimension = dimensions[dimension_name]

        validate_required_columns(
            dimension,
            required_columns[dimension_name],
            dimension_name,
        )
        validate_primary_key(
            dimension,
            key_column,
            dimension_name,
        )

        if (
            raw_dataset_name is not None
            and len(dimension)
            != len(datasets[raw_dataset_name])
        ):
            raise ValueError(
                f"Row-count mismatch for "
                f"{dimension_name}."
            )

    dim_date = dimensions["dim_date"]
    expected_date_count = (
        pd.to_datetime(dim_date["date"]).max()
        - pd.to_datetime(dim_date["date"]).min()
    ).days + 1

    if len(dim_date) != expected_date_count:
        raise ValueError(
            "dim_date contains a date gap."
        )


def build_fact_appointments(
        datasets: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    appointments = datasets["appointments"].copy()

    fact_appointments = appointments.merge(
        datasets["patients"][
            [
                "patient_id",
                "birth_year",
            ]
        ],
        on="patient_id",
        how="left",
        validate="many_to_one",
    )

    fact_appointments["appointment_date_key"] = (
        datetime_to_date_key(
            fact_appointments["scheduled_start_at"]
        )
    )
    fact_appointments["booked_date_key"] = (
        datetime_to_date_key(
            fact_appointments["booked_at"]
        )
    )
    fact_appointments[
        "status_updated_date_key"
    ] = datetime_to_date_key(
        fact_appointments["status_updated_at"]
    )
    fact_appointments["scheduled_hour"] = (
        fact_appointments[
            "scheduled_start_at"
        ].dt.hour
    )

    fact_appointments["appointment_count"] = 1
    fact_appointments[
        "completed_appointment_count"
    ] = (
        fact_appointments["status"]
        .eq("completed")
        .astype("int8")
    )
    fact_appointments["no_show_count"] = (
        fact_appointments["status"]
        .eq("no_show")
        .astype("int8")
    )
    fact_appointments["cancelled_count"] = (
        fact_appointments["status"]
        .eq("cancelled")
        .astype("int8")
    )
    fact_appointments["rescheduled_count"] = (
        fact_appointments["status"]
        .eq("rescheduled")
        .astype("int8")
    )
    fact_appointments["non_completed_count"] = (
        fact_appointments["status"]
        .ne("completed")
        .astype("int8")
    )

    fact_appointments["booking_lead_minutes"] = (
        minutes_between(
            fact_appointments["scheduled_start_at"],
            fact_appointments["booked_at"],
        )
    )
    fact_appointments["patient_wait_minutes"] = (
        minutes_between(
            fact_appointments["chair_start_at"],
            fact_appointments["check_in_at"],
        )
    )
    fact_appointments["actual_chair_minutes"] = (
        minutes_between(
            fact_appointments["chair_end_at"],
            fact_appointments["chair_start_at"],
        )
    )
    fact_appointments["checkout_delay_minutes"] = (
        minutes_between(
            fact_appointments["checkout_at"],
            fact_appointments["chair_end_at"],
        )
    )
    fact_appointments["schedule_variance_minutes"] = (
        fact_appointments["actual_chair_minutes"]
        - fact_appointments["planned_duration_min"]
    )

    status_notice_minutes = minutes_between(
        fact_appointments["scheduled_start_at"],
        fact_appointments["status_updated_at"],
    )
    notice_status_mask = fact_appointments[
        "status"
    ].isin(
        [
            "cancelled",
            "rescheduled",
        ]
    )
    fact_appointments["status_notice_minutes"] = (
        status_notice_minutes.where(
            notice_status_mask
        )
    )

    fact_appointments[
        "approximate_age_at_appointment"
    ] = (
        fact_appointments[
            "scheduled_start_at"
        ].dt.year
        - fact_appointments["birth_year"]
    ).astype("Int64")
    fact_appointments[
        "rescheduled_from_appointment_id"
    ] = pd.to_numeric(
        fact_appointments[
            "rescheduled_from_appointment_id"
        ],
        errors="raise",
    ).astype("Int64")

    return fact_appointments[
        [
            "appointment_id",
            "patient_id",
            "dentist_id",
            "appointment_date_key",
            "booked_date_key",
            "status_updated_date_key",
            "booked_at",
            "scheduled_start_at",
            "scheduled_hour",
            "planned_duration_min",
            "visit_type",
            "booking_channel",
            "status",
            "status_updated_at",
            "reminder_sent",
            "check_in_at",
            "chair_start_at",
            "chair_end_at",
            "checkout_at",
            "status_change_reason",
            "rescheduled_from_appointment_id",
            "appointment_count",
            "completed_appointment_count",
            "no_show_count",
            "cancelled_count",
            "rescheduled_count",
            "non_completed_count",
            "booking_lead_minutes",
            "patient_wait_minutes",
            "actual_chair_minutes",
            "checkout_delay_minutes",
            "schedule_variance_minutes",
            "status_notice_minutes",
            "approximate_age_at_appointment",
        ]
    ].copy()


def validate_fact_appointments(
        datasets: dict[str, pd.DataFrame],
        dimensions: dict[str, pd.DataFrame],
        fact_appointments: pd.DataFrame,
) -> None:
    if len(fact_appointments) != len(
        datasets["appointments"]
    ):
        raise ValueError(
            "Row-count mismatch for fact_appointments."
        )

    validate_required_columns(
        fact_appointments,
        (
            "appointment_id",
            "patient_id",
            "dentist_id",
            "appointment_date_key",
            "booked_date_key",
            "booked_at",
            "scheduled_start_at",
            "scheduled_hour",
            "planned_duration_min",
            "visit_type",
            "booking_channel",
            "status",
            "reminder_sent",
            "appointment_count",
            "completed_appointment_count",
            "no_show_count",
            "cancelled_count",
            "rescheduled_count",
            "non_completed_count",
            "booking_lead_minutes",
            "approximate_age_at_appointment",
        ),
        "fact_appointments",
    )
    validate_primary_key(
        fact_appointments,
        "appointment_id",
        "fact_appointments",
    )
    validate_foreign_key(
        fact_appointments,
        "patient_id",
        dimensions["dim_patients"],
        "patient_id",
        "fact_appointments.patient_id",
    )
    validate_foreign_key(
        fact_appointments,
        "dentist_id",
        dimensions["dim_dentists"],
        "dentist_id",
        "fact_appointments.dentist_id",
    )

    for date_key_column in (
        "appointment_date_key",
        "booked_date_key",
        "status_updated_date_key",
    ):
        validate_foreign_key(
            fact_appointments,
            date_key_column,
            dimensions["dim_date"],
            "date_key",
            (
                f"fact_appointments."
                f"{date_key_column}"
            ),
        )

    status_flag_checks = {
        "completed_appointment_count": "completed",
        "no_show_count": "no_show",
        "cancelled_count": "cancelled",
        "rescheduled_count": "rescheduled",
    }

    for flag_column, status_value in (
        status_flag_checks.items()
    ):
        expected_values = (
            fact_appointments["status"]
            .eq(status_value)
            .astype("int8")
        )

        if not fact_appointments[
            flag_column
        ].equals(expected_values):
            raise ValueError(
                f"Invalid {flag_column} values."
            )

    completed_mask = fact_appointments[
        "status"
    ].eq("completed")

    if fact_appointments.loc[
        completed_mask,
        "actual_chair_minutes",
    ].isna().any():
        raise ValueError(
            "Completed appointments have "
            "missing actual chair minutes."
        )

    if fact_appointments.loc[
        completed_mask,
        "actual_chair_minutes",
    ].le(0).any():
        raise ValueError(
            "Completed appointments have "
            "non-positive actual chair minutes."
        )

    if fact_appointments.loc[
        ~completed_mask,
        "actual_chair_minutes",
    ].notna().any():
        raise ValueError(
            "Non-completed appointments have "
            "actual chair minutes."
        )

    non_negative_columns = (
        "booking_lead_minutes",
        "patient_wait_minutes",
        "actual_chair_minutes",
        "checkout_delay_minutes",
        "status_notice_minutes",
    )

    for column_name in non_negative_columns:
        if fact_appointments[
            column_name
        ].dropna().lt(0).any():
            raise ValueError(
                f"Negative values found in "
                f"{column_name}."
            )


def build_fact_procedures(
        datasets: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    appointment_procedures = datasets[
        "appointment_procedures"
    ].copy()

    appointment_context = datasets[
        "appointments"
    ][
        [
            "appointment_id",
            "patient_id",
            "dentist_id",
            "scheduled_start_at",
            "status",
            "chair_start_at",
            "chair_end_at",
        ]
    ].rename(
        columns={
            "status": "appointment_status",
        }
    )

    procedure_context = datasets[
        "procedure_catalog"
    ][
        [
            "procedure_code",
            "default_planned_duration_min",
            "standard_fee_amount",
            "standard_direct_cost",
        ]
    ]

    allocation_totals = (
        datasets["payment_allocations"]
        .groupby(
            "appointment_procedure_id",
            as_index=False,
        )
        .agg(
            allocated_amount_total=(
                "allocated_amount",
                "sum",
            ),
        )
    )

    fact_procedures = (
        appointment_procedures
        .merge(
            appointment_context,
            on="appointment_id",
            how="left",
            validate="many_to_one",
        )
        .merge(
            procedure_context,
            on="procedure_code",
            how="left",
            validate="many_to_one",
        )
        .merge(
            allocation_totals,
            on="appointment_procedure_id",
            how="left",
            validate="one_to_one",
        )
    )

    fact_procedures["plan_item_id"] = (
        pd.to_numeric(
            fact_procedures["plan_item_id"],
            errors="raise",
        ).astype("Int64")
    )
    fact_procedures["appointment_date_key"] = (
        datetime_to_date_key(
            fact_procedures["scheduled_start_at"]
        )
    )
    fact_procedures["procedure_count"] = 1
    fact_procedures[
        "completed_procedure_count"
    ] = (
        fact_procedures["completion_status"]
        .eq("completed")
        .astype("int8")
    )
    fact_procedures[
        "partially_completed_procedure_count"
    ] = (
        fact_procedures["completion_status"]
        .eq("partially_completed")
        .astype("int8")
    )
    fact_procedures[
        "discontinued_procedure_count"
    ] = (
        fact_procedures["completion_status"]
        .eq("discontinued")
        .astype("int8")
    )
    fact_procedures[
        "linked_to_plan_item_count"
    ] = (
        fact_procedures["plan_item_id"]
        .notna()
        .astype("int8")
    )

    fact_procedures["duration_weight"] = (
        fact_procedures[
            "default_planned_duration_min"
        ]
        * fact_procedures["quantity"]
    )
    fact_procedures[
        "appointment_total_duration_weight"
    ] = (
        fact_procedures
        .groupby("appointment_id")[
            "duration_weight"
        ]
        .transform("sum")
    )
    actual_chair_minutes = minutes_between(
        fact_procedures["chair_end_at"],
        fact_procedures["chair_start_at"],
    )
    fact_procedures[
        "allocated_chair_minutes"
    ] = (
        actual_chair_minutes
        * fact_procedures["duration_weight"]
        / fact_procedures[
            "appointment_total_duration_weight"
        ]
    )
    fact_procedures[
        "allocated_chair_hours"
    ] = (
        fact_procedures[
            "allocated_chair_minutes"
        ]
        / 60
    )

    fact_procedures["net_revenue"] = (
        fact_procedures["fee_amount"]
        - fact_procedures["discount_amount"]
    ).round(2)
    fact_procedures["direct_margin"] = (
        fact_procedures["net_revenue"]
        - fact_procedures["direct_cost"]
    ).round(2)
    fact_procedures["standard_fee_total"] = (
        fact_procedures["standard_fee_amount"]
        * fact_procedures["quantity"]
    ).round(2)
    fact_procedures[
        "standard_direct_cost_total"
    ] = (
        fact_procedures["standard_direct_cost"]
        * fact_procedures["quantity"]
    ).round(2)
    fact_procedures[
        "fee_variance_from_standard"
    ] = (
        fact_procedures["fee_amount"]
        - fact_procedures["standard_fee_total"]
    ).round(2)

    fact_procedures[
        "allocated_amount_total"
    ] = (
        fact_procedures[
            "allocated_amount_total"
        ]
        .fillna(0)
        .round(2)
    )
    fact_procedures["outstanding_balance"] = (
        fact_procedures["net_revenue"]
        - fact_procedures[
            "allocated_amount_total"
        ]
    ).round(2)

    fact_procedures[
        "allocated_chair_minutes"
    ] = fact_procedures[
        "allocated_chair_minutes"
    ].round(6)
    fact_procedures[
        "allocated_chair_hours"
    ] = fact_procedures[
        "allocated_chair_hours"
    ].round(6)

    return fact_procedures[
        [
            "appointment_procedure_id",
            "appointment_id",
            "plan_item_id",
            "patient_id",
            "dentist_id",
            "procedure_code",
            "appointment_date_key",
            "tooth_code",
            "quantity",
            "completion_status",
            "procedure_count",
            "completed_procedure_count",
            "partially_completed_procedure_count",
            "discontinued_procedure_count",
            "linked_to_plan_item_count",
            "duration_weight",
            "allocated_chair_minutes",
            "allocated_chair_hours",
            "fee_amount",
            "discount_amount",
            "net_revenue",
            "direct_cost",
            "direct_margin",
            "standard_fee_total",
            "standard_direct_cost_total",
            "fee_variance_from_standard",
            "allocated_amount_total",
            "outstanding_balance",
        ]
    ].copy()


def validate_fact_procedures(
        datasets: dict[str, pd.DataFrame],
        dimensions: dict[str, pd.DataFrame],
        fact_appointments: pd.DataFrame,
        fact_procedures: pd.DataFrame,
) -> None:
    if len(fact_procedures) != len(
        datasets["appointment_procedures"]
    ):
        raise ValueError(
            "Row-count mismatch for fact_procedures."
        )

    validate_required_columns(
        fact_procedures,
        tuple(
            column_name
            for column_name
            in fact_procedures.columns
            if column_name not in (
                "plan_item_id",
                "tooth_code",
            )
        ),
        "fact_procedures",
    )
    validate_primary_key(
        fact_procedures,
        "appointment_procedure_id",
        "fact_procedures",
    )

    foreign_key_checks = (
        (
            "appointment_id",
            fact_appointments,
            "appointment_id",
        ),
        (
            "patient_id",
            dimensions["dim_patients"],
            "patient_id",
        ),
        (
            "dentist_id",
            dimensions["dim_dentists"],
            "dentist_id",
        ),
        (
            "procedure_code",
            dimensions["dim_procedures"],
            "procedure_code",
        ),
        (
            "appointment_date_key",
            dimensions["dim_date"],
            "date_key",
        ),
        (
            "plan_item_id",
            datasets["treatment_plan_items"],
            "plan_item_id",
        ),
    )

    for (
        child_column,
        parent_dataframe,
        parent_column,
    ) in foreign_key_checks:
        validate_foreign_key(
            fact_procedures,
            child_column,
            parent_dataframe,
            parent_column,
            (
                f"fact_procedures."
                f"{child_column}"
            ),
        )

    positive_columns = (
        "quantity",
        "duration_weight",
        "allocated_chair_minutes",
    )

    for column_name in positive_columns:
        if fact_procedures[
            column_name
        ].le(0).any():
            raise ValueError(
                f"Non-positive values found in "
                f"{column_name}."
            )

    expected_chair_minutes = (
        fact_appointments[
            "actual_chair_minutes"
        ].sum()
    )
    allocated_chair_minutes = (
        fact_procedures[
            "allocated_chair_minutes"
        ].sum()
    )

    if abs(
        allocated_chair_minutes
        - expected_chair_minutes
    ) > 0.001:
        raise ValueError(
            "Procedure chair-time allocation "
            "does not reconcile to appointments."
        )

    expected_net_revenue = (
        datasets["appointment_procedures"][
            "fee_amount"
        ]
        - datasets["appointment_procedures"][
            "discount_amount"
        ]
    ).sum()

    if abs(
        fact_procedures["net_revenue"].sum()
        - expected_net_revenue
    ) > 0.01:
        raise ValueError(
            "Procedure net revenue does not "
            "reconcile to raw data."
        )

    expected_allocated_amount = datasets[
        "payment_allocations"
    ]["allocated_amount"].sum()

    if abs(
        fact_procedures[
            "allocated_amount_total"
        ].sum()
        - expected_allocated_amount
    ) > 0.01:
        raise ValueError(
            "Procedure payment allocations do "
            "not reconcile to raw data."
        )

    if fact_procedures[
        "outstanding_balance"
    ].lt(-0.005).any():
        raise ValueError(
            "Negative procedure outstanding "
            "balances found."
        )


def build_fact_treatment_plan_items(
        datasets: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    treatment_plan_items = datasets[
        "treatment_plan_items"
    ].copy()

    plan_context = datasets[
        "treatment_plans"
    ][
        [
            "plan_id",
            "patient_id",
            "proposed_by_dentist_id",
            "source_appointment_id",
            "proposed_at",
            "plan_status",
            "valid_until",
        ]
    ]

    procedure_link_context = (
        datasets["appointment_procedures"]
        .loc[
            lambda dataframe: (
                dataframe["plan_item_id"].notna()
            )
        ]
        .merge(
            datasets["appointments"][
                [
                    "appointment_id",
                    "scheduled_start_at",
                ]
            ],
            on="appointment_id",
            how="left",
            validate="many_to_one",
        )
    )

    procedure_link_context[
        "linked_net_revenue"
    ] = (
        procedure_link_context["fee_amount"]
        - procedure_link_context["discount_amount"]
    ).round(2)

    linked_procedure_summary = (
        procedure_link_context
        .groupby(
            "plan_item_id",
            as_index=False,
        )
        .agg(
            linked_procedure_count=(
                "appointment_procedure_id",
                "size",
            ),
            linked_completed_procedure_count=(
                "completion_status",
                lambda values: (
                    values.eq("completed").sum()
                ),
            ),
            linked_quantity=(
                "quantity",
                "sum",
            ),
            linked_net_revenue=(
                "linked_net_revenue",
                "sum",
            ),
            first_linked_procedure_at=(
                "scheduled_start_at",
                "min",
            ),
        )
    )

    fact_treatment_plan_items = (
        treatment_plan_items
        .merge(
            plan_context,
            on="plan_id",
            how="left",
            validate="many_to_one",
        )
        .merge(
            linked_procedure_summary,
            on="plan_item_id",
            how="left",
            validate="one_to_one",
        )
    )

    fact_treatment_plan_items[
        "source_appointment_id"
    ] = pd.to_numeric(
        fact_treatment_plan_items[
            "source_appointment_id"
        ],
        errors="raise",
    ).astype("Int64")

    fact_treatment_plan_items[
        "proposed_date_key"
    ] = datetime_to_date_key(
        fact_treatment_plan_items["proposed_at"]
    )
    fact_treatment_plan_items[
        "decision_date_key"
    ] = datetime_to_date_key(
        fact_treatment_plan_items["decision_at"]
    )
    fact_treatment_plan_items[
        "valid_until_date_key"
    ] = datetime_to_date_key(
        fact_treatment_plan_items["valid_until"]
    )
    fact_treatment_plan_items[
        "first_linked_procedure_date_key"
    ] = datetime_to_date_key(
        fact_treatment_plan_items[
            "first_linked_procedure_at"
        ]
    )

    fact_treatment_plan_items[
        "plan_item_count"
    ] = 1
    fact_treatment_plan_items[
        "accepted_item_count"
    ] = (
        fact_treatment_plan_items[
            "decision_status"
        ]
        .eq("accepted")
        .astype("int8")
    )
    fact_treatment_plan_items[
        "declined_item_count"
    ] = (
        fact_treatment_plan_items[
            "decision_status"
        ]
        .eq("declined")
        .astype("int8")
    )
    fact_treatment_plan_items[
        "pending_item_count"
    ] = (
        fact_treatment_plan_items[
            "decision_status"
        ]
        .eq("pending")
        .astype("int8")
    )
    fact_treatment_plan_items[
        "deferred_item_count"
    ] = (
        fact_treatment_plan_items[
            "decision_status"
        ]
        .eq("deferred")
        .astype("int8")
    )
    fact_treatment_plan_items[
        "decided_item_count"
    ] = (
        fact_treatment_plan_items[
            "decision_status"
        ]
        .ne("pending")
        .astype("int8")
    )

    fact_treatment_plan_items[
        "net_proposed_value"
    ] = (
        fact_treatment_plan_items[
            "proposed_fee_amount"
        ]
        - fact_treatment_plan_items[
            "proposed_discount_amount"
        ]
    ).round(2)
    fact_treatment_plan_items[
        "accepted_proposed_value"
    ] = (
        fact_treatment_plan_items[
            "net_proposed_value"
        ]
        * fact_treatment_plan_items[
            "accepted_item_count"
        ]
    ).round(2)
    fact_treatment_plan_items[
        "decided_proposed_value"
    ] = (
        fact_treatment_plan_items[
            "net_proposed_value"
        ]
        * fact_treatment_plan_items[
            "decided_item_count"
        ]
    ).round(2)

    link_numeric_columns = (
        "linked_procedure_count",
        "linked_completed_procedure_count",
        "linked_quantity",
        "linked_net_revenue",
    )

    for column_name in link_numeric_columns:
        fact_treatment_plan_items[
            column_name
        ] = fact_treatment_plan_items[
            column_name
        ].fillna(0)

    for column_name in (
        "linked_procedure_count",
        "linked_completed_procedure_count",
        "linked_quantity",
    ):
        fact_treatment_plan_items[
            column_name
        ] = fact_treatment_plan_items[
            column_name
        ].astype("int64")

    fact_treatment_plan_items[
        "linked_net_revenue"
    ] = fact_treatment_plan_items[
        "linked_net_revenue"
    ].round(2)

    fact_treatment_plan_items[
        "accepted_item_completed_count"
    ] = (
        fact_treatment_plan_items[
            "accepted_item_count"
        ].eq(1)
        & fact_treatment_plan_items[
            "linked_completed_procedure_count"
        ].gt(0)
    ).astype("int8")

    fact_treatment_plan_items[
        "decision_time_days"
    ] = (
        minutes_between(
            fact_treatment_plan_items[
                "decision_at"
            ],
            fact_treatment_plan_items[
                "proposed_at"
            ],
        )
        / (60 * 24)
    ).round(2)
    fact_treatment_plan_items[
        "days_to_first_completed_procedure"
    ] = (
        minutes_between(
            fact_treatment_plan_items[
                "first_linked_procedure_at"
            ],
            fact_treatment_plan_items[
                "decision_at"
            ],
        )
        / (60 * 24)
    ).round(2)

    fact_treatment_plan_items["valid_until"] = (
        fact_treatment_plan_items[
            "valid_until"
        ].dt.date
    )

    return fact_treatment_plan_items[
        [
            "plan_item_id",
            "plan_id",
            "patient_id",
            "proposed_by_dentist_id",
            "source_appointment_id",
            "procedure_code",
            "proposed_date_key",
            "decision_date_key",
            "valid_until_date_key",
            "first_linked_procedure_date_key",
            "proposed_at",
            "valid_until",
            "plan_status",
            "tooth_code",
            "sequence_order",
            "priority_level",
            "proposed_quantity",
            "proposed_fee_amount",
            "proposed_discount_amount",
            "net_proposed_value",
            "decision_status",
            "decision_at",
            "plan_item_count",
            "accepted_item_count",
            "declined_item_count",
            "pending_item_count",
            "deferred_item_count",
            "decided_item_count",
            "accepted_proposed_value",
            "decided_proposed_value",
            "decision_time_days",
            "linked_procedure_count",
            "linked_completed_procedure_count",
            "linked_quantity",
            "linked_net_revenue",
            "first_linked_procedure_at",
            "days_to_first_completed_procedure",
            "accepted_item_completed_count",
        ]
    ].copy()


def validate_fact_treatment_plan_items(
        datasets: dict[str, pd.DataFrame],
        dimensions: dict[str, pd.DataFrame],
        fact_appointments: pd.DataFrame,
        fact_treatment_plan_items: pd.DataFrame,
) -> None:
    if len(fact_treatment_plan_items) != len(
        datasets["treatment_plan_items"]
    ):
        raise ValueError(
            "Row-count mismatch for "
            "fact_treatment_plan_items."
        )

    optional_columns = (
        "source_appointment_id",
        "decision_date_key",
        "valid_until_date_key",
        "first_linked_procedure_date_key",
        "valid_until",
        "tooth_code",
        "decision_at",
        "decision_time_days",
        "first_linked_procedure_at",
        "days_to_first_completed_procedure",
    )
    validate_required_columns(
        fact_treatment_plan_items,
        tuple(
            column_name
            for column_name
            in fact_treatment_plan_items.columns
            if column_name not in optional_columns
        ),
        "fact_treatment_plan_items",
    )
    validate_primary_key(
        fact_treatment_plan_items,
        "plan_item_id",
        "fact_treatment_plan_items",
    )

    foreign_key_checks = (
        (
            "plan_id",
            datasets["treatment_plans"],
            "plan_id",
        ),
        (
            "patient_id",
            dimensions["dim_patients"],
            "patient_id",
        ),
        (
            "proposed_by_dentist_id",
            dimensions["dim_dentists"],
            "dentist_id",
        ),
        (
            "source_appointment_id",
            fact_appointments,
            "appointment_id",
        ),
        (
            "procedure_code",
            dimensions["dim_procedures"],
            "procedure_code",
        ),
    )

    for (
        child_column,
        parent_dataframe,
        parent_column,
    ) in foreign_key_checks:
        validate_foreign_key(
            fact_treatment_plan_items,
            child_column,
            parent_dataframe,
            parent_column,
            (
                "fact_treatment_plan_items."
                f"{child_column}"
            ),
        )

    for date_key_column in (
        "proposed_date_key",
        "decision_date_key",
        "valid_until_date_key",
        "first_linked_procedure_date_key",
    ):
        validate_foreign_key(
            fact_treatment_plan_items,
            date_key_column,
            dimensions["dim_date"],
            "date_key",
            (
                "fact_treatment_plan_items."
                f"{date_key_column}"
            ),
        )

    if fact_treatment_plan_items[
        "net_proposed_value"
    ].lt(0).any():
        raise ValueError(
            "Negative treatment-plan item "
            "values found."
        )

    for column_name in (
        "decision_time_days",
        "days_to_first_completed_procedure",
    ):
        if fact_treatment_plan_items[
            column_name
        ].dropna().lt(0).any():
            raise ValueError(
                f"Negative values found in "
                f"{column_name}."
            )

    linked_mask = fact_treatment_plan_items[
        "linked_procedure_count"
    ].gt(0)

    if fact_treatment_plan_items.loc[
        linked_mask,
        "accepted_item_count",
    ].ne(1).any():
        raise ValueError(
            "Non-accepted plan items are linked "
            "to performed procedures."
        )

    expected_linked_procedure_count = int(
        datasets["appointment_procedures"][
            "plan_item_id"
        ].notna().sum()
    )

    if fact_treatment_plan_items[
        "linked_procedure_count"
    ].sum() != expected_linked_procedure_count:
        raise ValueError(
            "Linked procedure counts do not "
            "reconcile to raw data."
        )

    expected_linked_net_revenue = (
        datasets["appointment_procedures"]
        .loc[
            lambda dataframe: (
                dataframe["plan_item_id"].notna()
            ),
            "fee_amount",
        ].sum()
        - datasets["appointment_procedures"]
        .loc[
            lambda dataframe: (
                dataframe["plan_item_id"].notna()
            ),
            "discount_amount",
        ].sum()
    )

    if abs(
        fact_treatment_plan_items[
            "linked_net_revenue"
        ].sum()
        - expected_linked_net_revenue
    ) > 0.01:
        raise ValueError(
            "Linked procedure revenue does not "
            "reconcile to raw data."
        )


def build_fact_payments(
        datasets: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    payments = datasets["payments"].copy()

    allocation_totals = (
        datasets["payment_allocations"]
        .groupby(
            "payment_id",
            as_index=False,
        )
        .agg(
            allocation_count=(
                "allocation_id",
                "size",
            ),
            allocated_amount_total=(
                "allocated_amount",
                "sum",
            ),
        )
    )

    fact_payments = payments.merge(
        allocation_totals,
        on="payment_id",
        how="left",
        validate="one_to_one",
    )

    fact_payments["received_date_key"] = (
        datetime_to_date_key(
            fact_payments["received_at"]
        )
    )
    fact_payments["transaction_count"] = 1
    fact_payments[
        "completed_transaction_count"
    ] = (
        fact_payments["payment_status"]
        .eq("completed")
        .astype("int8")
    )

    completed_mask = fact_payments[
        "payment_status"
    ].eq("completed")
    payment_mask = fact_payments[
        "transaction_type"
    ].eq("payment")
    deposit_mask = fact_payments[
        "transaction_type"
    ].eq("deposit")
    refund_mask = fact_payments[
        "transaction_type"
    ].eq("refund")
    inflow_mask = (
        completed_mask
        & (payment_mask | deposit_mask)
    )

    fact_payments[
        "completed_payment_count"
    ] = (
        completed_mask
        & payment_mask
    ).astype("int8")
    fact_payments[
        "completed_deposit_count"
    ] = (
        completed_mask
        & deposit_mask
    ).astype("int8")
    fact_payments[
        "completed_refund_count"
    ] = (
        completed_mask
        & refund_mask
    ).astype("int8")

    fact_payments[
        "completed_cash_inflow"
    ] = (
        fact_payments["amount"]
        .where(inflow_mask, 0)
        .round(2)
    )
    fact_payments[
        "completed_refund_amount"
    ] = (
        fact_payments["amount"]
        .where(
            completed_mask & refund_mask,
            0,
        )
        .round(2)
    )
    fact_payments["net_cash_amount"] = (
        fact_payments[
            "completed_cash_inflow"
        ]
        - fact_payments[
            "completed_refund_amount"
        ]
    ).round(2)

    fact_payments["allocation_count"] = (
        fact_payments["allocation_count"]
        .fillna(0)
        .astype("int64")
    )
    fact_payments[
        "allocated_amount_total"
    ] = (
        fact_payments[
            "allocated_amount_total"
        ]
        .fillna(0)
        .round(2)
    )
    fact_payments[
        "unallocated_inflow_amount"
    ] = (
        fact_payments["amount"]
        - fact_payments[
            "allocated_amount_total"
        ]
    ).where(
        inflow_mask,
        0,
    ).round(2)
    fact_payments[
        "has_unallocated_inflow_count"
    ] = (
        fact_payments[
            "unallocated_inflow_amount"
        ].gt(0.005)
    ).astype("int8")

    return fact_payments[
        [
            "payment_id",
            "patient_id",
            "received_date_key",
            "received_at",
            "transaction_type",
            "payment_arrangement",
            "payment_method",
            "payment_status",
            "reference_code",
            "amount",
            "transaction_count",
            "completed_transaction_count",
            "completed_payment_count",
            "completed_deposit_count",
            "completed_refund_count",
            "completed_cash_inflow",
            "completed_refund_amount",
            "net_cash_amount",
            "allocation_count",
            "allocated_amount_total",
            "unallocated_inflow_amount",
            "has_unallocated_inflow_count",
        ]
    ].copy()


def validate_fact_payments(
        datasets: dict[str, pd.DataFrame],
        dimensions: dict[str, pd.DataFrame],
        fact_payments: pd.DataFrame,
) -> None:
    if len(fact_payments) != len(
        datasets["payments"]
    ):
        raise ValueError(
            "Row-count mismatch for fact_payments."
        )

    validate_required_columns(
        fact_payments,
        tuple(
            column_name
            for column_name
            in fact_payments.columns
            if column_name != "reference_code"
        ),
        "fact_payments",
    )
    validate_primary_key(
        fact_payments,
        "payment_id",
        "fact_payments",
    )
    validate_foreign_key(
        fact_payments,
        "patient_id",
        dimensions["dim_patients"],
        "patient_id",
        "fact_payments.patient_id",
    )
    validate_foreign_key(
        fact_payments,
        "received_date_key",
        dimensions["dim_date"],
        "date_key",
        "fact_payments.received_date_key",
    )

    if fact_payments["amount"].le(0).any():
        raise ValueError(
            "Non-positive payment amounts found."
        )

    allocated_mask = fact_payments[
        "allocation_count"
    ].gt(0)
    eligible_allocation_mask = (
        fact_payments["payment_status"]
        .eq("completed")
        & fact_payments[
            "transaction_type"
        ].isin(
            [
                "payment",
                "deposit",
            ]
        )
    )

    if fact_payments.loc[
        allocated_mask,
    ].loc[
        ~eligible_allocation_mask[
            allocated_mask
        ]
    ].shape[0]:
        raise ValueError(
            "Allocations are linked to "
            "ineligible payment transactions."
        )

    if fact_payments[
        "unallocated_inflow_amount"
    ].lt(-0.005).any():
        raise ValueError(
            "Overallocated payment "
            "transactions found."
        )

    expected_allocation_count = len(
        datasets["payment_allocations"]
    )

    if fact_payments[
        "allocation_count"
    ].sum() != expected_allocation_count:
        raise ValueError(
            "Payment allocation counts do not "
            "reconcile to raw data."
        )

    expected_allocated_amount = datasets[
        "payment_allocations"
    ]["allocated_amount"].sum()

    if abs(
        fact_payments[
            "allocated_amount_total"
        ].sum()
        - expected_allocated_amount
    ) > 0.01:
        raise ValueError(
            "Payment allocated amounts do not "
            "reconcile to raw data."
        )

    completed_payments = datasets[
        "payments"
    ].loc[
        lambda dataframe: (
            dataframe["payment_status"]
            .eq("completed")
        )
    ]
    expected_net_cash = (
        completed_payments.loc[
            completed_payments[
                "transaction_type"
            ].isin(
                [
                    "payment",
                    "deposit",
                ]
            ),
            "amount",
        ].sum()
        - completed_payments.loc[
            completed_payments[
                "transaction_type"
            ].eq("refund"),
            "amount",
        ].sum()
    )

    if abs(
        fact_payments["net_cash_amount"].sum()
        - expected_net_cash
    ) > 0.01:
        raise ValueError(
            "Net cash does not reconcile to "
            "raw completed transactions."
        )


def build_fact_payment_allocations(
        datasets: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    payment_allocations = datasets[
        "payment_allocations"
    ].copy()

    payment_context = datasets["payments"][
        [
            "payment_id",
            "patient_id",
            "received_at",
            "transaction_type",
            "payment_arrangement",
            "payment_method",
            "payment_status",
        ]
    ].rename(
        columns={
            "patient_id": "payment_patient_id",
        }
    )

    procedure_context = datasets[
        "appointment_procedures"
    ][
        [
            "appointment_procedure_id",
            "appointment_id",
            "procedure_code",
            "completion_status",
        ]
    ].rename(
        columns={
            (
                "completion_status"
            ): "procedure_completion_status",
        }
    )

    appointment_context = datasets[
        "appointments"
    ][
        [
            "appointment_id",
            "patient_id",
            "dentist_id",
            "scheduled_start_at",
            "chair_end_at",
            "status",
        ]
    ].rename(
        columns={
            "patient_id": "service_patient_id",
            "status": "appointment_status",
        }
    )

    fact_payment_allocations = (
        payment_allocations
        .merge(
            payment_context,
            on="payment_id",
            how="left",
            validate="many_to_one",
        )
        .merge(
            procedure_context,
            on="appointment_procedure_id",
            how="left",
            validate="many_to_one",
        )
        .merge(
            appointment_context,
            on="appointment_id",
            how="left",
            validate="many_to_one",
        )
    )

    fact_payment_allocations[
        "patient_id"
    ] = fact_payment_allocations[
        "payment_patient_id"
    ]
    fact_payment_allocations[
        "payment_received_date_key"
    ] = datetime_to_date_key(
        fact_payment_allocations["received_at"]
    )
    fact_payment_allocations[
        "service_date_key"
    ] = datetime_to_date_key(
        fact_payment_allocations[
            "scheduled_start_at"
        ]
    )
    fact_payment_allocations[
        "procedure_completed_at"
    ] = fact_payment_allocations[
        "chair_end_at"
    ]
    fact_payment_allocations[
        "allocation_count"
    ] = 1
    fact_payment_allocations[
        "days_from_procedure_completion_to_payment"
    ] = (
        minutes_between(
            fact_payment_allocations[
                "received_at"
            ],
            fact_payment_allocations[
                "procedure_completed_at"
            ],
        )
        / (60 * 24)
    ).round(2)

    before_completion_mask = (
        fact_payment_allocations["received_at"]
        < fact_payment_allocations[
            "procedure_completed_at"
        ]
    )
    same_day_mask = (
        fact_payment_allocations[
            "received_at"
        ].dt.normalize()
        == fact_payment_allocations[
            "procedure_completed_at"
        ].dt.normalize()
    )
    same_day_after_completion_mask = (
        ~before_completion_mask
        & same_day_mask
    )
    after_service_date_mask = (
        ~before_completion_mask
        & ~same_day_mask
    )

    fact_payment_allocations[
        "before_completion_allocation_count"
    ] = before_completion_mask.astype("int8")
    fact_payment_allocations[
        "same_day_after_completion_allocation_count"
    ] = same_day_after_completion_mask.astype(
        "int8"
    )
    fact_payment_allocations[
        "after_service_date_allocation_count"
    ] = after_service_date_mask.astype("int8")

    payment_timing_group = pd.Series(
        "after_service_date",
        index=fact_payment_allocations.index,
        dtype="string",
    )
    payment_timing_group.loc[
        before_completion_mask
    ] = "before_procedure_completion"
    payment_timing_group.loc[
        same_day_after_completion_mask
    ] = "same_day_after_completion"
    fact_payment_allocations[
        "payment_timing_group"
    ] = payment_timing_group

    return fact_payment_allocations[
        [
            "allocation_id",
            "payment_id",
            "appointment_procedure_id",
            "appointment_id",
            "patient_id",
            "dentist_id",
            "procedure_code",
            "payment_received_date_key",
            "service_date_key",
            "received_at",
            "procedure_completed_at",
            "transaction_type",
            "payment_arrangement",
            "payment_method",
            "payment_status",
            "procedure_completion_status",
            "payment_timing_group",
            "allocation_count",
            "allocated_amount",
            "days_from_procedure_completion_to_payment",
            "before_completion_allocation_count",
            "same_day_after_completion_allocation_count",
            "after_service_date_allocation_count",
        ]
    ].copy()


def validate_fact_payment_allocations(
        datasets: dict[str, pd.DataFrame],
        dimensions: dict[str, pd.DataFrame],
        fact_appointments: pd.DataFrame,
        fact_procedures: pd.DataFrame,
        fact_payments: pd.DataFrame,
        fact_payment_allocations: pd.DataFrame,
) -> None:
    if len(fact_payment_allocations) != len(
        datasets["payment_allocations"]
    ):
        raise ValueError(
            "Row-count mismatch for "
            "fact_payment_allocations."
        )

    validate_required_columns(
        fact_payment_allocations,
        tuple(
            fact_payment_allocations.columns
        ),
        "fact_payment_allocations",
    )
    validate_primary_key(
        fact_payment_allocations,
        "allocation_id",
        "fact_payment_allocations",
    )

    foreign_key_checks = (
        (
            "payment_id",
            fact_payments,
            "payment_id",
        ),
        (
            "appointment_procedure_id",
            fact_procedures,
            "appointment_procedure_id",
        ),
        (
            "appointment_id",
            fact_appointments,
            "appointment_id",
        ),
        (
            "patient_id",
            dimensions["dim_patients"],
            "patient_id",
        ),
        (
            "dentist_id",
            dimensions["dim_dentists"],
            "dentist_id",
        ),
        (
            "procedure_code",
            dimensions["dim_procedures"],
            "procedure_code",
        ),
    )

    for (
        child_column,
        parent_dataframe,
        parent_column,
    ) in foreign_key_checks:
        validate_foreign_key(
            fact_payment_allocations,
            child_column,
            parent_dataframe,
            parent_column,
            (
                "fact_payment_allocations."
                f"{child_column}"
            ),
        )

    for date_key_column in (
        "payment_received_date_key",
        "service_date_key",
    ):
        validate_foreign_key(
            fact_payment_allocations,
            date_key_column,
            dimensions["dim_date"],
            "date_key",
            (
                "fact_payment_allocations."
                f"{date_key_column}"
            ),
        )

    if fact_payment_allocations[
        "allocated_amount"
    ].le(0).any():
        raise ValueError(
            "Non-positive payment allocations found."
        )

    eligible_payment_mask = (
        fact_payment_allocations[
            "payment_status"
        ].eq("completed")
        & fact_payment_allocations[
            "transaction_type"
        ].isin(
            [
                "payment",
                "deposit",
            ]
        )
    )

    if not eligible_payment_mask.all():
        raise ValueError(
            "Ineligible payment transactions "
            "found in payment allocations."
        )

    source_patient_check = (
        datasets["payment_allocations"]
        .merge(
            datasets["payments"][
                [
                    "payment_id",
                    "patient_id",
                ]
            ],
            on="payment_id",
            validate="many_to_one",
        )
        .merge(
            datasets["appointment_procedures"][
                [
                    "appointment_procedure_id",
                    "appointment_id",
                ]
            ],
            on="appointment_procedure_id",
            validate="many_to_one",
        )
        .merge(
            datasets["appointments"][
                [
                    "appointment_id",
                    "patient_id",
                ]
            ],
            on="appointment_id",
            validate="many_to_one",
            suffixes=(
                "_payment",
                "_service",
            ),
        )
    )

    if source_patient_check[
        "patient_id_payment"
    ].ne(
        source_patient_check[
            "patient_id_service"
        ]
    ).any():
        raise ValueError(
            "Payment and service patient "
            "identifiers do not match."
        )

    timing_count_total = fact_payment_allocations[
        [
            "before_completion_allocation_count",
            (
                "same_day_after_completion_"
                "allocation_count"
            ),
            "after_service_date_allocation_count",
        ]
    ].sum(axis=1)

    if not timing_count_total.eq(1).all():
        raise ValueError(
            "Invalid payment timing groups found."
        )

    expected_allocated_amount = datasets[
        "payment_allocations"
    ]["allocated_amount"].sum()

    reconciled_amounts = (
        fact_payment_allocations[
            "allocated_amount"
        ].sum(),
        fact_procedures[
            "allocated_amount_total"
        ].sum(),
        fact_payments[
            "allocated_amount_total"
        ].sum(),
    )

    if any(
        abs(
            amount
            - expected_allocated_amount
        ) > 0.01
        for amount in reconciled_amounts
    ):
        raise ValueError(
            "Payment allocations do not "
            "reconcile across processed facts."
        )


def write_processed_datasets(
        processed_datasets: dict[str, pd.DataFrame],
        output_dir: Path,
        file_names: dict[str, str],
) -> None:
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    for dataset_name, csv_name in file_names.items():
        dataframe = processed_datasets[dataset_name]
        output_path = output_dir / csv_name

        dataframe.to_csv(
            output_path,
            index=False,
        )

        print(
            f"Wrote {csv_name}: "
            f"{len(dataframe):,} rows"
        )


def validate_written_datasets(
        processed_datasets: dict[str, pd.DataFrame],
        output_dir: Path,
        file_names: dict[str, str],
) -> None:
    expected_csv_names = set(
        file_names.values()
    )
    actual_csv_names = {
        path.name
        for path in output_dir.glob("*.csv")
    }

    missing_csv_names = sorted(
        expected_csv_names - actual_csv_names
    )
    unexpected_csv_names = sorted(
        actual_csv_names - expected_csv_names
    )

    if missing_csv_names or unexpected_csv_names:
        raise ValueError(
            "Processed output file mismatch. "
            f"Missing: {missing_csv_names}. "
            f"Unexpected: {unexpected_csv_names}."
        )

    for dataset_name, csv_name in file_names.items():
        expected_dataframe = processed_datasets[
            dataset_name
        ]
        written_dataframe = pd.read_csv(
            output_dir / csv_name,
        )

        if (
            written_dataframe.columns.tolist()
            != expected_dataframe.columns.tolist()
        ):
            raise ValueError(
                f"Written column mismatch in "
                f"{csv_name}."
            )

        if len(written_dataframe) != len(
            expected_dataframe
        ):
            raise ValueError(
                f"Written row-count mismatch in "
                f"{csv_name}."
            )

    print(
        "Validated written CSV files: "
        f"{len(file_names)} datasets"
    )


def main() -> None:
    args = parse_args()
    datasets = read_raw_datasets(args.raw_dir)

    for spec in RAW_DATASET_SPECS:
        print(
            f"Read {spec.csv_name}: "
            f"{len(datasets[spec.name]):,} rows"
        )

    print()
    dimensions = build_dimensions(datasets)
    validate_dimensions(
        datasets,
        dimensions,
    )
    write_processed_datasets(
        dimensions,
        args.output_dir,
        DIMENSION_FILE_NAMES,
    )

    print()
    fact_appointments = build_fact_appointments(
        datasets,
    )
    validate_fact_appointments(
        datasets,
        dimensions,
        fact_appointments,
    )
    write_processed_datasets(
        {
            "fact_appointments": (
                fact_appointments
            ),
        },
        args.output_dir,
        APPOINTMENT_FACT_FILE_NAMES,
    )

    print()
    fact_procedures = build_fact_procedures(
        datasets,
    )
    validate_fact_procedures(
        datasets,
        dimensions,
        fact_appointments,
        fact_procedures,
    )
    write_processed_datasets(
        {
            "fact_procedures": fact_procedures,
        },
        args.output_dir,
        PROCEDURE_FACT_FILE_NAMES,
    )

    print()
    fact_treatment_plan_items = (
        build_fact_treatment_plan_items(
            datasets,
        )
    )
    validate_fact_treatment_plan_items(
        datasets,
        dimensions,
        fact_appointments,
        fact_treatment_plan_items,
    )
    write_processed_datasets(
        {
            "fact_treatment_plan_items": (
                fact_treatment_plan_items
            ),
        },
        args.output_dir,
        TREATMENT_PLAN_ITEM_FACT_FILE_NAMES,
    )

    print()
    fact_payments = build_fact_payments(
        datasets,
    )
    validate_fact_payments(
        datasets,
        dimensions,
        fact_payments,
    )
    write_processed_datasets(
        {
            "fact_payments": fact_payments,
        },
        args.output_dir,
        PAYMENT_FACT_FILE_NAMES,
    )

    print()
    fact_payment_allocations = (
        build_fact_payment_allocations(
            datasets,
        )
    )
    validate_fact_payment_allocations(
        datasets,
        dimensions,
        fact_appointments,
        fact_procedures,
        fact_payments,
        fact_payment_allocations,
    )
    write_processed_datasets(
        {
            "fact_payment_allocations": (
                fact_payment_allocations
            ),
        },
        args.output_dir,
        PAYMENT_ALLOCATION_FACT_FILE_NAMES,
    )

    print()
    processed_datasets = {
        **dimensions,
        "fact_appointments": fact_appointments,
        "fact_procedures": fact_procedures,
        "fact_treatment_plan_items": (
            fact_treatment_plan_items
        ),
        "fact_payments": fact_payments,
        "fact_payment_allocations": (
            fact_payment_allocations
        ),
    }
    processed_file_names = {
        **DIMENSION_FILE_NAMES,
        **APPOINTMENT_FACT_FILE_NAMES,
        **PROCEDURE_FACT_FILE_NAMES,
        **TREATMENT_PLAN_ITEM_FACT_FILE_NAMES,
        **PAYMENT_FACT_FILE_NAMES,
        **PAYMENT_ALLOCATION_FACT_FILE_NAMES,
    }
    validate_written_datasets(
        processed_datasets,
        args.output_dir,
        processed_file_names,
    )

    print()
    print(
        "All processed analytical datasets "
        "built and "
        "validated successfully."
    )


if __name__ == "__main__":
    main()
