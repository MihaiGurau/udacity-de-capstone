"""
This is a boilerplate pipeline 'data_engineering'
generated using Kedro 0.18.8
"""

import logging
from typing import Callable, Dict

import polars as pl
import requests
from udacity_de_capstone.utils import (
    format_column_names,
    rich_error_wrapper,
    rich_success_wrapper,
)

log = logging.getLogger(__name__)


def _run_generic_dq(df: pl.DataFrame) -> None:
    """Common data quality checks for the project's datasets"""
    # check that we have at least one value
    if df.is_empty():
        err = "Empty DataFrame!"
        log.error(rich_error_wrapper(err), extra={"markup": True})
        raise ValueError(err)

    # check for valid latitudes
    if not df["latitude"].is_between(-90, 90).all():
        err = "Latitutes outside [-90, 90] degrees range found!"
        log.error(rich_error_wrapper(err), extra={"markup": True})
        raise ValueError(err)

    # check for valid longitudes
    if not df["longitude"].is_between(-180, 180).all():
        err = "Longitudes outside [-180, 180] degrees range found!"
        log.error(rich_error_wrapper(err), extra={"markup": True})
        raise ValueError(err)

    # check that we don't have any duplicates
    if df.is_duplicated().any():
        err = "Duplicate airport entries found!"
        log.error(rich_error_wrapper(err), extra={"markup": True})
        raise ValueError(err)


def transform_population(response: requests.Response) -> pl.DataFrame:
    """
    Loads population data and
    performs type casts, column cleaning, renaming, and sorting
    """

    data = response.json()
    population = pl.from_records(data[1:], schema=data[0])
    population = (
        population.rename({"POP_2021": "POPULATION", "LASTUPDATE": "LAST_UPDATE_DATE"})
        .with_columns(
            pl.col("LAST_UPDATE_DATE").str.to_date(r"%B. %d, %Y"),
            pl.col("POPULATION").cast(pl.Int64),
        )
        .drop("state")
        .sort("NAME")
    )
    population.columns = format_column_names(population.columns)
    return population


def dq_population(population: pl.DataFrame) -> pl.DataFrame:
    """Runs data quality checks on population data"""
    # check for negative population values
    if not population.filter(pl.col("population") < 0).is_empty():
        err = "Negative population values found"
        log.error(err)
        raise ValueError(err)
    else:
        log.info(
            rich_success_wrapper("All DQ checks on population data passed!"),
            extra={"markup": True},
        )

    return population


def transform_airports(airports: pl.DataFrame) -> pl.DataFrame:
    """Basic transformations for airports"""
    df = airports.with_columns(pl.col("AIRPORT").cast(pl.Categorical)).drop(
        "DISPLAY_AIRPORT_CITY_NAME_FULL",
        "FAA",
    )
    df.columns = format_column_names(df.columns)
    return df


def combine_flight_state_population(
    flights: Dict[str, Callable[[], pl.DataFrame]],
    airports: pl.DataFrame,
    population: pl.DataFrame,
) -> pl.DataFrame:
    """Enrich the flight data with population figures on state level.
    This is simply done to allow for easier analysis later of combined datasets.
    """
    output: Dict[str, pl.DataFrame] = {}
    for partition_id, load_flights in flights.items():
        # load partitioned data
        flight_data = load_flights()

        # create lazy versions of polars dataframes
        ldf_airports = airports.lazy()
        ldf_population = population.lazy()

        # rename partition for output (kinda ugly...)
        new_partition_id = f"combined{partition_id[partition_id.rfind('_', 0, partition_id.rfind('_')):]}"

        # apply joins and keep only needed columns
        output[new_partition_id] = (
            flight_data.limit(10)
            .lazy()
            .join(
                ldf_airports.select(
                    pl.col("airport"),
                    pl.col("airport_state_name").alias("origin_state_name"),
                    pl.col("airport_state_code").alias("origin_state_code"),
                ),
                left_on="origin",
                right_on="airport",
                how="inner",
            )
            .join(
                ldf_airports.select(
                    pl.col("airport"),
                    pl.col("airport_state_name").alias("destination_state_name"),
                    pl.col("airport_state_code").alias("destination_state_code"),
                ),
                left_on="destination",
                right_on="airport",
                how="inner",
            )
            .join(
                ldf_population.select(
                    pl.col("name").alias("origin_state_name"),
                    pl.col("population").alias("origin_state_population"),
                ),
                on="origin_state_name",
                how="inner",
            )
            .join(
                ldf_population.select(
                    pl.col("name").alias("destination_state_name"),
                    pl.col("population").alias("destination_state_population"),
                ),
                on="destination_state_name",
                how="inner",
            )
            .collect()
        )

    return output


def dq_airports(airports: pl.DataFrame) -> pl.DataFrame:
    """Data quality checks for airports"""
    # first run all generic checks
    _run_generic_dq(airports)

    # check for any null values
    null_counts = airports.null_count()
    if sum(null_counts.row(0)) != 0:
        print(null_counts.transpose(include_header=True, column_names=["null_count"]))
        err = "Detected null values!"
        log.error(rich_error_wrapper(err), extra={"markup": True})
        raise ValueError(err)

    log.info(
        rich_success_wrapper("All DQ checks on airports data passed!"),
        extra={"markup": True},
    )

    return airports


def transform_flights(flights: pl.DataFrame) -> Dict[str, pl.DataFrame]:
    """Initial transformation of flight data"""

    size_unit = "gb"
    size_raw = flights.estimated_size(unit=size_unit)
    log.info(f"Raw flights dataset size: {size_raw:.2f} GB")
    log.info(f"Records: {flights.shape[0]:,}")

    df = (
        flights.lazy()
        .with_columns(
            pl.col("FL_DATE").str.to_date(),
            pl.col("MKT_UNIQUE_CARRIER").cast(pl.Categorical),
            pl.col("MKT_CARRIER_FL_NUM").cast(str).str.zfill(4),
            pl.col("OP_UNIQUE_CARRIER").cast(pl.Categorical),
            pl.col("OP_CARRIER_FL_NUM").cast(str).str.zfill(4),
            pl.col("DEP_TIME").str.to_datetime(),
            pl.col("CRS_DEP_TIME").str.to_datetime(),
            pl.col("MANUFACTURER").cast(pl.Categorical),
            pl.col("ICAO TYPE").cast(pl.Categorical).alias("ICAO_TYPE"),
            pl.col("RANGE").cast(pl.Categorical),
            pl.col("WIDTH").cast(pl.Categorical),
            pl.col("LOW_LEVEL_CLOUD").cast(pl.Boolean),
            pl.col("MID_LEVEL_CLOUD").cast(pl.Boolean),
            pl.col("HIGH_LEVEL_CLOUD").cast(pl.Boolean),
        )
        .rename({"DEST": "DESTINATION"})
        .drop("ICAO TYPE")
        .collect()
    )

    # log size changes post dtype application
    size_parsed = df.estimated_size(unit=size_unit)
    size_diff_pct = (size_parsed - size_raw) / size_raw
    log.info(f"Parsed flights dataset size: {size_parsed:.2f} GB")
    log.info(f"Percentage size difference post dtype application: {size_diff_pct:.2%}")

    # perform column name formatting
    df.columns = format_column_names(df.columns)

    # partition by flight year and month
    p_key = "year_month"
    partitions = df.with_columns(
        pl.col("fl_date").dt.strftime("%Y_%m").alias(p_key),
    ).partition_by(p_key, as_dict=True)

    # remove partitioning column
    for p in partitions.values():
        _ = p.drop_in_place(p_key)

    # rename partition keys
    old_keys = list(partitions.keys())
    new_keys = (f"flights_{x}" for x in old_keys)
    for old_key, new_key in zip(old_keys, new_keys):
        partitions[new_key] = partitions.pop(old_key)

    return partitions


def dq_flights(
    flights: Dict[str, Callable[[], pl.DataFrame]]
) -> Dict[str, pl.DataFrame]:
    """Perform quality checks on flight data"""

    for year_month, data_func in flights.items():
        # first load the data for the currently processed partition
        data = data_func()

        # run all generic checks
        _run_generic_dq(data)

        # check for null values in specific columns
        cols_for_null_checks = [
            "fl_date",
            "origin",
            "destination",
            "op_unique_carrier",
            "mkt_unique_carrier",
        ]
        null_counts = data.select(cols_for_null_checks).null_count()
        if sum(null_counts.row(0)) != 0:
            err = (
                f"Null values for relevant columns detected in {year_month} partition!"
                " (printing at most 5 of them)"
            )
            log.error(rich_error_wrapper(err), extra={"markup": True})
            raise ValueError(err)

    # return unchanged data if all checks passed
    log.info(
        rich_success_wrapper("All DQ checks on flights data passed!"),
        extra={"markup": True},
    )

    return flights
