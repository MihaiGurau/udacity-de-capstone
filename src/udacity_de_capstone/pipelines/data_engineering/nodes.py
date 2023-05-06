"""
This is a boilerplate pipeline 'data_engineering'
generated using Kedro 0.18.8
"""

import polars as pl
import requests
from udacity_de_capstone.utils import format_column_names


def extract_population_node(response: requests.Response) -> pl.DataFrame:
    """Loads population data from the US Census API"""
    data = response.json()
    return pl.from_records(data[1:], schema=data[0])


def transform_population_node(population: pl.DataFrame) -> pl.DataFrame:
    """
    Performs type casts, column cleaning, renaming, and sorting on population data
    """
    df = (
        population.rename({"POP_2021": "POPULATION", "LASTUPDATE": "LAST_UPDATE_DATE"})
        .with_columns(
            pl.col("LAST_UPDATE_DATE").str.to_date(r"%B. %d, %Y"),
            pl.col("POPULATION").cast(pl.Int64),
        )
        .drop("state")
        .sort(by="NAME")
    )
    df.columns = format_column_names(df.columns)
    return df
