import streamlit as st
import pandas as pd
import numpy as np

def load_data():
    return pd.read_csv('Testing Metrics.csv')

def calculate_stats(player_data):
    bat_speeds = [float(player_data[f'Bat Speed {i}']) for i in range(1,6)]
    rot_accs = [float(player_data[f'Rot. Acc. {i}']) for i in range(1,6)]
    exit_velos = [float(player_data[f'Exit Velo {i}']) for i in range(1,6)]
    vbas = [float(player_data[f'VBA {i}']) for i in range(1,6)]
    
    return {
        'bat_speed': {'avg': np.mean(bat_speeds), 'max': np.max(bat_speeds)},
        'rot_acc': {'avg': np.mean(rot_accs), 'max': np.max(rot_accs)},
        'exit_velo': {'avg': np.mean(exit_velos), 'max': np.max(exit_velos)},
        'vba_count': sum(1 for x in vbas if x > -24),
        'dece': any(-30 <= x <= -20 for x in vbas),
        'gs': any(-40 <= x <= -30 for x in vbas)
    }

st.set_page_config(page_title="Baseball Metrics Dashboard", layout="wide")
st.title("Player Metrics Dashboard")

df = load_data()

search = st.text_input("", placeholder="Search by name...")
if search:
    matches = df[df['First Name'].str.contains(search, case=False) | 
                 df['Last Name'].str.contains(search, case=False)]
    if not matches.empty:
        player = matches.iloc[0]
        stats = calculate_stats(player)
        
        st.header(f"{player['First Name']} {player['Last Name']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Bat Speed (mph)", 
                     f"{stats['bat_speed']['avg']:.1f}", 
                     f"Max: {stats['bat_speed']['max']:.1f}")
        with col2:
            st.metric("Rotational Acceleration (g)", 
                     f"{stats['rot_acc']['avg']:.1f}", 
                     f"Max: {stats['rot_acc']['max']:.1f}")
        with col3:
            st.metric("Exit Velocity (mph)", 
                     f"{stats['exit_velo']['avg']:.1f}", 
                     f"Max: {stats['exit_velo']['max']:.1f}")
        
        st.subheader("Swing Issues")
        st.write(f"{stats['vba_count']} swings above -24°")
        
        if stats['dece']:
            st.success("✓ Dece")
        if stats['gs']:
            st.success("✓ G's")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export Training Reports", type="primary"):
                st.success("Reports exported!")
        with col2:
            st.markdown("[View Deceleration Report]()")
    else:
        st.warning("No player found")
