# Udacity Data Engineering Capstone Project

## Goal
Get data about US domestic flights in 2022, as well as Census data about population (and economic factors) to enable OLAP on delays, frequencies, movement, etc.

## Types of analytics
Here are possible analytics questions that could be answered based on the final dataset combinations:
- What are the airlines / airports with most delays?
- What is the On Time Performance (OTP) of various airlines?
- What are the busiest airports per month?
- Which cancellation reasons are most frequent per month / airport / airline?
- Are the most populous states also those with the most flights?
- What is the flights / airports per (thousand-)state inhabitants ratio for each state?

## Getting started
Set up your Python venv using `python -m venv venv`, install [Kedro](https://pypi.org/project/kedro/), and then run `pip install -r src/requirements.txt`.

The CSV datasets need to be downloaded from their source and placed in the `data/01_raw` directory. Note that the pipeline expects airlines data to be unzipped and stored in `data/01_raw/us-airlines-domestic-departure-dataset/`.

For the API datasets, only the API key needs to be placed in a `conf/local/credentials.yml` file, which has to be created beforehand. A sample of how this file should look like is indicated below. To obtain your API key, see [here](https://www.census.gov/content/dam/Census/library/publications/2020/acs/acs_api_handbook_2020_ch02.pdf).

```yaml
dev_census_api:
  key: <YOUR_CENSUS_API_KEY>
```

To run the project, open a terminal in the project workspace and run `kedro run`. Logging is enabled for all runs ([example](docs/data_dictionary/example_run_log.info))

Note: by default, the pipeline will run sequentially. Running it in parallel can be achieved by executing `kedro run -r ParallelRunner`.

## Used technologies & motivation
Kedro and Polars are at the backbone of the project. Here's a short description of each:

- [Kedro](https://kedro.org/), because I think it is sits at the intersection between Data Engineering, Data Science, and MLOps, as a framework designed to create reproducible DS & MLOps experiments. It includes handy features for structuring Data Engineering pipelines, such as a Data Catalog that can be easily extended and adapted to a variety of data sources (e.g., S3, ADLS Gen, local) and formats (e.g, CSV, API, Parquet), as well.
- [Polars](https://www.pola.rs/), because is a relatively new and fast DataFrame library, developed in Rust, with a clean Expressions API (similar to Spark), and support for optimized query execution in lazy mode

I mainly use Databricks in my day-to-day job, thus I wanted to learn somehting new. Not all organizations *need* resources to be deployed in the cloud, and I decided to write this project using local sources specified in the Kedro catalog and using Polars. Should one want to move to a more productional setting to accommodate more data and / or users, this can be done by adjusting it with the suitable file formats & credentials, as indicated in the [examples provieded in the docs](https://docs.kedro.org/en/stable/data/data_catalog.html#use-the-data-catalog-with-the-yaml-api), with what should be minimal effort.

While developing locally can be more constraining in terms of resources, using Polars turned out to be a breeze, thanks to its query engine, which I used in combination with setting proper `dtypes` and Kedro's `ParitionedDataSet`.

## Project structure summary
Here are the most important files for the project:

- [catalog.yml](conf/base/catalog.yml): contains all Data Catalog entries (i.e., pipeline inputs, intermediary datasets, and outputs), specifying the storage type, location, etc.
- [pipeline.py](src/udacity_de_capstone/pipelines/data_engineering/pipeline.py): constructs the pipeline in code by linking nodes, inputs, and outputs
- [nodes.py](src/udacity_de_capstone/pipelines/data_engineering/nodes.py): smallest unit of work, each of which are responsible for consuming one or more datasets and yielding new ones. These are used for transformation and validation, as exporting is done using Kedro and the Data Catalog

There's also a [notebook](notebooks/eda.ipynb) that was used when starting the projec to perform EDA on the input datasets and prototype transformations before writing them in modular way was nodes in the pipeline.

## DAG
The figure below displays the Data Engineering pipeline as a DAG. This was created using `kedro viz` ([link](https://github.com/kedro-org/kedro-viz)). The DAG is constructed based on the `nodes` and `catalog` datasets. Execution order is *not* always the same, as `kedro` constructs the DAG based on the inputs and outputs of each node.

![DAG](images/dag.svg?raw=true&sanitize=true "DAG")

## Data Dictionary
The output data dictionary is stored as a collection of JSON files exported from the schema of `polars.DataFrame` objects. These can be found in the [data_dictionary](docs/data_dictionary/) folder of the repo. As a summary, there are two layers of pipeline outputs:

1. Complete Data - this is a partitioned dataset which includes all the joined data coming from all sources. Its intended use is for data practitioners who would be comfortable running analytics using Polars or Spark.

2. Business Level Aggregates - these are overall statistics about operating carriers, airports, and states. They are meant to be used by Business Analysts for reporting. While theses datasets are currently stored in CSV format, they could easily be copied to a relational database (e.g., Postgres).

## Addressing other scenarios
The Udacity project speicifcation highlighted the below scenarios that should be addressed. 

### 100x increase in data volume
Should this happen, there are a few ways in which we could adapt the pipeline. One of them is the move storage from local to a Data Lake, and compute from local to an Apache Spark cluster.

Kedro could remain at the center of the pipeline design, and its Data Catalog needs to be adusted with updated paths to the chosen Data Lake. Also, since Polars has a simiolar API to Spark, migrating the code to Spark and taking advantage of distributed computing should be relatively straightforward. The latter is also aided by the fact that the project is now using `PartitionedDataSet`s. While these are a Kedro concept and are now implemented using Python's Pickle serializer, they could be adapted to use columnar file formats like Parquet.

### Daily 7am run of pipelines
Currently, the pipeline processes static data (i.e., one year of US domestic flight departures). Should there be new data coming in each day at a specific time, there are a few changes to make:

- An orchestration tool should be used (e.g., Apache Airflow, Databricks). A Kedro project could be run in either. There's also an [Airflow plugin](https://github.com/quantumblacklabs/kedro-airflow) which could come in handy
- Insertion / updating mechanisms in Polars and partitioned datasets need to be adjusted to account for new records

### 100+ users accessing the data
Using a Data Lake for storage should accommodate this scenario on the storage side. For computation, the business level aggregates can be placed in a relational database of choice or be written to Parquet files, which can then be subsequently loaded and analyzed using a BI tool such as Power BI or Tableau.

## Input dataset description
<!-- ### Aircraft Characteristics Data ([source](https://www.faa.gov/airports/engineering/aircraft_char_database/data(https://www.faa.gov/airports/engineering/aircraft_char_database/data)))
| Field       | Value                                                                |
| ----------- | -------------------------------------------------------------------- |
| Description | Technical specifications of aircraft known to the FAA                |
| Format      | CSV                                                                  | -->

### US Airlines Domestic Flights 2022 ([source](https://www.kaggle.com/datasets/jl8771/2022-us-airlines-domestic-departure-data))
| Field       | Value                                                                                                                                                         |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Description | Data about domestic departing US flights in 2022, complete with airport codes, cancellations, and basic weather indicators (usually at the departure station) |
| Files       | ActiveWeather, Cancellation, Carriers, CompleteData, Stations                                                                                                 |
| Format      | CSV                                                                                                                                                           |
| Data size   | 6,954,636 flight records

### US Census Data ([source](https://www.census.gov/data/developers/data-sets/popest-popproj.html))
| Field       | Value                                                                        |
| ----------- | ---------------------------------------------------------------------------- |
| Description | US Census data regarding population                                          |
| Format      | JSON API response                                                            |
| API Key     | Request your own API key [here](https://api.census.gov/data/key_signup.html) |

<!-- ### Airport Data ([source](https://github.com/davidmegginson/ourairports-data))
| Field       | Value                                                                   |
| ----------- | ----------------------------------------------------------------------- |
| Description | Detailed airport data, with more fields than in the US airlines dataset |
| Format      | CSV                                                                     |
 -->
