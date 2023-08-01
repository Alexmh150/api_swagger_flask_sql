from flask import Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import datetime, random

# Read csv file
def read_file(file_name,n_times):
    df = pd.read_csv(file_name)
    if n_times > 1:
        df = pd.concat([df]*n_times)

    return df

# create trip df
def create_trip_df(df):
    df.datetime = pd.to_datetime(df.datetime)
    df = df[['region_id','origin_coord','destination_coord','datetime','datasource_id']]
    
    return df

# create and store the dim_region table
def create_store_region_table(df, database_name, model):
    # Rename column
    df.rename(columns={'region':'region_name'},inplace=True)
    df.region_name = df.region_name.str.lower()
    # Retrieve unique region names
    region_names = df.region_name.unique().tolist()

    # Create dataframe from lists
    region_id = []
    region_population = []
    i = 1
    for region_name in region_names:
        region_id.append(i)
        region_population.append(random.randrange(50000,200000,1))
        i += 1

    region_df = pd.DataFrame({'region_id':region_id,
                              'region_name':region_names,
                              'region_population':region_population})
    
    # Update df initial with region_id    
    df = df.merge(region_df[['region_name','region_id']],on = 'region_name',how='inner')
    df.drop(columns=['region_name'],inplace=True)

    # Call method to store the df in database
    store_df(df=region_df, database_name=database_name, model=model)

    return df

# Create and store dim_datasource table
def create_store_datasource_table(df, database_name, model):
    # Rename column
    df.rename(columns={'datasource':'datasource_name'},inplace=True)
    # Retrive datasource_name uniques
    datasource_names = df.datasource_name.unique()

    # Create df from list
    datasource_id = []
    datasource_url = []
    i = 1

    for datasource_name in datasource_names:
        datasource_id.append(i)
        datasource_url.append("https://"+datasource_name+".com")
        i += 1

    datasource_df = pd.DataFrame({'datasource_id':datasource_id,
                              'datasource_name':datasource_names,
                              'datasource_url':datasource_url})
    
    # Update initial df adding the column datasource_id
    df = df.merge(datasource_df[['datasource_name','datasource_id']],on = 'datasource_name',how='inner')
    df.drop(columns=['datasource_name'],inplace=True)

    # Call methos to store the df in database
    store_df(df=datasource_df, database_name=database_name, model=model)

    return df

# Create and store dim_date table
def create_store_date_table(df, database_name, model):
    # Trasform column to datetime
    df.datetime = pd.to_datetime(df.datetime,format='%Y-%m-%d %H:%M:%S')
    
    # Get min date and max date
    start_date = df.datetime.min()
    end_date = df.datetime.max()
    
    # Declare incremental
    delta = datetime.timedelta(days=1)

    # Create df from lists
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

        current_date += delta
    
    date_df = pd.DataFrame({
        'date': date,
        'day_name': days,
        'week_number': weeks,
        'month': months,
        'year': years
    })

    # Call method to store df in database
    store_df(df=date_df, database_name=database_name, model=model)
    return "DimDate has been stored"

# Transform the days to number
def get_week_day_name(date):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[date.weekday()]

# Store df
def store_df(df, database_name, model):
    # Establish connection to sql
    engine = create_engine(f'sqlite:///{database_name}')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create dict to store
    data_dict = df.to_dict(orient='records')

    # Insert data
    session.bulk_insert_mappings(model, data_dict)
    session.commit()
    session.close()

# Store data for chunks to notify the status on the process
def store_notify_df(df, df_name, chunk_size, database_name, model):
    
    if chunk_size is None:
        chunk_size = 10
    
    # Store data from chunks and send a response to api
    def generate_updates():
        total_rows = len(df)
        rows_processed = 0
        
        num_process = total_rows//chunk_size

        # Send response to api
        yield f"Process started: Date ingested for {df_name}\n"

        # Store data
        for i in range(num_process):
            if i+1 == num_process:
                df_to_store = df[i*chunk_size:]
            else:
                df_to_store = df[i*chunk_size:((i+1)*chunk_size)]
            
            # Call method to store data
            store_df(df=df_to_store, database_name=database_name, model=model)

            # Update the number of rows processed
            rows_processed += len(df_to_store)

            # Calculate the progress percentage
            progress = (rows_processed / total_rows) * 100

            # Send response to api
            yield f"Date ingested for {df_name}: {progress} %\n"

        # Send response to api
        yield f"Process finished: Date ingested for {df_name}\n"
        
    # Return the status updates as an SSE stream
    return Response(generate_updates(), content_type='text/event-stream')