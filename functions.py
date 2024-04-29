import pandas as pd
from geocodio import GeocodioClient

# Define function to remove specified columns
def remove_columns(df, columns_to_remove):
    return df.drop(columns=[col for col in columns_to_remove if col in df.columns], inplace=False)



# Define function to clean owner names
def clean_name(df, column_name, order, extra_clean):
    if extra_clean:
        df[column_name] = df[column_name].str.replace(',', '')
        df[column_name] = df[column_name].str.replace(r' \S ', ' ', regex=True)

    if order == "Last First":
        df[['Last_Name', 'First_Name']] = df[column_name].str.split(' ', n=1, expand=True)
        df['First_Name'] = df['First_Name'].str.split(' ').str[0]
    elif order == "First Last":
        df[['First_Name', 'Last_Name']] = df[column_name].str.split(' ', n=1, expand=True)
        df['Last_Name'] = df['Last_Name'].str.split(' ').str[0]

    df.drop(column_name, axis=1, inplace=True)
    return df

def clean_addresses(df, address_columns, likely_city='', likely_state='', likely_zip=''):    
    client = GeocodioClient('53cfaaae0ac225aaa25326d606099662963ca2a')
    
    # Create a single string address from the provided columns, converting all elements to strings
    df['full_address'] = df[address_columns].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)
    
    # Fill likely city, state, and zip if provided
    if likely_city:
        df['full_address'] += ' ' + likely_city
    if likely_state:
        df['full_address'] += ' ' + likely_state
    if likely_zip:
        df['full_address'] += ' ' + likely_zip
    
    # Prepare data for API
    address_dict = df['full_address'].to_dict()

    # Geocode addresses
    geocoded_data = client.geocode(list(address_dict.values()))

    # Prepare DataFrame to collect cleaned addresses
    cleaned_addresses = {
        'Clean_Address': [],
        'Clean_City': [],
        'Clean_State': [],
        'Clean_Zip': [],
        'Clean_County': []
    }

    # Extract data from geocoded results
    for i, result in enumerate(geocoded_data):
        if result and result['results']:
            top_result = result['results'][0]['address_components']
            cleaned_addresses['Clean_Address'].append(f"{top_result.get('number', '')} {top_result.get('formatted_street', '').strip()}")
            cleaned_addresses['Clean_City'].append(top_result.get('city', ''))
            cleaned_addresses['Clean_State'].append(top_result.get('state', ''))
            cleaned_addresses['Clean_Zip'].append(top_result.get('zip', ''))
            cleaned_addresses['Clean_County'].append(top_result.get('county', ''))
        else:
            # Append blanks if no results found
            cleaned_addresses['Clean_Address'].append('')
            cleaned_addresses['Clean_City'].append('')
            cleaned_addresses['Clean_State'].append('')
            cleaned_addresses['Clean_Zip'].append('')
            cleaned_addresses['Clean_County'].append('')

    # Create DataFrame from cleaned addresses
    clean_df = pd.DataFrame(cleaned_addresses)

    # Merge the cleaned address information back into the original DataFrame
    df = pd.concat([df, clean_df], axis=1)

    # Optionally, you can drop the temporary 'full_address' column
    df.drop(columns=['full_address'], inplace=True)

    return df
