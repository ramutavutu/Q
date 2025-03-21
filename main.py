from google.cloud.sql.connector import Connector
import sqlalchemy
import pandas as pd
import pandas_gbq
from google.auth import compute_engine
from google.cloud import bigquery
from google.cloud import secretmanager
import logging
import datetime
import os

DHW_PROJECT_NAME = os.environ["DHW_PROJECT_NAME"]
DWH_PROJECT_ID = os.environ["DWH_PROJECT_ID"]
BQ_TABLE_DATASET = os.environ["BQ_TABLE_DATASET"]
BQ_TABLE_NAME = os.environ["BQ_TABLE_NAME"]
SOURCE_DB_NAME = os.environ["SOURCE_DB_NAME"]
SOURCE_TABLE_NAME = os.environ["SOURCE_TABLE_NAME"] 
ETL_ENVIRONMENT = os.environ["ETL_ENVIRONMENT"]

def get_secret_value(secret_name,project_id):

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=name)
    secret_value = response.payload.data.decode("UTF-8")

    return secret_value


def retrieve_execution_date_range(bq_table):
    cred = compute_engine.Credentials()    
    
    bq_client = bigquery.Client(project=DHW_PROJECT_NAME,credentials=cred)    
    
    bq_query  = 'SELECT FORMAT_DATETIME("%Y-%m-%d %H:%M:%E6S",max(updated)) start_date, \
                    FORMAT_DATETIME("%Y-%m-%d %H:%M:%E6S",current_timestamp()) end_date \
                FROM ' + DHW_PROJECT_NAME + '.' + BQ_TABLE_DATASET + '.' + bq_table     

    bq_resultset = bq_client.query(bq_query).to_dataframe();   
    
    bq_client.close()

    return bq_resultset

def check_bq_table_exists(project_id,bq_dataset,bq_table):
    cred = compute_engine.Credentials()    
    
    bq_client = bigquery.Client(project=DHW_PROJECT_NAME,credentials=cred)    
    
    try:
        bq_client.get_table(project_id+"."+bq_dataset+"."+bq_table)   
        bq_table_exists = True
    except:
        bq_table_exists = False
    
    bq_client.close()
    return bq_table_exists

def cloudsql_getconn():
    connector = Connector()
    conn = connector.connect(
                            get_secret_value(ETL_ENVIRONMENT+"_cloudsql_connection_name",DWH_PROJECT_ID),
                            "pymysql",
                            user=get_secret_value(ETL_ENVIRONMENT+"_cloudsql_user",DWH_PROJECT_ID),
                            password=get_secret_value(ETL_ENVIRONMENT+"_cloudsql_password",DWH_PROJECT_ID),
                            db=SOURCE_DB_NAME  
                            )    
    return conn    

def return_mysql_query():
    bq_table_exists= check_bq_table_exists(DHW_PROJECT_NAME,BQ_TABLE_DATASET,BQ_TABLE_NAME)
        
    if bq_table_exists:    
        query_date_range = retrieve_execution_date_range(bq_table=BQ_TABLE_NAME)    

    pool = sqlalchemy.create_engine(
                                    "mysql+pymysql://",
                                    creator=cloudsql_getconn,                                    
                                    )    
    db_conn = pool.connect()
    
    setcommand = "SET session group_concat_max_len=40000; "
    db_conn.execute(sqlalchemy.text(setcommand))      
    
    #QUERY INFORMATION SCHEMA TO CREATE A DYNAMIC SQL QUERY, REMOVING ENCRYPTED AND HASH COLUMNS FROM THE OUTUPUT    
    query_columns = "select CONCAT('select ', GROUP_CONCAT(case when data_type <> 'binary' then column_name else concat('bin_to_uuid(',column_name,') as ',column_name) end order by ordinal_position),' from ',table_name) query from information_schema.columns where table_name = '"+SOURCE_TABLE_NAME+"' and column_name not like '%encrypted%' and column_name not like '%hash%'; "        
    
    query = pd.read_sql_query(sqlalchemy.text(query_columns),db_conn)

    query_cp = query.copy()
    
    query_as_str=""
    query_as_str = str(query_cp["query"].values[0])

    if bq_table_exists:
        query_as_str += " where updated > '" + query_date_range['start_date'].values[0] + "' and updated <= '" + query_date_range['end_date'].values[0] + "'"  
    
    db_conn.close()
    pool.dispose()   

    return query_as_str


def move_data():                
    try:
        print(str(datetime.datetime.now()) + ' - Starting data copy! ( DB:'+ SOURCE_DB_NAME +' - Table: '+ SOURCE_TABLE_NAME +')')
        pool = sqlalchemy.create_engine(
                                        "mysql+pymysql://",
                                        creator=cloudsql_getconn,
                                        )
    
        db_conn = pool.connect()                                                         
        query = return_mysql_query()                

        print(query)

        df_results = pd.read_sql_query(query,db_conn)        

        if (df_results.shape[0] > 0):           
            cred = compute_engine.Credentials()    
            pandas_gbq.to_gbq(  df_results,
                                project_id=  DHW_PROJECT_NAME,
                                destination_table= BQ_TABLE_DATASET + '.' + BQ_TABLE_NAME,
                                if_exists="append",
                                credentials=cred,
                                api_method="load_csv")        
        
        db_conn.close()
        pool.dispose()

        print('Rows moved to BQ: ' + str(df_results.shape[0]))
        print(str(datetime.datetime.now()) + ' - Finished data copy!')
            
        return "SUCCESS"           
        
    except Exception as error:
        logging.exception("Exception occurred")
        print(str(error))
        return str(error)   
    
def hello_http(request):  
  output = move_data() 
  print(output)
  return output
