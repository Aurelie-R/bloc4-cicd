from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import os
from urllib.error import URLError

@st.cache_data
def get_data() -> pd.DataFrame:
    conn = st.connection(
        "postgresql",
        type="sql",
        url=os.environ['BACKEND_STORE_URI']
    )
    df = conn.query("SELECT * FROM transactions WHERE trans_date_trans_time >= TO_CHAR(CURRENT_DATE - INTERVAL '1 day', 'YYYY-MM-DD') || ' 00:00:00' AND trans_date_trans_time < TO_CHAR(CURRENT_DATE, 'YYYY-MM-DD') || ' 00:00:00'")
    return df
JOUR_HIER = (pd.Timestamp.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
st.title(f"Tableau des transactions bancaires du {JOUR_HIER}")

try:
    df = get_data()
    st.dataframe(data = df, width="content", hide_index=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Nombre de transactions", value=len(df))
        st.metric(label="Montant total des transactions", value=f"${df['amt'].sum():,.2f}")
    with col2:
        st.metric(label="Nombre de transactions frauduleuses", value=len(df[df['prediction'] == 1]))
        st.metric(label="Montant total des transactions frauduleuses", value=f"${df[df['prediction'] == 1]['amt'].sum():,.2f}")

except URLError as e:
    st.error(f"This demo requires internet access. Connection error: {e.reason}")
