"""
This is a boilerplate pipeline 'data_engineering'
generated using Kedro 0.18.8
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import (
    agg_by_departure_airport,
    agg_by_op_carrier,
    agg_by_state,
    combine_all_data,
    dq_airports,
    dq_flights,
    dq_population,
    transform_airports,
    transform_flights,
    transform_population,
)


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=transform_population,
                inputs="raw_population",
                outputs="population_transformed",
                name="transform_population",
                tags="population",
            ),
            node(
                func=dq_population,
                inputs="population_transformed",
                outputs="population_validated",
                name="validate_population",
                tags="population",
            ),
            node(
                func=transform_airports,
                inputs="raw_airports",
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
                inputs="raw_flights",
                outputs="flights_transformed",
                name="transform_flights",
                tags="flights",
            ),
            node(
                func=dq_flights,
                inputs="flights_transformed",
                outputs="flights_validated",
                name="validate_flights",
                tags="flights",
            ),
            node(
                func=combine_all_data,
                inputs=[
                    "flights_validated",
                    "airports_validated",
                    "population_validated",
                    "raw_cancellation_codes",
                    "raw_weather_codes",
                    "raw_carriers",
                ],
                outputs="combined_all",
                name="combine_all_sources",
                tags="combined",
            ),
            node(
                func=agg_by_op_carrier,
                inputs="combined_all",
                outputs="operating_carrier_stats",
                name="create_operating_carrier_aggregate",
                tags="business",
            ),
            node(
                func=agg_by_state,
                inputs="combined_all",
                outputs="state_stats",
                name="create_state_level_aggregate",
                tags="business",
            ),
            node(
                func=agg_by_departure_airport,
                inputs="combined_all",
                outputs="departure_airport_stats",
                name="create_departure_airport_level_aggregate",
                tags="business",
            ),
        ]
    )
