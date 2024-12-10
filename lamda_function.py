import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import boto3
from datetime import datetime

def lambda_handler(event, context):
    client_id = os.environ.get('client_id')
    client_secret = os.environ.get('client_secret')
    
    # Initialize Spotify client credentials
    client_credential_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    sp = spotipy.Spotify(auth_manager=client_credential_manager)

    # Define the playlist URL and extract the URI
    playlist = "https://open.spotify.com/playlist/6VOedaf3eNWDOVpa9Qdlvg"
    playlist_URI = playlist.split("/")[-1]
    data = sp.playlist_tracks(playlist_URI)

    # Set up S3 client and save data
    client = boto3.client('s3')

    filename = "spotify_raw_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
    client.put_object(
        Bucket="spotify-data-manvith",
        Key="raw_data/to-be-processed_data/" + filename,
        Body=json.dumps(data)
    )

    # Set up AWS Glue and start a job
    glue = boto3.client("glue")
    gluejobname = "Spotify_transformation_job"

    try:
        runId = glue.start_job_run(JobName=gluejobname)
        status = glue.get_job_run(JobName=gluejobname, RunId=runId['JobRunId'])
        print("Job Status: ", status['JobRun']['JobRunState'])
    except glue.exceptions.ClientError as e:
        print("Glue Client Error: ", e)
    except Exception as e:
        print("An unexpected error occurred: ", e)
