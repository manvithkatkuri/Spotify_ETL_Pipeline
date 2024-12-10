# Spotify_ETL_Pipeline

This project implements an ETL Pipeline for Spotify Data using a combination of AWS services, Snowflake, and Power BI. The goal is to extract Spotify playlist data, transform it, and load it into a Snowflake database for further analysis and visualization.

## Workflow Description

### 1. Data Extraction: AWS Lambda
A Spotify API is used to extract raw playlist data in JSON format. The connection is established using SpotifyClientCredentials, where client credentials (Client ID and Secret) are securely stored in the Lambda environment variables.

The lambda_function.py script:
1. Retrieves playlist details using the Spotify API.

2. Saves the raw JSON data into an Amazon S3 bucket (spotify-data-manvith) under the folder raw_data/to-be-processed_data/. The file is named using a timestamp for unique identification.

3. Triggers an AWS Glue Job (Spotify_transformation_job) to process the extracted data.
This function is triggered every minute using Amazon CloudWatch.
