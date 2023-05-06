"""
This is a boilerplate pipeline 'data_engineering'
generated using Kedro 0.18.8
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import extract_population_node, transform_population_node


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=extract_population_node,
                inputs="census_population",
                outputs="census_population_df",
                name="extract_population",
            ),
            node(
                func=transform_population_node,
                inputs="census_population_df",
                outputs="census_population_transformed",
                name="transform_population",
            ),
        ]
    )
