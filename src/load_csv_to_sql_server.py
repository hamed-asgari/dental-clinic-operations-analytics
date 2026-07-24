"""Load synthetic dental-clinic CSV files into SQL Server."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pyodbc


@dataclass(frozen=True)
class TableSpec:
    csv_name: str
    table_name: str
    columns: tuple[str, ...]
    string_columns: tuple[str, ...] = ()
    integer_columns: tuple[str, ...] = ()
    numeric_columns: tuple[str, ...] = ()
    boolean_columns: tuple[str, ...] = ()
    datetime_columns: tuple[str, ...] = ()
    date_columns: tuple[str, ...] = ()


TABLE_SPECS = (
    TableSpec(
        csv_name="patients.csv",
        table_name="Patients",
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
        string_columns=(
            "sex",
            "city_area",
            "insurance_type",
            "referral_source",
            "preferred_contact_channel",
            "patient_status",
        ),
        integer_columns=(
            "patient_id",
            "birth_year",
        ),
        datetime_columns=(
            "registered_at",
        ),
    ),
    TableSpec(
        csv_name="dentists.csv",
        table_name="Dentists",
        columns=(
            "dentist_id",
            "dentist_role",
            "engagement_type",
            "start_date",
            "end_date",
            "scheduled_hours_weekly",
            "active",
        ),
        string_columns=(
            "dentist_role",
            "engagement_type",
        ),
        integer_columns=(
            "dentist_id",
        ),
        numeric_columns=(
            "scheduled_hours_weekly",
        ),
        boolean_columns=(
            "active",
        ),
        date_columns=(
            "start_date",
            "end_date",
        ),
    ),
    TableSpec(
        csv_name="procedure_catalog.csv",
        table_name="ProcedureCatalog",
        columns=(
            "procedure_code",
            "procedure_name",
            "procedure_group",
            "default_planned_duration_min",
            "standard_fee_amount",
            "standard_direct_cost",
            "active",
        ),
        string_columns=(
            "procedure_code",
            "procedure_name",
            "procedure_group",
        ),
        integer_columns=(
            "default_planned_duration_min",
        ),
        numeric_columns=(
            "standard_fee_amount",
            "standard_direct_cost",
        ),
        boolean_columns=(
            "active",
        ),
    ),
    TableSpec(
        csv_name="appointments.csv",
        table_name="Appointments",
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
        string_columns=(
            "visit_type",
            "booking_channel",
            "status",
            "status_change_reason",
        ),
        integer_columns=(
            "appointment_id",
            "patient_id",
            "dentist_id",
            "planned_duration_min",
            "rescheduled_from_appointment_id",
        ),
        boolean_columns=(
            "reminder_sent",
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
    TableSpec(
        csv_name="treatment_plans.csv",
        table_name="TreatmentPlans",
        columns=(
            "plan_id",
            "patient_id",
            "proposed_by_dentist_id",
            "source_appointment_id",
            "proposed_at",
            "plan_status",
            "valid_until",
        ),
        string_columns=(
            "plan_status",
        ),
        integer_columns=(
            "plan_id",
            "patient_id",
            "proposed_by_dentist_id",
            "source_appointment_id",
        ),
        datetime_columns=(
            "proposed_at",
        ),
        date_columns=(
            "valid_until",
        ),
    ),
    TableSpec(
        csv_name="treatment_plan_items.csv",
        table_name="TreatmentPlanItems",
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
        string_columns=(
            "procedure_code",
            "tooth_code",
            "priority_level",
            "decision_status",
        ),
        integer_columns=(
            "plan_item_id",
            "plan_id",
            "sequence_order",
            "proposed_quantity",
        ),
        numeric_columns=(
            "proposed_fee_amount",
            "proposed_discount_amount",
        ),
        datetime_columns=(
            "decision_at",
        ),
    ),
    TableSpec(
        csv_name="appointment_procedures.csv",
        table_name="AppointmentProcedures",
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
        string_columns=(
            "procedure_code",
            "tooth_code",
            "completion_status",
        ),
        integer_columns=(
            "appointment_procedure_id",
            "appointment_id",
            "plan_item_id",
            "quantity",
        ),
        numeric_columns=(
            "fee_amount",
            "discount_amount",
            "direct_cost",
        ),
    ),
    TableSpec(
        csv_name="payments.csv",
        table_name="Payments",
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
        string_columns=(
            "transaction_type",
            "payment_arrangement",
            "payment_method",
            "payment_status",
            "reference_code",
            "notes",
        ),
        integer_columns=(
            "payment_id",
            "patient_id",
        ),
        numeric_columns=(
            "amount",
        ),
        datetime_columns=(
            "received_at",
        ),
    ),
    TableSpec(
        csv_name="payment_allocations.csv",
        table_name="PaymentAllocations",
        columns=(
            "allocation_id",
            "payment_id",
            "appointment_procedure_id",
            "allocated_amount",
        ),
        integer_columns=(
            "allocation_id",
            "payment_id",
            "appointment_procedure_id",
        ),
        numeric_columns=(
            "allocated_amount",
        ),
    ),
)

DELETE_ORDER = (
    "PaymentAllocations",
    "Payments",
    "AppointmentProcedures",
    "TreatmentPlanItems",
    "TreatmentPlans",
    "Appointments",
    "ProcedureCatalog",
    "Dentists",
    "Patients",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
    )

    parser.add_argument(
        "--server",
        default="localhost",
    )

    parser.add_argument(
        "--database",
        default="DentalClinicAnalytics_Test",
    )

    parser.add_argument(
        "--driver",
        default="ODBC Driver 17 for SQL Server",
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/raw"),
    )

    return parser.parse_args()


def build_connection_string(
        server: str,
        database: str,
        driver: str,
) -> str:
    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )


def normalize_boolean_column(
        series: pd.Series,
        column_name: str,
) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.astype("boolean")

    normalized = (
        series.astype("string")
        .str.strip()
        .str.lower()
    )

    mapped = normalized.map(
        {
            "true": True,
            "false": False,
            "1": True,
            "0": False,
        }
    )

    invalid_mask = (
            series.notna()
            & mapped.isna()
    )

    if invalid_mask.any():
        invalid_values = (
            series.loc[invalid_mask]
            .astype(str)
            .unique()
            .tolist()
        )

        raise ValueError(
            f"Invalid boolean values in "
            f"{column_name}: {invalid_values}"
        )

    return mapped.astype("boolean")


def read_dataset(
        data_dir: Path,
        spec: TableSpec,
) -> pd.DataFrame:
    csv_path = data_dir / spec.csv_name

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {csv_path}"
        )

    dtype_map = {
        column: "string"
        for column in spec.string_columns
    }

    dataframe = pd.read_csv(
        csv_path,
        dtype=dtype_map,
        keep_default_na=True,
    )

    expected_columns = set(spec.columns)
    actual_columns = set(dataframe.columns)

    missing_columns = sorted(
        expected_columns - actual_columns
    )

    unexpected_columns = sorted(
        actual_columns - expected_columns
    )

    if missing_columns or unexpected_columns:
        raise ValueError(
            f"Column mismatch in {spec.csv_name}. "
            f"Missing: {missing_columns}. "
            f"Unexpected: {unexpected_columns}."
        )

    dataframe = dataframe.loc[
        :,
        list(spec.columns),
    ].copy()

    for column in spec.integer_columns:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="raise",
        ).astype("Int64")

    for column in spec.numeric_columns:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="raise",
        )

    for column in spec.boolean_columns:
        dataframe[column] = (
            normalize_boolean_column(
                dataframe[column],
                column,
            )
        )

    for column in spec.datetime_columns:
        dataframe[column] = pd.to_datetime(
            dataframe[column],
            errors="raise",
        )

    for column in spec.date_columns:
        dataframe[column] = pd.to_datetime(
            dataframe[column],
            errors="raise",
        ).dt.date

    return dataframe


def convert_to_python_value(
        value: object,
) -> object:
    if value is None or value is pd.NA:
        return None

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    if isinstance(value, np.generic):
        return value.item()

    return value


def dataframe_to_rows(
        dataframe: pd.DataFrame,
) -> list[tuple[object, ...]]:
    return [
        tuple(
            convert_to_python_value(value)
            for value in row
        )
        for row in dataframe.itertuples(
            index=False,
            name=None,
        )
    ]


def clear_existing_data(
        cursor: pyodbc.Cursor,
) -> None:
    for table_name in DELETE_ORDER:
        cursor.execute(
            f"DELETE FROM dbo.[{table_name}];"
        )


def insert_dataframe(
        cursor: pyodbc.Cursor,
        spec: TableSpec,
        dataframe: pd.DataFrame,
) -> None:
    column_sql = ", ".join(
        f"[{column}]"
        for column in spec.columns
    )

    placeholder_sql = ", ".join(
        "?"
        for _ in spec.columns
    )

    insert_sql = (
        f"INSERT INTO dbo.[{spec.table_name}] "
        f"({column_sql}) "
        f"VALUES ({placeholder_sql});"
    )

    rows = dataframe_to_rows(dataframe)

    cursor.fast_executemany = True
    cursor.executemany(
        insert_sql,
        rows,
    )


def main() -> None:
    args = parse_args()

    if not args.data_dir.exists():
        raise FileNotFoundError(
            f"Data directory not found: "
            f"{args.data_dir}"
        )

    connection_string = (
        build_connection_string(
            server=args.server,
            database=args.database,
            driver=args.driver,
        )
    )

    loaded_counts: dict[str, int] = {}

    connection = pyodbc.connect(
        connection_string,
        autocommit=False,
    )

    try:
        cursor = connection.cursor()

        clear_existing_data(cursor)

        for spec in TABLE_SPECS:
            dataframe = read_dataset(
                args.data_dir,
                spec,
            )

            insert_dataframe(
                cursor,
                spec,
                dataframe,
            )

            loaded_counts[
                spec.table_name
            ] = len(dataframe)

            print(
                f"Loaded {spec.table_name}: "
                f"{len(dataframe):,} rows"
            )

        for spec in TABLE_SPECS:
            cursor.execute(
                f"SELECT COUNT(*) "
                f"FROM dbo.[{spec.table_name}];"
            )

            database_count = int(
                cursor.fetchone()[0]
            )

            expected_count = loaded_counts[
                spec.table_name
            ]

            if database_count != expected_count:
                raise RuntimeError(
                    f"Row-count mismatch for "
                    f"{spec.table_name}: "
                    f"expected {expected_count}, "
                    f"found {database_count}."
                )

        connection.commit()

        print()
        print(
            "All datasets loaded and "
            "validated successfully."
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()
