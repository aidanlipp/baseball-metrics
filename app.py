import streamlit as st
import pandas as pd
import numpy as np
from docx import Document
import io

def load_data():
    return pd.read_csv('Testing Metrics.csv')

def extract_age_group(age_str):
    return int(age_str.replace('u', ''))

def calculate_percentile(value, series):
    return round(100 * (series <= value).mean())

def calculate_age_based_stats(player_data, df):
    df['age_group'] = df['age'].apply(extract_age_group)
    player_age_group = extract_age_group(player_data['age'])
    age_group_df = df[df['age_group'] == player_age_group]
    
    bat_speeds = [float(player_data[f'Bat Speed {i}']) for i in range(1,6)]
    rot_accs = [float(player_data[f'Rot. Acc. {i}']) for i in range(1,6)]
    exit_velos = [float(player_data[f'Exit Velo {i}']) for i in range(1,6)]
    vbas = [float(player_data[f'VBA {i}']) for i in range(1,6)]
    
    age_bat_speeds = age_group_df[[f'Bat Speed {i}' for i in range(1,6)]].mean(axis=1)
    age_rot_accs = age_group_df[[f'Rot. Acc. {i}' for i in range(1,6)]].mean(axis=1)
    age_exit_velos = age_group_df[[f'Exit Velo {i}' for i in range(1,6)]].mean(axis=1)
    
    age_max_bat_speeds = age_group_df[[f'Bat Speed {i}' for i in range(1,6)]].max(axis=1)
    age_max_rot_accs = age_group_df[[f'Rot. Acc. {i}' for i in range(1,6)]].max(axis=1)
    age_max_exit_velos = age_group_df[[f'Exit Velo {i}' for i in range(1,6)]].max(axis=1)

    vba_high = sum(1 for x in vbas if x > -24)
    vba_low = sum(1 for x in vbas if x < -45)
    avg_rot_acc = np.mean(rot_accs)
    avg_vba = np.mean(vbas)
    
    vba_issue = vba_high >= 3 or vba_low >= 3
    rot_issue = avg_rot_acc < 7.0
    decel_issue = not (vba_issue or rot_issue)
    
    return {
        'age_group': player_age_group,
        'bat_speed': {
            'avg': np.mean(bat_speeds),
            'percentile': calculate_percentile(np.mean(bat_speeds), age_bat_speeds)
        },
        'max_bat_speed': {
            'value': np.max(bat_speeds),
            'percentile': calculate_percentile(np.max(bat_speeds), age_max_bat_speeds)
        },
        'rot_acc': {
            'avg': avg_rot_acc,
            'percentile': calculate_percentile(np.mean(rot_accs), age_rot_accs)
        },
        'max_rot_acc': {
            'value': np.max(rot_accs),
            'percentile': calculate_percentile(np.max(rot_accs), age_max_rot_accs)
        },
        'exit_velo': {
            'avg': np.mean(exit_velos),
            'percentile': calculate_percentile(np.mean(exit_velos), age_exit_velos)
        },
        'max_exit_velo': {
            'value': np.max(exit_velos),
            'percentile': calculate_percentile(np.max(exit_velos), age_max_exit_velos)
        },
        'swing_issues': {
            'vba_high': vba_high,
            'vba_low': vba_low,
            'vba_issue': vba_issue,
            'rot_issue': rot_issue,
            'decel_issue': decel_issue,
            'avg_vba': avg_vba
        }
    }

def generate_report(player_data, stats):
    if stats['swing_issues']['vba_issue']:
        doc = Document('templates/VBA_template.docx')
    elif stats['swing_issues']['rot_issue']:
        doc = Document('templates/RotAcc_template.docx')
    else:
        doc = Document('templates/Decel_template.docx')
    
    # Replace placeholders in paragraphs
    for paragraph in doc.paragraphs:
        text = paragraph.text
        if '{name}' in text:
            text = text.replace('{name}', f"{player_data['First Name']} {player_data['Last Name']}")
        if '{exit_velo}' in text:
            text = text.replace('{exit_velo}', f"{stats['exit_velo']['avg']:.1f}")
        if '{rot_acc}' in text:
            text = text.replace('{rot_acc}', f"{stats['rot_acc']['avg']:.1f}")
        if '{vba_high}' in text:
            text = text.replace('{vba_high}', str(stats['swing_issues']['vba_high']))
        if '{avg_vba}' in text:
            text = text.replace('{avg_vba}', f"{stats['swing_issues']['avg_vba']:.1f}")
        paragraph.text = text

    # Save to memory
    docx_stream = io.BytesIO()
    doc.save(docx_stream)
    docx_stream.seek(0)
    return docx_stream

st.set_page_config(page_title="Baseball Metrics Dashboard", layout="wide")
st.title("Player Metrics Dashboard")

df = load_data()

search = st.text_input("", placeholder="Search by name...")
if search:
    matches = df[df['First Name'].str.contains(search, case=False) | 
                 df['Last Name'].str.contains(search, case=False)]
    if not matches.empty:
        player = matches.iloc[0]
        stats = calculate_age_based_stats(player, df)
        
        st.header(f"{player['First Name']} {player['Last Name']} ({player['age']})")
        
        st.subheader("Average Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Bat Speed (mph)", 
                     f"{stats['bat_speed']['avg']:.1f}",
                     f"{stats['bat_speed']['percentile']}%ile in {stats['age_group']}u")
        with col2:
            st.metric("Avg Rotational Acceleration (g)", 
                     f"{stats['rot_acc']['avg']:.1f}",
                     f"{stats['rot_acc']['percentile']}%ile in {stats['age_group']}u")
        with col3:
            st.metric("Avg Exit Velocity (mph)", 
                     f"{stats['exit_velo']['avg']:.1f}",
                     f"{stats['exit_velo']['percentile']}%ile in {stats['age_group']}u")
        
        st.subheader("Max Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Max Bat Speed (mph)", 
                     f"{stats['max_bat_speed']['value']:.1f}",
                     f"{stats['max_bat_speed']['percentile']}%ile in {stats['age_group']}u")
        with col2:
            st.metric("Max Rotational Acceleration (g)", 
                     f"{stats['max_rot_acc']['value']:.1f}",
                     f"{stats['max_rot_acc']['percentile']}%ile in {stats['age_group']}u")
        with col3:
            st.metric("Max Exit Velocity (mph)", 
                     f"{stats['max_exit_velo']['value']:.1f}",
                     f"{stats['max_exit_velo']['percentile']}%ile in {stats['age_group']}u")
        
        st.subheader("Swing Issues")
        issues = stats['swing_issues']
        if issues['vba_issue']:
            message = []
            if issues['vba_high'] >= 3:
                message.append(f"{issues['vba_high']} swings above -24°")
            if issues['vba_low'] >= 3:
                message.append(f"{issues['vba_low']} swings below -45°")
            st.warning("VBA Issue: " + " and ".join(message))
        if issues['rot_issue']:
            st.warning(f"Rotational Acceleration Issue: Average below 7.0g")
        if issues['decel_issue']:
            st.success("Deceleration Pattern")
        
        if st.button("Export Training Reports", type="primary"):
            docx_file = generate_report(player, stats)
            st.download_button(
                "Download Training Plan",
                docx_file,
                f"{player['First Name']}_{player['Last Name']}_plan.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.warning("No player found")
