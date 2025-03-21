from jira_sad_alerts_create import *

create_jira_issue(  
                    sql_server = "LTYPRDCHSSQL00", 
                    sql_database_name = "CHASE_APPLE_Infosec",
                    sql_query  = "select * from Chase_Apple_FraudEmail a where not exists (select 0 from Chase_Apple_FraudEmail_log b where a.order_id = b.order_id and a.var_id = b.var_id) ",                                         
                    jira_project = "LFO",
                    jira_ticket_type = "Alert",                    
                    jira_ticket_summary = "Chase Apple FRAUD ALERT: Order(s) detected are associated with prior Fraud phone number, E-Mail,User_ID, address and first and last name ",
                    jira_ticket_description="Please, check the attached file for details!",
                    sql_log_table_name="Chase_Apple_FraudEmail_log"                    
                    )


