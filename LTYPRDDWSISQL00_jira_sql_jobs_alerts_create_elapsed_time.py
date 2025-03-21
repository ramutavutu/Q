#https://jira.readthedocs.io/
#https://github.com/pycontribs/jira
from jira.client import JIRA
import pandas as pd
import sqlalchemy
import sys

def create_jira_issue(sql_server):
    SQL_QUERY = """
                WITH
                    CTE_SYSESSION (AgentStartDate)
                    AS 
                    (
                        SELECT MAX(AGENT_START_DATE) AS AgentStartDate FROM MSDB.DBO.SYSSESSIONS
                    ),
                    CTE_EXECUTION_AVG_TIME 
                    AS 
                    (
                        SELECT 
                                j.name AS JobName,
                                AVG(h.run_duration) AVGDurationSeconds        
                            FROM msdb.dbo.sysjobs j
                            INNER JOIN msdb.dbo.sysjobhistory h 
                                ON j.job_id = h.job_id
                            WHERE h.run_status = 1 		
                            GROUP BY j.name
                    ),
                    CTE_RUNNING_JOBS
                    AS
                    (
                    SELECT sjob.name AS JobName
                        ,CASE 
                            WHEN SJOB.enabled = 1 THEN 'Enabled'
                            WHEN sjob.enabled = 0 THEN 'Disabled'
                            END AS JobEnabled        
                        ,CASE 
                            WHEN ACT.start_execution_date IS NOT NULL AND ACT.stop_execution_date IS NULL  THEN 'Running'
                            WHEN ACT.start_execution_date IS NOT NULL AND ACT.stop_execution_date IS NOT NULL AND HIST.run_status = 1 THEN 'Stopped'
                            WHEN HIST.run_status = 0 THEN 'Failed'
                            WHEN HIST.run_status = 3 THEN 'Canceled'
                        END AS JobActivity
                        ,DATEDIFF(SECOND,act.start_execution_date, GETDATE()) ElapsedSecondsSinceStarted        
                        ,act.start_execution_date AS JobStartDate        
                            FROM MSDB.DBO.syssessions AS SYS1
                        INNER JOIN CTE_SYSESSION AS SYS2 ON SYS2.AgentStartDate = SYS1.agent_start_date
                        JOIN  msdb.dbo.sysjobactivity act ON act.session_id = SYS1.session_id
                        JOIN msdb.dbo.sysjobs sjob ON sjob.job_id = act.job_id
                        LEFT JOIN  msdb.dbo.sysjobhistory hist ON hist.job_id = act.job_id AND hist.instance_id = act.job_history_id
                        WHERE ACT.start_execution_date IS NOT NULL AND ACT.stop_execution_date IS NULL        
                    )

                SELECT CTE_RUNNING_JOBS.*,
                    CTE_EXECUTION_AVG_TIME.AVGDurationSeconds
                FROM CTE_RUNNING_JOBS
                    INNER JOIN CTE_EXECUTION_AVG_TIME
                        on CTE_RUNNING_JOBS.JobName = CTE_EXECUTION_AVG_TIME.JobName
                        and CTE_RUNNING_JOBS.ElapsedSecondsSinceStarted > (CTE_EXECUTION_AVG_TIME.AVGDurationSeconds * 2)
                        and CTE_RUNNING_JOBS.ElapsedSecondsSinceStarted > 1800

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
                                                summary= "LONG RUNNING JOB - " + df_job["JobName"].values[0] + " (" + sql_server + ")"  ,    
                                                description= " The job '" + df_job["JobName"].values[0] + "' has started the current execution on " + str(df_job["JobStartDate"].values[0]) + " and is still running after " + str(df_job["ElapsedSecondsSinceStarted"].values[0]) + " seconds.", 
                                                issuetype={'name': JIRA_TICKET_TYPE }                              
                                                )
                print(new_issue) 
            #close the connection to SQL Server            
            engine.dispose()    
            

        #print( "SUCCESS")
        sys.exit(0) 
        
            
    except Exception as error:        
        print("ERROR:" + str(error))
        sys.exit(1)

output = create_jira_issue(      
                        sql_server = "LTYPRDDWSISQL00",  
                        )

print(output)
