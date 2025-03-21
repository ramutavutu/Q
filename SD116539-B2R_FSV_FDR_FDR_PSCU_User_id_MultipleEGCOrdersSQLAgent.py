from jira_sad_alerts_create import *

create_jira_issue(  
                    sql_server = "LTYPRDDWSRSQL00", 
                    sql_database_name = "Infosec",
                    sql_query  = "select * from B2R_FSV_FDR_FDR_PSCU_User_id_MultipleEGCOrders a where not exists (select 0 from B2R_FSV_FDR_FDR_PSCU_User_id_MultipleEGCOrders_log b where a.order_id = b.order_id ) ",                                         
                    jira_project = "LFO",
                    jira_ticket_type = "Alert",                    
                    jira_ticket_summary = "Core FRAUD ALERT: FSV,FDR,FDR_PSCU Greater than 3 ecard orders in last 24hours (3 or more orders)  ",
                    jira_ticket_description="Please, check the attached file for details!",
                    sql_log_table_name="B2R_FSV_FDR_FDR_PSCU_User_id_MultipleEGCOrders_log"                    
                    )


