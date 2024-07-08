##### LIBRARY ######
import streamlit as st


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
    st.markdown('hello')


if __name__ == "__main__":
    main()