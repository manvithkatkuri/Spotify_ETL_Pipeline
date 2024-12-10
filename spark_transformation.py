
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
  
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
from pyspark.sql.functions import col, explode, to_date, concat_ws
from datetime import datetime
from awsglue.dynamicframe import DynamicFrame
s3_path="s3://spotify-data-manvith/raw_data/to-be-processed_data/"

source_df=glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    format="json",
    connection_options={
        "paths": [s3_path]},

    
)
spotify_df=source_df.toDF()
spotify_df.show(5)
spotify_df.withColumn("items",explode("items")).show(5)
def process_album(df):
    df = df.withColumn("items", explode("items")).select(
        col("items.track.album.id").alias("album_id"),
        col("items.track.album.name").alias("album_name"),
        col("items.track.album.release_date").alias("album_release_date"),
        col("items.track.album.total_tracks").alias("album_total_tracks"),
        col("items.track.album.external_urls.spotify").alias("album_url")
    ).drop_duplicates(['album_id'])
    return df


def process_artists(df):
    # Explode the "items" array to process each item individually
    df = df.withColumn("items", explode(col("items")))

    # Explode the "artists" array to process each artist individually
    df = df.withColumn("artists", explode(col("items.track.album.artists"))).select(
        col("artists.id").alias("artist_id"),
        col("artists.name").alias("artist_name"),
        col("artists.external_urls.spotify").alias("artist_url")
    ).drop_duplicates(['artist_id'])
    
    return df

def process_songs(df):
    df = df.withColumn("items", explode(col("items")))
    
    df = df.withColumn("artists", explode(col("items.track.album.artists"))).select(
        col("items.track.name").alias("song_name"),
        col("items.track.id").alias("song_id"),
        col("items.track.duration_ms").alias("duration_ms"),
        col("items.track.external_urls.spotify").alias("song_url"),
        col("items.track.popularity").alias("song_popularity"),
        col("items.track.album.id").alias("album_id"),
        col("artists.id").alias("artist_id"),
        col("items.added_at").alias("song_added_at")
        
    
    
    ).drop_duplicates(['song_id'])
    
    df=df.withColumn("song_added_at",to_date(col("song_added_at")))
    return df
    


album_df=process_album(spotify_df)
album_df.show(5)
artists_df=process_artists(spotify_df)
artists_df.show(5)
songs_df=process_songs(spotify_df)
songs_df.show(5)
def write_to_s3(df, path_suffix, format_type="csv"):
    dynamic_frame = DynamicFrame.fromDF(df, glueContext, "dynamic_frame")
    glueContext.write_dynamic_frame.from_options(
        frame=dynamic_frame,
        connection_type="s3",
        connection_options={"path": f"s3://spotify-data-manvith/transformed_data/{path_suffix}/"},
        format=format_type,
        format_options={"separator": ",", "quoteChar": '"', "withHeader": True}
        
    )

    
    
write_to_s3(album_df, "album/album_transformed_{}".format(datetime.now().strftime("%Y-%m-%d")),"csv")
write_to_s3(artists_df, "artists/artists_transformed_{}".format(datetime.now().strftime("%Y-%m-%d")),"csv")
write_to_s3(songs_df, "songs/songs_transformed_{}".format(datetime.now().strftime("%Y-%m-%d")),"csv")
job.commit()