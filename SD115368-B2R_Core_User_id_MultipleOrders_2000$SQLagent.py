from jira_sad_alerts_create import *

create_jira_issue(  
                    sql_server = "LTYPRDKEYSQL00", 
                    sql_database_name = "Infosec",
                    sql_query  = "select * from B2R_User_id_MultipleOrders_2000$ a where not exists (select 0 from B2R_User_id_MultipleOrders_2000$_log b where a.order_id = b.order_id ) ",                                         
                    jira_project = "LFO",
                    jira_ticket_type = "Alert",                    
                    jira_ticket_summary = "Core FRAUD ALERT: Core Multiple Orders by the same USER_ID in 24 hours worth more than 2000$ ",
                    jira_ticket_description="Please, check the attached file for details!",
                    sql_log_table_name="B2R_User_id_MultipleOrders_2000$_log"                    
                    )


