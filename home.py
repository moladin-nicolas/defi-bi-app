##### LIBRARY #####
import streamlit as st
from pages import lineage, query


##### CONFIG #####
try:
    st.set_page_config(
        page_title='DeFi BI App',
        layout='wide'
    )
except:
    pass


##### PAGE #####
def main():
    st.title('DeFi BI App')
    st.write('### Welcome!')
    st.write("""
    This application is designed to help Business Intelligence operations.
    
    **Navigation Instructions:**
    - Use the sidebar on the left to switch between different pages.
    - Each page contains specific tool for BI operations.
             
    **Pages:**
    - Home: This page, introduction and navigation instructions.
    - Lineage: Visualization of data lineage.
    - Query: Documentation of queries.

    Feel free to explore and let us know if you have any questions or need further assistance.
    """)
    

if __name__ == "__main__":
    main()
