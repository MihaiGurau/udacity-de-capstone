"""
This is a boilerplate pipeline 'data_engineering'
generated using Kedro 0.18.8
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import (
    dq_population_node,
    extract_population_node,
    transform_population_node,
)


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=extract_population_node,
                inputs="raw_census_population",
                outputs="census_population",
                name="extract_population",
                tags="population",
            ),
            node(
                func=transform_population_node,
                inputs="census_population",
                outputs="census_population_clean",
                name="transform_population",
                tags="population",
            ),
            node(
                func=dq_population_node,
                inputs="census_population_clean",
                outputs="census_population_validated",
                name="validate_population",
                tags="population",
            ),
        ]
    )
