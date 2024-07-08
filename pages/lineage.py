##### LIBRARY ######
import random
from glob import glob
from datetime import datetime
import pandas as pd
from functions import process as fp, update as fu
import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge 
from streamlit_flow.layouts import LayeredLayout


##### CONFIG #####
try:
    st.set_page_config(
        page_title='DeFi BI App',
        layout='wide',
        initial_sidebar_state='collapsed'
    )
except:
    pass


##### PAGE ######
def main():
    # initiate variables
    client = None
    df_raw = pd.DataFrame()
    df_edges = pd.DataFrame()
    df_nodes = pd.DataFrame()

    # use latest data
    if df_raw.empty:
        file_paths = glob('data/*.csv')
        if file_paths:
            file_paths.sort()
            last_file = file_paths[-1]
        df_raw = pd.read_csv(last_file)
        df_edges = fp.get_edges(df_raw)
        df_nodes = fp.get_nodes(df_edges)

    # menu bar
    col1, col2, col3, col4, col5 = st.columns([4, 1, 2, 1, 1])
    # select box
    with col1:
        st.markdown(
            """
            <style>
            [data-baseweb="select"] {
                margin-top: -45px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        select_options = df_nodes.table.sort_values().to_list()
        select_index = select_options.index(st.query_params['table']) if 'table' in st.query_params else 0
        selected_table = st.selectbox('', select_options, index=select_index)
        
    # show button
    with col2:
        is_show = st.button('Show lineage')
    # empty space
    with col3:
        pass
    # last refresh
    with col4:
        latest_version = datetime.strptime(last_file.split('.')[0].split('/')[-1].split('_')[-1], '%Y%m%d').strftime('%Y-%m-%d')
        st.markdown(f"<p style='margin-top:5px'>Latest version: {latest_version}</p>", unsafe_allow_html=True)
    # refresh data button
    with col5:
        is_refresh = st.button('Refresh lineage')
        if is_refresh:
            if client == None:
                client = fu.initiate_metabase()
            df_raw_ = fu.run_metabase(client, 2866) # 2866 metabase for defi_bi queries
            if not df_raw.equals(df_raw_):
                timestamp = datetime.now().strftime('%Y%m%d')
                df_raw_.to_csv(f'data/defi_bi_{timestamp}.csv', index=False)
                df_raw = df_raw_.copy()
                del df_raw_
    
    # initiate flow session variables
    if 'nodes' not in st.session_state:
        st.session_state['nodes'] = []
        st.session_state['edges'] = []
        st.session_state['flow_key'] = f'hackable_flow_{random.randint(0, 1000)}'
        is_show = True

    # initiate flow component  
    streamlit_flow(
        st.session_state['flow_key'],
        st.session_state['nodes'],
        st.session_state['edges'],
        height=750,
        layout=LayeredLayout(direction='right', horizontal_spacing=150, vertical_spacing=30, node_node_spacing=30, node_layer_spacing=100),
        fit_view=True
    )
    
    # check if data is not empty
    if not df_raw.empty:
        # filter data based on select box input
        df_edges_ = fp.get_lineage(df_edges, selected_table)
        df_nodes_ = fp.get_nodes(df_edges_)

        # button to refresh lineage
        if is_show and selected_table:
            flow_key = st.session_state['flow_key']
            if flow_key in st.session_state and flow_key:
                # generate nodes and edges
                st.session_state['nodes'] = [
                    StreamlitFlowNode(
                        id=row.table,
                        pos=(0,0),
                        data={'label': row.table},
                        node_type=row.type,
                        source_position='right',
                        target_position='left',
                        style={'word-wrap': 'break-word', 'backgroundColor': '#F8DE7E'} if row.table == selected_table else {'word-wrap': 'break-word', 'width': 200}
                    ) for row in df_nodes_.itertuples(index=False)
                ]
                st.session_state['edges'] = [
                    StreamlitFlowEdge(
                        f'{row.source}-{row.table}',
                        row.source,
                        row.table,
                        animated=True
                    ) for row in df_edges_.itertuples(index=False)
                ]
                # delete session and rerun to refresh
                del st.session_state[flow_key]
                st.session_state['flow_key'] = f'hackable_flow_{random.randint(0, 1000)}'
                st.rerun()


if __name__ == "__main__":
    main()