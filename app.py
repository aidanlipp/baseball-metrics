import streamlit as st
import pandas as pd
import numpy as np

def load_data():
    return pd.read_csv('Testing Metrics.csv')

def calculate_percentile(value, series):
    return round(100 * (series <= value).mean())

def calculate_stats(player_data, df):
    bat_speeds = [float(player_data[f'Bat Speed {i}']) for i in range(1,6)]
    rot_accs = [float(player_data[f'Rot. Acc. {i}']) for i in range(1,6)]
    exit_velos = [float(player_data[f'Exit Velo {i}']) for i in range(1,6)]
    vbas = [float(player_data[f'VBA {i}']) for i in range(1,6)]
    
    # Calculate averages for all players
    all_bat_speeds = df[[f'Bat Speed {i}' for i in range(1,6)]].mean(axis=1)
    all_rot_accs = df[[f'Rot. Acc. {i}' for i in range(1,6)]].mean(axis=1)
    all_exit_velos = df[[f'Exit Velo {i}' for i in range(1,6)]].mean(axis=1)
    
    # Calculate max values for all players
    all_max_bat_speeds = df[[f'Bat Speed {i}' for i in range(1,6)]].max(axis=1)
    all_max_rot_accs = df[[f'Rot. Acc. {i}' for i in range(1,6)]].max(axis=1)
    all_max_exit_velos = df[[f'Exit Velo {i}' for i in range(1,6)]].max(axis=1)
    
    return {
        'bat_speed': {
            'avg': np.mean(bat_speeds),
            'percentile': calculate_percentile(np.mean(bat_speeds), all_bat_speeds)
        },
        'max_bat_speed': {
            'value': np.max(bat_speeds),
            'percentile': calculate_percentile(np.max(bat_speeds), all_max_bat_speeds)
        },
        'rot_acc': {
            'avg': np.mean(rot_accs),
            'percentile': calculate_percentile(np.mean(rot_accs), all_rot_accs)
        },
        'max_rot_acc': {
            'value': np.max(rot_accs),
            'percentile': calculate_percentile(np.max(rot_accs), all_max_rot_accs)
        },
        'exit_velo': {
            'avg': np.mean(exit_velos),
            'percentile': calculate_percentile(np.mean(exit_velos), all_exit_velos)
        },
        'max_exit_velo': {
            'value': np.max(exit_velos),
            'percentile': calculate_percentile(np.max(exit_velos), all_max_exit_velos)
        },
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
        stats = calculate_stats(player, df)
        
        st.header(f"{player['First Name']} {player['Last Name']}")
        
        # Average metrics
        st.subheader("Average Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Bat Speed (mph)", 
                     f"{stats['bat_speed']['avg']:.1f}",
                     f"{stats['bat_speed']['percentile']}%ile")
        with col2:
            st.metric("Avg Rotational Acceleration (g)", 
                     f"{stats['rot_acc']['avg']:.1f}",
                     f"{stats['rot_acc']['percentile']}%ile")
        with col3:
            st.metric("Avg Exit Velocity (mph)", 
                     f"{stats['exit_velo']['avg']:.1f}",
                     f"{stats['exit_velo']['percentile']}%ile")
        
        # Max metrics
        st.subheader("Max Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Max Bat Speed (mph)", 
                     f"{stats['max_bat_speed']['value']:.1f}",
                     f"{stats['max_bat_speed']['percentile']}%ile")
        with col2:
            st.metric("Max Rotational Acceleration (g)", 
                     f"{stats['max_rot_acc']['value']:.1f}",
                     f"{stats['max_rot_acc']['percentile']}%ile")
        with col3:
            st.metric("Max Exit Velocity (mph)", 
                     f"{stats['max_exit_velo']['value']:.1f}",
                     f"{stats['max_exit_velo']['percentile']}%ile")
        
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
