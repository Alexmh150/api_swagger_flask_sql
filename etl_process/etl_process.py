from create_database.models import create_database, Trip, DimDate, DimRegion
from flask import Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import datetime
import random

# Read csv file
def read_file(file_name):
    df = pd.read_csv(file_name)
    return df

# Create necessary tables
# create trip df
def create_trip_df(df):
    df.rename(columns={'region':'region_name'},inplace=True)
    df.region_name = df.region_name.str.lower()
    df.datetime = pd.to_datetime(df.datetime)
    
    return df

# create region df
def create_store_region_df(df, database_name, model):
    region_name = df.region_name.unique()
    region_population = [ random.randrange(100,200,1) for i in region_name]

    region_df = pd.DataFrame({'region_name':region_name,'region_population':region_population})

    store_df(df=region_df, database_name=database_name, model=model)

# Create date df
def create_store_date_df(df, database_name, model):
    df.datetime = pd.to_datetime(df.datetime,format='%Y-%m-%d %H:%M:%S')
    start_date = df.datetime.min()
    end_date = df.datetime.max()
    delta = datetime.timedelta(days=1)

    current_date = start_date
    date = []
    days = []
    months = []
    years = []
    weeks = []
    while current_date <= end_date:

        # Get week day name
        day_name = get_week_day_name(current_date)

        # Get week number
        week_number = current_date.isocalendar()[1]

        date.append(current_date)
        days.append(day_name)
        months.append(current_date.month)
        years.append(current_date.year)
        weeks.append(week_number)

        # Move to the next date
        current_date += delta
    
    date_df = pd.DataFrame({
        'date': date,
        'day_name': days,
        'week_number': weeks,
        'month': months,
        'year': years
    })

    store_df(df=date_df, database_name=database_name, model=model)
    return "DimDate has been stored"

def get_week_day_name(date):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[date.weekday()]

def store_df(df, database_name, model):
    engine = create_engine(f'sqlite:///{database_name}')
    Session = sessionmaker(bind=engine)
    session = Session()
    data_dict = df.to_dict(orient='records')
    session.bulk_insert_mappings(model, data_dict)
    session.commit()
    session.close()

#store_df
def store_notify_df(df, df_name, chunk_size, database_name, model):

    def generate_updates():
        total_rows = len(df)
        rows_processed = 0

        num_process = total_rows//chunk_size

        for i in range(num_process):
            if i == num_process-1:
                df_to_store = df[i*chunk_size:]
            else:
                df_to_store = df[i*chunk_size:((i+1)*chunk_size)-1]
            
            store_df(df=df_to_store, database_name=database_name, model=model)

            # Update the number of rows processed
            rows_processed += len(df_to_store)

            # Calculate the progress percentage
            progress = (rows_processed / total_rows) * 100

            # Yield the progress update to the client as an SSE event
            yield f"Date ingested for {df_name}: {progress} %\n"

    # Return the status updates as an SSE stream
    return Response(generate_updates(), content_type='text/event-stream')