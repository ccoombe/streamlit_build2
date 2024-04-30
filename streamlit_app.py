import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder
from functions import remove_columns, clean_name, clean_addresses
import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

authenticator.login()

if st.session_state["authentication_status"]:
    authenticator.logout()

    st.title('Welcome to the Data Processing Tool')
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Uploaded Data:")
        st.dataframe(df)
    
        clean_names = st.checkbox('Clean names by splitting them into First and Last names')
        remove_cols = st.checkbox('Remove columns')
        clean_addresses_option = st.checkbox('Clean Addresses')
    
        if clean_names:
            column_to_process = st.selectbox('Select column to split into First Name and Last Name', df.columns)
            extra_clean = st.checkbox('Remove commas and 1 character long strings from the selected column')
            name_order = st.radio("Select name order in the column", ('Last First', 'First Last'))
            st.session_state.name_settings = (column_to_process, name_order, extra_clean)
    
        if remove_cols:
            columns_to_remove = st.multiselect('Select columns to remove', df.columns)
            st.session_state.remove_settings = columns_to_remove
    
        if clean_addresses_option:
            # Dropdown selectors for address components based on available columns
            address_columns = [st.selectbox('Address Column 1 (required)', df.columns)]
            address_columns += [st.selectbox('Address Column 2 (optional)', [''] + list(df.columns))]
            address_columns += [st.selectbox('Address Column 3 (optional)', [''] + list(df.columns))]
            address_columns += [st.selectbox('Address Column 4 (optional)', [''] + list(df.columns))]
            address_columns = [col for col in address_columns if col]  # Remove empty selections
    
            likely_city = st.text_input('Likely City (optional)')
            likely_state = st.text_input('Likely State (optional)')
            likely_zip = st.text_input('Likely Zip (optional)')
    
        if st.button('Process Data'):
            if clean_names and 'name_settings' in st.session_state:
                df = clean_name(df, *st.session_state.name_settings)
            if remove_cols and 'remove_settings' in st.session_state:
                df = remove_columns(df, st.session_state.remove_settings)
            if clean_addresses_option:
                df = clean_addresses(df, address_columns, likely_city, likely_state, likely_zip)
    
            st.write('Processed Data:', df)
            AgGrid(df, editable=True)

            if st.button('Confirm Updates'):
                # Process updates here
                pass

            # Download button for the processed data
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download processed data", csv, "processed_data.csv", "text/csv", key='download-csv')
    

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
