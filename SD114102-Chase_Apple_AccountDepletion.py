from jira_sad_alerts_create import *

create_jira_issue(  
                    sql_server = "LTYPRDCHSSQL00", 
                    sql_database_name = "CHASE_APPLE_Infosec",
                    sql_query  = "select * from Chase_Apple_AccountDepletion a where not exists (select 0 from Chase_Apple_AccountDepletion_log b where a.order_id = b.order_id ) ",                                         
                    jira_project = "LFO",
                    jira_ticket_type = "Alert",                    
                    jira_ticket_summary = "Chase Apple FRAUD ALERT: Account Depletion ",
                    jira_ticket_description="Please, check the attached file for details!",
                    sql_log_table_name="Chase_Apple_AccountDepletion_log"                    
                    )


