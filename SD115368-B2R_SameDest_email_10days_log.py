from jira_sad_alerts_create import *

create_jira_issue(  
                    sql_server = "LTYPRDDWSRSQL00", 
                    sql_database_name = "Infosec",
                    sql_query  = "select * from B2R_SameDest_email_10days a where not exists (select 0 from B2R_SameDest_email_10days_log b where a.order_id = b.order_id ) ",                                         
                    jira_project = "LFO",
                    jira_ticket_type = "Alert",                    
                    jira_ticket_summary = "CORE FRAUD ALERT: Multiple orders to same destination or having same email in last 10 days  ",
                    jira_ticket_description="Please, check the attached file for details!",
                    sql_log_table_name="B2R_SameDest_email_10days_log"                    
                    )


