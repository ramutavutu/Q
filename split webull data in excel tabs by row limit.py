import mysql.connector
import pandas as pd
import os
import time
import xlsxwriter

# Create a target directory for saving Excel files
output_folder = r'R:\Ronaldo TSQL'
output_file = 'DBA-2426.xlsx'
max_rows_per_sheet = 1048576

# Database Connection
conn = mysql.connector.connect(user='',
                        password='',
                        host='127.0.0.1',
                        port='3308',
                        database='bakkt')

cursor = conn.cursor()

# Define the list of states
#states = ['AA','AE','AK','AL','AP','AR','AZ','CA','CO','CT','DC','DE','FL','GA','GU','HI','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MP','MS','MT','NC','ND','NE','NH','NJ','NM','NULL','NV','NY','OH','OK','OR','PA','PR','RI','SC','SD','TN','TX','UT','VA','VI','VT','WA','WI','WV','WY']

# Define the SQL query
query = """
        select 	ppl.created, 
                BIN_TO_UUID(ppl.party_id) party_id,  
                case ppl.address_country
                    when 156 then 'MEX'
                    when 232 then 'USA'
                    when 238 then 'VGB'
                else 
                    'NOT DEFINED'
                end country,
                ppl.address_region,
                ppl.partner_party_ref,
                ppl.level,		 
                ppl.status		
        from partner p
            inner join partner_party_link ppl 
                on ppl.partner_id = p.id		
                and ppl.status = 'ACTIVE'                
        where p.name = 'Webull Pay'
        order by ppl.created
"""
# Create a Pandas Excel writer
writer = pd.ExcelWriter(output_folder+'\\'+output_file, engine='xlsxwriter')

cursor.execute(query)
data = cursor.fetchall()

# Create a Pandas DataFrame from the query results
P_data = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])

# Split the DataFrame into chunks based on the maximum rows
df_chunks = [P_data[i:i + max_rows_per_sheet] for i in range(0, len(P_data), max_rows_per_sheet)]

# Write each chunk to a separate sheet
for i, chunk in enumerate(df_chunks):
    sheet_name = f'Sheet{i + 1}'
    chunk.to_excel(writer, sheet_name=sheet_name, index=False)

# Save the Excel file
writer.close()

# Print a success message
print(f"Query results saved to Excel")