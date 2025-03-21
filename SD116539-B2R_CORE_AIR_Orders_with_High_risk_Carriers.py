from jira_sad_alerts_create import *

create_jira_issue(  
                    sql_server = "LTYPRDDWSRSQL00", 
                    sql_database_name = "Infosec",
                    sql_query  = "select * from CORE_AIR_Orders_with_High_risk_Carriers a where not exists (select 0 from CORE_AIR_Orders_with_High_risk_Carriers_log b where a.order_id = b.order_id ) ",                                         
                    jira_project = "LFO",
                    jira_ticket_type = "Alert",                    
                    jira_ticket_summary = "CORE FRAUD ALERT: AIR Orders with High-risk Carriers ",
                    jira_ticket_description="Please, check the attached file for details!",
                    sql_log_table_name="CORE_AIR_Orders_with_High_risk_Carriers_log"                    
                    )


