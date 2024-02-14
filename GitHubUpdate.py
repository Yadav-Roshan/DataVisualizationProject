import requests
import pandas as pd
import json
import base64

# GitHub repository information
repo_owner = 'Yadav-Roshan'
repo_name = 'DataVisualizationProject'
file_path = 'Origin_Weather.csv'

# Your personal access token
access_token = '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'

# Create a DataFrame with your new data
new_data = {
    'Column1': [1, 2, 3],
    'Column2': ['A', 'B', 'C']
}
df = pd.DataFrame(new_data)

# Convert the DataFrame to CSV format
new_csv_content = df.to_csv(index=False)

# Encode the new content to base64
new_content_base64 = base64.b64encode(new_csv_content.encode('utf-8')).decode('utf-8')

# URL to the raw content of the CSV file
raw_url = f'https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{file_path}'

# Get the current content of the CSV file
response = requests.get(raw_url)
# print(response.json())

if response.status_code == 200:
     # Extract the SHA hash from the response headers
    current_sha = response.headers['ETag'].strip('W/"')  # Remove 'W/"' from the ETag value
    print(current_sha)

    # Create a commit to update the file
    update_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}'
    headers = {
        'Authorization': f'token {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'message': 'Replace CSV file content',
        'content': new_content_base64
    }

    # Send the update request
    update_response = requests.put(update_url, headers=headers, data=json.dumps(data))
    print(update_response.text)

    if update_response.status_code == 200:
        print('CSV file content replaced successfully!')
    else:
        print(f'Failed to replace CSV file content. Status code: {update_response.status_code}')
else:
    print(f'Failed to fetch the CSV file. Status code: {response.status_code}')