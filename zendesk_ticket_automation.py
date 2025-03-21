"""
-Zendesk API documentation
https://developer.zendesk.com/api-reference/ticketing/introduction/ 

-Zendesk Postman collection
https://www.postman.com/zendesk-redback/zendesk-public-api/collection/pknuupn/support-api 

NOTE: I had trouble getting this to work as well. The docs aren't quite right.
Use below as Postman Authentication Settings
    Type: Basic Auth
    Username: techapi@bakkt.com/token
    Password: {your_api_token}


-Python example
https://developer.zendesk.com/documentation/ticketing/getting-started/making-requests-to-the-zendesk-api/



"""

import requests
import os

ZENDESK_API_TOKEN = 'zA1YBycER86jOdh1OuJyQsRdDMh6zJQ1lhXkO6sb' #os.getenv('ZENDESK_API_TOKEN')  # Make sure this is correctly set in your environment
ZENDESK_SUBDOMAIN = 'bridge2solutions.zendesk.com' #your_subdomain.zendesk.com'  # Replace with your Zendesk subdomain
ZENDESK_USER_EMAIL = 'techapi@bakkt.com' #you_zendesk_email' # Replace with the Zendesk email address used to access the subdomain

# Check if ZENDESK_API_TOKEN was correctly retrieved from environment
if not ZENDESK_API_TOKEN:
    print('ZENDESK_API_TOKEN environment variable is not set. Exiting.')
    exit()

url = f'https://{ZENDESK_SUBDOMAIN}/api/v2/tickets.json'

auth = f'{ZENDESK_USER_EMAIL}/token', ZENDESK_API_TOKEN

ticket_json = {
                'ticket': {                    
                    'subject': 'Missing VAR ORDER ID - 00000001',
                    'description': 'Please action on this BAC order 00000001 from 08/20/2024 as soon as possible.',
                    'assignee_email': 'techapi@bakkt.com'
                }
            }

# Perform the HTTP GET request
response = requests.post(url, auth=auth,json=ticket_json)
#response.text

# Check for HTTP codes other than 200
if response.status_code != 201:
    print('Status:', response.status_code, 'Problem with the request. Exiting.')
    exit()

# Decode the JSON response into a dictionary and use the data
#data = response.json()

