#https://jira.readthedocs.io/
#https://github.com/pycontribs/jira
from jira.client import JIRA
from io import BytesIO
from datetime import datetime
import pandas as pd
import sqlalchemy
import sys

def create_jira_issue(  sql_server, #SQL SERVER NAME WHERE THE DATABASE RESIDES 
                        sql_database_name, #DATABASE IN USE TO STORE THE TABLES
                        sql_query, #QUERY TO BE USED TO GENERATE THE OUTUPUT WITH ORDERS
                        jira_project, #JIRA PROJECT THAT TICKETS WILL BE CREATED
                        jira_ticket_type, #JIRA TICKET TYPE (Request, Task, Issue etc.) https://support.atlassian.com/jira-cloud-administration/docs/what-are-issue-types/
                        jira_ticket_summary, #TICKET SUMMARY LINE
                        jira_ticket_description, #TICKET DESCRIPTION
                        sql_log_table_name #SQL TABLE TO LOG THE PROCESS
                        ):
    
    #JIRA web url
    #JIRA_CLOUD_BASE_URL = "https://sherwoodforest-sandbox-109.atlassian.net"    
    JIRA_CLOUD_BASE_URL = "https://sherwoodforest.atlassian.net"
    
    #Jira user name to connect and create the tickets
    JIRA_USER_NAME = "jira_loyalty_automated_tickets@bakkt.com" #jira_automated_tickets@bakkt.com
    
    #Jira cloud token generated for the user
    #https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
    JIRA_CLOUD_TOKEN = "ATATT3xFfGF0BnCidHmK9r5G6C1UrUtceIU2pojUMbcmIJnhjPLrp0UKVvl-iWc6o_GuzS46cfWhdKvS50xWfHQONZh93cvFQ7-tUR-4W43xFoDQL4pFBEXsFPL7mDixVF749o6a02_nq6sEwwD6s0tvdSH4xuFMVJnFI9x_Lv4YJy1yknAOS7w=AE59143C"    

    try:    
        #create the database connection    
        engine = sqlalchemy.create_engine('mssql+pyodbc://' + sql_server + '/' + sql_database_name + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')

        #execute the query to return the orders
        df = pd.read_sql_query(sql_query, engine)                  

        #check if the query has returned orders
        if (df.shape[0] > 0): 

            userlist = df["user_id"].unique().tolist()
            
            for userid in userlist:
                df_orderlist = df[df['user_id'] == userid]
                
                ticket_description = ""                                
                for index, row in df_orderlist.iterrows():    
                    ticket_description += "\n\n"
                    for column in df_orderlist.columns:
                        ticket_description +=  (f"{column} : {row[column]}") +"\n"

                #create a bytesio object to handle the excel file creation in memory, avoiding the need to save it to attach latter to the Jira ticket
                excel_attachment = BytesIO()
                
                #use the BytesIO object as the filehandle.
                writer = pd.ExcelWriter(excel_attachment, engine='xlsxwriter')
                
                #write the data frame to the BytesIO object.
                df_orderlist.to_excel(writer, sheet_name='Order List',index=False)
                writer.close()
                
                #set the JIRA project
                jira_options = {'server': JIRA_CLOUD_BASE_URL}

                #set JIRA authentication and connect
                jira = JIRA(options=jira_options,  basic_auth=(JIRA_USER_NAME, JIRA_CLOUD_TOKEN))
                
                #create the issue
                new_issue = jira.create_issue(  project= jira_project, 
                                                summary= jira_ticket_summary  + " - USER_ID:" + userid,
                                                description= ticket_description, 
                                                issuetype={'name': jira_ticket_type }                              
                                                )
                #print(new_issue) 
                
                #assing the ticket to someone
                #jira.assign_issue(new_issue, JIRA_ASSIGNEE) If required to assing to a specific person
            
                #attach the excel file generated in memory to the Jira ticket
                jira.add_attachment(issue=new_issue, attachment=excel_attachment, filename= datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + ' - order_list.xlsx')
          
                #add the jira ticket number to the results. It requires a new dataframe once dataframe.assing does not save the new value to the dataframe. To have the modification, it needs to be sent to a new df
                df_updated = df_orderlist.assign(jira_ticket_number = str(new_issue)) 
            
                #save the new dataframe rows to the log table
                df_updated.to_sql(name=sql_log_table_name,con=engine,if_exists="append", index=False)                      
                                
            #close the connection to SQL Server            
            engine.dispose()    
            

        #print( "SUCCESS")
        sys.exit(0) 
        
            
    except Exception as error:        
        #print("ERROR:" + str(error))
        sys.exit(1)

      