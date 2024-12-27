--create database
create database spotify_db;

--creating storage integration
create or replace storage integration s3_init
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = S3
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::225989346388:role/etl_spotify_snoflake_role'
  STORAGE_ALLOWED_LOCATIONS=('s3://spotify-data-manvith')
  comment ='Creating connection to S3 ';

--verifying details of integration  
DESC integration s3_init;--change the aws user arn and externalId in aws

--creating file format
  CREATE OR REPLACE file format csv_fileformat
      type=csv
      field_delimiter=','
      skip_header=1
      null_if=('NULL','null')
      empty_field_as_null=TRUE;


--creating stage
 CREATE OR REPLACE stage spotify_stage
   URL='s3://spotify-data-manvith/transformed_data/'
   STORAGE_INTEGRATION=s3_init
   FILE_FORMAT=csv_fileformat;


--verifying stage creation
 list @spotify_stage;



--creating tables
 CREATE OR REPLACE TABLE tbl_album(
     album_id STRING,
     album_name STRING,
     album_release_date DATE,
     album_total_tracks INT,
     album_url STRING
     
    
 )



 CREATE OR REPLACE TABLE tbl_artists(
      artist_id STRING,
      artist_name STRING,
      artist_url STRING
 
 )
song_name,song_id,duration_ms,song_url,song_popularity,album_id,artist_id,song_added_at


  CREATE OR REPLACE TABLE tbl_songs(
     song_name STRING,
     song_id STRING,
     duration_ms INT,
     song_url STRING,
     song_popularity INT,
     album_id STRING,
     artist_id STRING,
     song_added_at DATE
  )
 
  COPY INTO tbl_songs
  FROM @spotify_stage/songs/songs_transformed_2024-12-08/

  SELECT * FROM TBL_SONGS;

  -- CREATE SNOWPIPE
CREATE OR REPLACE SCHEMA PIPE;

CREATE OR REPLACE PIPE spotify_db.pipe.tbl_album_pipe
auto_ingest=TRUE
AS
COPY INTO spotify_db.public.tbl_album
FROM @spotify_db.public.spotify_stage/album/;

CREATE OR REPLACE PIPE spotify_db.pipe.tbl_artists_pipe
auto_ingest=TRUE
AS
COPY INTO spotify_db.public.tbl_artists
FROM @spotify_db.public.spotify_stage/artists/;

CREATE OR REPLACE PIPE spotify_db.pipe.tbl_songs_pipe
auto_ingest=TRUE
AS
COPY INTO spotify_db.public.tbl_songs
FROM @spotify_db.public.spotify_stage/songs/;



--Event creation
DESC pipe pipe.tbl_songs_pipe

DESC pipe pipe.tbl_album_pipe

DESC pipe pipe.tbl_artists_pipe


SELECT COUNT(*) FROM TBL_ALBUM;

--Debugging pipe
SELECT SYSTEM$PIPE_STATUS('pipe.tbl_album_pipe')  


SELECT COUNT(*) FROM TBL_SONGS;

SELECT COUNT(*) FROM TBL_ARTISTS;

  
