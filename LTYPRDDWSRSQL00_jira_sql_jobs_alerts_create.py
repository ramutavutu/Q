#https://jira.readthedocs.io/
#https://github.com/pycontribs/jira
from jira.client import JIRA
import pandas as pd
import sqlalchemy
import sys

def create_jira_issue(sql_server):
    SQL_QUERY = """
                select	ItemPath JobName,
                        TimeStart ExecutionDate,
                        Status 'Message'
                from ReportServer.dbo.ExecutionLog3 j
                where RequestType = 'Subscription'
                and   cast(timestart as date) > '2024-06-10'
                and   status <> 'rsSuccess'     
                and   UserName = 'BRIDGE2SOLUTION\\SVC_CentralSQL'           
                and   not exists (select 0 
                                    from DBA.dbo.sql_agent_jira_tickets jt 
                                    where jt.JobName = j.ItemPath COLLATE SQL_Latin1_General_CP1_CI_AS
                                    and jt.ExecutionDate = j.TimeStart 
                                    and jt.Message = j.Status COLLATE SQL_Latin1_General_CP1_CI_AS) 
                order by 2
                """
    
    JIRA_CLOUD_BASE_URL = "https://sherwoodforest.atlassian.net"
    
    #Jira user name to connect and create the tickets
    JIRA_USER_NAME = "jira_loyalty_automated_tickets@bakkt.com" 
    
    #Jira cloud token generated for the user    
    JIRA_CLOUD_TOKEN = "ATATT3xFfGF0BnCidHmK9r5G6C1UrUtceIU2pojUMbcmIJnhjPLrp0UKVvl-iWc6o_GuzS46cfWhdKvS50xWfHQONZh93cvFQ7-tUR-4W43xFoDQL4pFBEXsFPL7mDixVF749o6a02_nq6sEwwD6s0tvdSH4xuFMVJnFI9x_Lv4YJy1yknAOS7w=AE59143C"    

    JIRA_TICKET_TYPE = "Bug"

    try:    
        #create the database connection    
        engine = sqlalchemy.create_engine('mssql+pyodbc://' + sql_server + '/' + 'DBA' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')

        #execute the query to return the orders
        df = pd.read_sql_query(SQL_QUERY, engine)                  

        #check if the query has returned orders
        if (df.shape[0] > 0): 

            joblist = df["JobName"].unique().tolist()
            
            for job in joblist:      

                df_job = df[df['JobName'] == job]     

                #set the JIRA project
                jira_options = {'server': JIRA_CLOUD_BASE_URL}

                #set JIRA authentication and connect
                jira = JIRA(options=jira_options,  basic_auth=(JIRA_USER_NAME, JIRA_CLOUD_TOKEN))
                
                #create the issue
                new_issue = jira.create_issue(  project= "DA", 
                                                summary= "SSRS SUBSCRIPTION FAILURE - " + df_job["JobName"].values[0] + " (" + sql_server + ")"  ,    
                                                description= df_job["Message"].values[0] + " - at " + str(df_job["ExecutionDate"].values[0]) + " - Check RSLOG file for error details", 
                                                issuetype={'name': JIRA_TICKET_TYPE }                              
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
        #print("ERROR:" + str(error))
        sys.exit(1)

output = create_jira_issue(      
                        sql_server = "LTYPRDDWSRSQL00",  
                        )

print(output)
