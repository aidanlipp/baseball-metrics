import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF

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
            'decel_issue': decel_issue
        }
    }

DECEL_TEMPLATE = """Speed Gain/Deceleration Program

Player Name: {name}

{name}'s exit velocity average was {exit_velo}mph. Based on the swing test results, an area they need to focus on is deceleration. In order for one body part to speed up the other needs to hit the brakes. Once achieved, their body will rotate faster and more efficiently. The drills listed below will help, I recommend 3 sets of 8-10 reps each.

Environment        Day 1                  Day 2
Bat Speed         Cardboard Slider       Cardboard Slider
Flips, short BP   Heels Down,No Stride   Heels Down,No Stride
Default to Tee    Double Tee Stop Swing  Double Tee Stop Swing"""

ROT_ACC_TEMPLATE = """Rotational Acceleration and Sequencing Program

Player Name: {name}

{name}'s exit velocity average was {exit_velo}mph. They were placed in this program because their Rotational Acceleration results averaged {rot_acc}g's (Ideally, we want this 15+). What this means is that they are rotating out of order (sequence), which will reduce their barrel accuracy & rotational speed. The drills listed below will help, I recommend 3 sets of 8 reps of each.

Environment        Day 1                     Day 2
Bat Speed         45 Degree Drill           45 Degree Drill
Flips, short BP   No Stride, 1,2,3 rhythm   No Stride, 1,2,3 rhythm
Default to Tee    PVC Stop Swing            PVC Stop Swing"""

VBA_TEMPLATE = """Vertical Bat Angle (VBA) Program

Player Name: {name}

{name}'s exit velocity average was {exit_velo}mph and their swing test showed {vba_high} swings above -24°. Their average VBA was {avg_vba}°. Ideally, we want to see their bat more vertical. Once achieved, it will allow them to stay "on plane" with the ball longer, which enables them to hit the ball hard when their timing is off. The drills below will help, I recommend 3 sets of 8 reps of each.

Environment                  Day 1                           Day 2
_______________________________________________________________________________
Bat Speed
Flips, short BP if available PVC Torso Turns at Various    PVC Torso Turns at Various
Default to Tee if you need to    Heights                       Heights
                            Double Tee Stop Swing           Double Tee Stop Swing
                            Hinge Against Tee               Hinge Against Tee

Short BP                    Hunt Heaters, Hit the ball      Runner on 3B, Infield In, Hit
                           HARD                            the Ball Hard to the OF

Live/Machine               If Available                     If Available

If you're able to hit a 3rd day you should, If you have access to a machine, work on high velo at
least once per week."""
def create_pdf(content, filename):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, content.split('\n')[0], 0, 1, 'L')  # Title
            self.ln(10)

        def footer(self):
            self.set_y(-30)
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Who Wrote this Report?', 0, 1, 'L')
            self.set_font('Arial', '', 12)
            self.cell(0, 6, 'Dan Kennon', 0, 1, 'L')
            self.cell(0, 6, 'dkennon@elitebaseballtraining.com', 0, 1, 'L')
            self.cell(0, 6, '(575) 520 1174', 0, 1, 'L')

    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    
    # Skip title (already in header)
    content_lines = content.split('\n')[1:]
    
    # Player name
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, content_lines[1], 0, 1, 'L')
    pdf.ln(5)
    
    # Main text
    pdf.set_font('Arial', '', 12)
    for line in content_lines[2:]:
        if "Environment" in line:
            pdf.set_font('Arial', 'B', 12)
        pdf.multi_cell(0, 8, line)
        pdf.set_font('Arial', '', 12)
    
    return pdf.output(dest='S').encode('latin-1')

def generate_report(player_data, stats):
    name = f"{player_data['First Name']} {player_data['Last Name']}"
    
    report_data = {
        'name': name,
        'exit_velo': f"{stats['exit_velo']['avg']:.1f}",
        'rot_acc': f"{stats['rot_acc']['avg']:.1f}",
        'vba_high': stats['swing_issues']['vba_high'],
        'avg_vba': "-24.0"  # Calculate this if needed
    }
    
    issues = stats['swing_issues']
    if issues['vba_issue']:
        template = VBA_TEMPLATE
    elif issues['rot_issue']:
        template = ROT_ACC_TEMPLATE
    else:
        template = DECEL_TEMPLATE
        
    content = template.format(**report_data)
    return create_pdf(content, f"{name}_plan.pdf")

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
            pdf = generate_report(player, stats)
            st.download_button(
                "Download Training Plan",
                pdf,
                f"{player['First Name']}_{player['Last Name']}_plan.pdf",
                "application/pdf"
            )
    else:
        st.warning("No player found")
