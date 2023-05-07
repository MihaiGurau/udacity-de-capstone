"""
This is a boilerplate pipeline 'data_engineering'
generated using Kedro 0.18.8
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import (
    dq_airports,
    dq_population,
    extract_population,
    transform_airports,
    transform_flights,
    transform_population,
)


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=extract_population,
                inputs="raw_census_population",
                outputs="census_population",
                name="extract_population",
                tags="population",
            ),
            node(
                func=transform_population,
                inputs="census_population",
                outputs="census_population_clean",
                name="transform_population",
                tags="population",
            ),
            node(
                func=dq_population,
                inputs="census_population_clean",
                outputs="census_population_validated",
                name="validate_population",
                tags="population",
            ),
            node(
                func=transform_airports,
                inputs="airports",
                outputs="airports_transformed",
                name="transform_airports",
                tags="flights",
            ),
            node(
                func=dq_airports,
                inputs="airports_transformed",
                outputs="airports_validated",
                name="validate_airports",
                tags="flights",
            ),
            node(
                func=transform_flights,
                inputs="flights",
                outputs="flights_transformed",
                name="transform_flights",
                tags="flights",
            ),
        ]
    )
