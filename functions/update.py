##### LIBRARY #####
import pandas as pd
from metabasepy import Client, MetabaseTableParser
import streamlit as st

##### METABASE #####
def initiate_metabase():
    if 'METABASE_USERNAME' in st.secrets:
        metabase_username = st.secrets['METABASE_USERNAME']
        metabase_password = st.secrets['METABASE_PASSWORD']
        client = Client(metabase_username, metabase_password, 'https://metabase.moladin.com/')
        client.authenticate()
    else:
        client = None
    # return client
    return client

def run_metabase(client, card_id):
    # get preview table
    response = client.cards.query(str(card_id))
    preview_table = MetabaseTableParser.get_table(response)
    column_names = [col['display_name'] for col in preview_table.cols]
    # get full table if rows = 2000
    if preview_table.row_count == 2000:
        json_result = cli.cards.download(card_id=str(card_id), format='json')
        df = pd.DataFrame(json_result)
        # arrange column orders
        df = df[column_names]
    else:
        df = pd.DataFrame(preview_table.rows, columns=column_names)
    # return result
    return df