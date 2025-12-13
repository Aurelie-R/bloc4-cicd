from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import os
from urllib.error import URLError

# Charger les variables d'environnement
load_dotenv()
BACKEND_STORE_URI = os.getenv("BACKEND_STORE_URI")
TABLE_NAME = os.getenv("TABLE_NAME")

st.set_page_config(
    page_title="Rapport de Fraudes",
    page_icon="🔍",
    layout="wide",  # ← C'est la clé !
    initial_sidebar_state="expanded"
)

@st.cache_data
def get_data(date_deb=None, date_fin=None) -> pd.DataFrame:
    # Utilisation de valeurs par défaut si aucun argument n'est fourni
    if date_deb is None:
        date_deb = pd.Timestamp.now() - pd.Timedelta(days=1)
    if date_fin is None:
        date_fin = pd.Timestamp.now()
    
    conn = st.connection(
        "postgresql",
        type="sql",
        url=BACKEND_STORE_URI
    )
    df = conn.query(
        f"SELECT * FROM {TABLE_NAME} "
        f"WHERE trans_date_trans_time >= '{date_deb.date()}' "
        f"AND trans_date_trans_time < '{date_fin.date()}';"
    )
    return df

st.title("Rapport de Fraudes")

# --- Initialisation du session_state ---
if 'dates_actives' not in st.session_state:
    st.session_state.dates_actives = None
if 'df' not in st.session_state:
    st.session_state.df = None

# --- Chargement initial des données ---
if st.session_state.df is None:
    st.session_state.df = get_data()
    if not st.session_state.df.empty:
        # Convertir en datetime si nécessaire
        if not pd.api.types.is_datetime64_any_dtype(st.session_state.df['trans_date_trans_time']):
            st.session_state.df['trans_date_trans_time'] = pd.to_datetime(st.session_state.df['trans_date_trans_time'])
        
        min_date = st.session_state.df['trans_date_trans_time'].min().date()
        max_date = st.session_state.df['trans_date_trans_time'].max().date()
        st.session_state.dates_actives = [min_date, max_date]

df = st.session_state.df

# --- Sidebar ---
if not df.empty:
    st.sidebar.header("Filtres")
    
    min_date = df['trans_date_trans_time'].min().date()
    max_date = df['trans_date_trans_time'].max().date()
    
    # Sélecteur de dates (ne déclenche PAS le rechargement)
    date_range = st.sidebar.date_input(
        "Sélectionnez la plage de dates",
        value=st.session_state.dates_actives if st.session_state.dates_actives else [min_date, max_date]
    )
    
    # Bouton de rafraîchissement - SEUL déclencheur du rechargement
    if st.sidebar.button("🔄 Appliquer les filtres"):
        if len(date_range) == 2:
            date_debut_selected, date_fin_selected = date_range
            
            # Recharger les données avec les nouvelles dates
            get_data.clear()
            st.session_state.df = get_data(
                date_deb=pd.Timestamp(date_debut_selected),
                date_fin=pd.Timestamp(date_fin_selected) + pd.Timedelta(days=1)
            )
            st.session_state.dates_actives = [date_debut_selected, date_fin_selected]
            st.rerun()
        else:
            st.sidebar.warning("⚠️ Veuillez sélectionner une plage de dates complète")
    
    # Afficher les dates actuellement appliquées
    if st.session_state.dates_actives:
        st.sidebar.info(f"📅 Période affichée : {st.session_state.dates_actives[0]} au {st.session_state.dates_actives[1]}")
    
    # --- Affichage des données ---
    if st.checkbox('Afficher les données brutes'):
        st.subheader('Données brutes')
        st.write(df)    
    # st.markdown("### Aperçu des données")
    # st.dataframe(data=df, width='stretch', hide_index=True)
    
    st.markdown("### Statistiques clés")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="Nombre de transactions", value=len(df))
        st.metric(
            label="Montant total des transactions",
            value=f"${df['amt'].sum():,.2f}"
        )
    
    with col2:
        nb_fraudes = len(df[df['fraud_pred'] == 1])
        montant_fraudes = df[df['fraud_pred'] == 1]['amt'].sum()
        
        st.metric(
            label="Nombre de transactions frauduleuses",
            value=nb_fraudes
        )
        st.metric(
            label="Montant total des transactions frauduleuses",
            value=f"${montant_fraudes:,.2f}"
        )
        
        # Taux de fraude
        if len(df) > 0:
            taux_fraude = (nb_fraudes / len(df)) * 100
            st.metric(
                label="Taux de fraude",
                value=f"{taux_fraude:.2f}%"
            )


    st.markdown("---")
    # --- Diagramme circulaire ---
    st.subheader("Répartition par catégorie")

    # Créer deux colonnes
    col1, col2 = st.columns(2)

    # --- Diagramme 1 : toutes les transactions ---
    df_donut_all = df.groupby('category').size().reset_index(name='count')
    fig_all = px.pie(
        df_donut_all,
        names='category',
        values='count',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    # Afficher les labels sur/autour des secteurs
    fig_all.update_traces(
        textposition='outside',  # 'inside', 'outside', ou 'auto'
        textinfo='label+percent'  # Affiche le nom et le pourcentage
    )
    fig_all.update_layout(showlegend=False)  # Masquer la légende externe
    col1.subheader("Toutes les transactions")
    col1.plotly_chart(fig_all)

    # --- Diagramme 2 : uniquement les fraudes ---
    if not df[df['is_fraud'] == 1].empty:
        df_donut_fraud = df[df['is_fraud'] == 1].groupby('category').size().reset_index(name='count')
        fig_fraud = px.pie(
            df_donut_fraud,
            names='category',
            values='count',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        # Afficher les labels sur/autour des secteurs
        fig_fraud.update_traces(
            textposition='outside',  # 'inside', 'outside', ou 'auto'
            textinfo='label+percent'  # Affiche le nom et le pourcentage
        )
        fig_fraud.update_layout(showlegend=False)  # Masquer la légende externe
        col2.subheader("Transactions frauduleuses")
        col2.plotly_chart(fig_fraud)
    else:
        col2.info("Aucune transaction frauduleuse pour cette période.")

else:
    st.warning("⚠️ Aucune donnée disponible.")