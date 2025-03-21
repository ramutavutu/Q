from jira_sad_alerts_create import *

create_jira_issue(  
                    sql_server = "LTYPRDKEYSQL00", 
                    sql_database_name = "Infosec",
                    sql_query  = "select * from B2R_Ordname_not_Passengername a where not exists (select 0 from B2R_Ordname_not_Passengername_log b where a.order_id = b.order_id ) ",                                         
                    jira_project = "LFO",
                    jira_ticket_type = "Alert",                    
                    jira_ticket_summary = "Core Travel FRAUD ALERT: Orders for where order name is not in passengers name ",
                    jira_ticket_description="Please, check the attached file for details!",
                    sql_log_table_name="B2R_Ordname_not_Passengername_log"                    
                    )


