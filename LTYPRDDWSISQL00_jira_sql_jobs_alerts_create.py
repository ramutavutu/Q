#https://jira.readthedocs.io/
#https://github.com/pycontribs/jira
from jira.client import JIRA
import pandas as pd
import sqlalchemy
import sys
import os

def map_priority(priority_code):
    priority_mapping = {
        'P1': 'High',
        'P2': 'Medium',
        'P3': 'Low'
    }
    return priority_mapping.get(priority_code, 'High')  # Default to 'High' if the code isn't found

    # Query the Excel file and return the "priority" for the "name" found
def query_excel_file(file_path, name_to_search):
    # Check if the file exists
    if not os.path.exists(file_path):
        return "Error: The file does not exist. Default priority set to High."
    
    try:
        df = pd.read_excel(file_path)
        
      
        if 'Process' in df.columns and 'Priority' in df.columns:
            result = df[df['Process'] == name_to_search]['Priority']
            if not result.empty:
                priority_code = result.iloc[0]
                # Map the priority code to human-readable format
                return map_priority(priority_code)
            else:
                return "No match found for the name. Default priority set to High."
        else:
            return "Required columns ('Process', 'priority') not found in the Excel file. Default priority set to High."
    except Exception as e:
        return f"Error reading the Excel file: {e}. Default priority set to High."


def create_jira_issue(sql_server):
    SQL_QUERY = """
                Execute dba.[dbo].[Select_SSIS_Error_Log]
                """


    
    JIRA_CLOUD_BASE_URL = "https://sherwoodforest.atlassian.net"
    
    #Jira user name to connect and create the tickets
    JIRA_USER_NAME = "jira_loyalty_automated_tickets@bakkt.com" 
    file_path = r"C:\\Users\\esilva\\Downloads\\20250130 - JIRA_Data Process_Mapping.xlsx"
    
    #Jira cloud token generated for the user    
    #JIRA_CLOUD_TOKEN = #"ATATT3xFfGF0BnCidHmK9r5G6C1UrUtceIU2pojUMbcmIJnhjPLrp0UKVvl-iWc6o_GuzS46cfWhdKvS50xWfHQONZh93cvFQ7-tUR-4W43xFoDQL4pFBEXsFPL7mDixVF749o6a02_nq6sEwwD6#s0tvdSH4xuFMVJnFI9x_Lv4YJy1yknAOS7w=AE59143C"    

    JIRA_TICKET_TYPE = "Bug"

    try:    
        #create the database connection    
        engine = sqlalchemy.create_engine('mssql+pyodbc://' + sql_server + '/' + 'DBA' + '?trusted_connection=yes&driver=ODBC+Driver+13+for+SQL+Server')

        #execute the query to return the orders
        df = pd.read_sql_query(SQL_QUERY, engine)                  

        #check if the query has returned orders
        if (df.shape[0] > 0): 

            joblist = df["JobName"].unique().tolist()
            
            for job in joblist:      

                df_job = df[df['JobName'] == job]    

                priority = query_excel_file (file_path,job)

                #set the JIRA project
                jira_options = {'server': JIRA_CLOUD_BASE_URL}

                #set JIRA authentication and connect
                jira = JIRA(options=jira_options,  basic_auth=(JIRA_USER_NAME, JIRA_CLOUD_TOKEN))
                print (priority)

               # If no priority found or an error occurred, assign "High"
                if "Default priority set to High" in priority or "Error" in priority:
                    priority = "High"

                    new_issue = jira.create_issue(  project= "DA", 
                                                summary= "Priority not avaible for job " + df_job["Message"].values[0]  ,    
                                                description= df_job["Message"].values[0] + " - at " + str(df_job["ExecutionDate"].values[0]), 
                                                issuetype={'name': JIRA_TICKET_TYPE },
                                                priority= {'name': priority},                  
                                                )

                
                #create the issue
                new_issue = jira.create_issue(  project= "DA", 
                                                summary= "JOB FAILURE - " + df_job["JobName"].values[0] + " (" + sql_server + ")"  ,    
                                                description= df_job["Message"].values[0] + " - at " + str(df_job["ExecutionDate"].values[0]), 
                                                issuetype={'name': JIRA_TICKET_TYPE },
                                                priority= {'name': priority},                  
                                                )
                print(new_issue) 
                #add the jira ticket number to the results. It requires a new dataframe once dataframe.assing does not save the new value to the dataframe. To have the modification, it needs to be sent to a new df
                df_updated = df_job.assign(jira_ticket_number = str(new_issue)) 
            
                #save the new dataframe rows to the log table
                df_updated.to_sql(name="sql_agent_jira_tickets",con=engine,if_exists="append", index=False)                      
                                
            #close the connection to SQL Server            
            engine.dispose()    
            

        #print( "SUCCESS")
        sys.exit(0) 
        
            
    except Exception as error:        
        print("ERROR:" + str(error))
        sys.exit(1)

output = create_jira_issue(      
                        sql_server = "127.0.0.1:39388",  
                        )

print(output)
