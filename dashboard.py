import streamlit as st
import pandas as pd
import requests
import json

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Fantasy NBA Assistant", layout="wide")

st.title("🏀 Fantasy NBA Assistant (8-Cat)")

# Sidebar for controls
st.sidebar.header("Controls")
if st.sidebar.button("Run Data Ingestion"):
    with st.spinner("Ingesting data from NBA API..."):
        try:
            response = requests.post(f"{API_URL}/ingest", json={"days": 15})
            if response.status_code == 200:
                st.sidebar.success("Ingestion started in background!")
            else:
                st.sidebar.error(f"Error: {response.text}")
        except Exception as e:
             st.sidebar.error(f"Failed to connect to API: {e}")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Trade Analyzer", "Player Explorer", "My Teams", "Leagues"])

# Helper to get players
@st.cache_data(ttl=60)
def get_players():
    try:
        r = requests.get(f"{API_URL}/players")
        if r.status_code == 200:
            return r.json()
    except:
        return []
    return []

@st.cache_data(ttl=60)
def get_stats():
    try:
        r = requests.get(f"{API_URL}/stats")
        if r.status_code == 200:
            return pd.DataFrame(r.json())
    except:
        return pd.DataFrame()
    return pd.DataFrame()

def get_teams():
    try:
        r = requests.get(f"{API_URL}/teams")
        if r.status_code == 200:
            return r.json()
    except:
        return []
    return []

def get_leagues():
    try:
        r = requests.get(f"{API_URL}/leagues")
        if r.status_code == 200:
            return r.json()
    except:
        return []
    return []

def get_team_players(team_id):
    try:
        r = requests.get(f"{API_URL}/teams/{team_id}/players")
        if r.status_code == 200:
            return r.json()
    except:
        return []
    return []

players = get_players()
player_map = {p['full_name']: p['id'] for p in players} if players else {}
reverse_map = {p['id']: p['full_name'] for p in players} if players else {}

with tab1:
    st.header("Daily Recommendations")
    
    st.write("Select your team to see lineup recommendations based on Z-scores.")
    
    # Check for persisted teams first
    teams = get_teams()
    team_options = {t['name']: t['id'] for t in teams}
    
    use_persisted = st.checkbox("Use Saved Team", value=True if teams else False)
    
    roster_ids = []
    
    if use_persisted and teams:
        selected_team_name = st.selectbox("Select Team", list(team_options.keys()))
        if selected_team_name:
            team_id = team_options[selected_team_name]
            team_players = get_team_players(team_id)
            roster_ids = [p['id'] for p in team_players]
            st.info(f"Loaded {len(roster_ids)} players from {selected_team_name}")
    else:
        my_team = st.multiselect("My Roster", options=list(player_map.keys()), key="dashboard_roster")
        if my_team:
            roster_ids = [player_map[name] for name in my_team]
    
    if st.button("Get Recommendations"):
        if not roster_ids:
            st.warning("Please select players or a team.")
        else:
            try:
                response = requests.post(f"{API_URL}/recommend/lineup", json=roster_ids)
                if response.status_code == 200:
                    df = pd.DataFrame(response.json())
                    if not df.empty:
                        # Formatting
                        cols = ['full_name', 'z_total'] + [c for c in df.columns if c.startswith('z_') and c != 'z_total']
                        st.dataframe(df[cols].style.background_gradient(cmap='RdYlGn', subset=['z_total']))
                    else:
                        st.info("No stats available for selected players.")
            except Exception as e:
                st.error(f"API Error: {e}")

with tab2:
    st.header("Trade Analyzer")
    
    col1, col2 = st.columns(2)
    
    teams = get_teams()
    team_options = {t['name']: t['id'] for t in teams}
    
    # Team A Selection
    with col1:
        st.subheader("Team A (You)")
        use_saved_a = st.checkbox("Use Saved Team A", key="saved_a")
        
        team_a_ids = []
        if use_saved_a and teams:
            t_name_a = st.selectbox("Select Team A", list(team_options.keys()), key="sel_a")
            if t_name_a:
                t_players = get_team_players(team_options[t_name_a])
                team_a_ids = [p['id'] for p in t_players]
        else:
            sel_a = st.multiselect("Select Roster A", options=list(player_map.keys()), key="man_a")
            if sel_a:
                team_a_ids = [player_map[p] for p in sel_a]
                
        # Sending Players (must be from roster)
        sending_names = [reverse_map.get(pid, str(pid)) for pid in team_a_ids if pid in reverse_map]
        sending = st.multiselect("Sending", options=sending_names, key="sending")
        
    # Team B Selection
    with col2:
        st.subheader("Team B (Opponent)")
        use_saved_b = st.checkbox("Use Saved Team B", key="saved_b")
        
        team_b_ids = []
        if use_saved_b and teams:
            t_name_b = st.selectbox("Select Team B", list(team_options.keys()), key="sel_b")
            if t_name_b:
                t_players = get_team_players(team_options[t_name_b])
                team_b_ids = [p['id'] for p in t_players]
        else:
            sel_b = st.multiselect("Select Roster B", options=list(player_map.keys()), key="man_b")
            if sel_b:
                team_b_ids = [player_map[p] for p in sel_b]
                
        # Receiving Players (must be from roster)
        receiving_names = [reverse_map.get(pid, str(pid)) for pid in team_b_ids if pid in reverse_map]
        receiving = st.multiselect("Receiving", options=receiving_names, key="receiving")
        
    if st.button("Analyze Trade"):
        if not sending or not receiving:
            st.error("Please select players to trade.")
        else:
            payload = {
                "team_a_roster": team_a_ids,
                "team_b_roster": team_b_ids,
                "players_to_b": [player_map[p] for p in sending],
                "players_to_a": [player_map[p] for p in receiving]
            }
            
            try:
                r = requests.post(f"{API_URL}/analyze/trade", json=payload)
                if r.status_code == 200:
                    data = r.json()
                    
                    st.write("### Impact Analysis")
                    
                    cA, cB = st.columns(2)
                    with cA:
                        diff_a = data['team_a']['diff']
                        st.metric("Team A Impact (Z-Score)", f"{diff_a:.2f}", delta_color="normal" if diff_a > 0 else "inverse")
                        st.json(data['team_a'])
                        
                    with cB:
                        diff_b = data['team_b']['diff']
                        st.metric("Team B Impact (Z-Score)", f"{diff_b:.2f}", delta_color="normal" if diff_b > 0 else "inverse")
                        st.json(data['team_b'])
            except Exception as e:
                st.error(f"Error: {e}")

with tab3:
    st.header("Player Explorer")
    st.write("View all player Z-scores.")
    
    df_stats = get_stats()
    if not df_stats.empty:
        # Reorder columns
        cols = ['full_name', 'games', 'z_total', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'FG3M', 'FG_PCT', 'FT_PCT']
        # Filter existing cols
        cols = [c for c in cols if c in df_stats.columns]
        
        st.dataframe(df_stats[cols].sort_values('z_total', ascending=False))
    else:
        st.info("No stats available. Please run ingestion.")

with tab4:
    st.header("My Teams")
    
    st.subheader("Create New Team")
    new_team_name = st.text_input("Team Name")
    new_team_owner = st.text_input("Owner Name")
    
    leagues = get_leagues()
    league_opts = {l['name']: l['id'] for l in leagues}
    sel_league = st.selectbox("Assign to League (Optional)", ["None"] + list(league_opts.keys()))
    
    if st.button("Create Team"):
        if new_team_name:
            payload = {"name": new_team_name, "owner_name": new_team_owner}
            if sel_league != "None":
                payload["league_id"] = league_opts[sel_league]
                
            try:
                r = requests.post(f"{API_URL}/teams", json=payload)
                if r.status_code == 200:
                    st.success(f"Team '{new_team_name}' created!")
                    st.rerun()
                else:
                    st.error("Failed to create team")
            except Exception as e:
                st.error(f"API Error: {e}")
                
    st.divider()
    
    st.subheader("Manage Teams")
    teams = get_teams()
    if teams:
        team_options = {t['name']: t['id'] for t in teams}
        selected_team = st.selectbox("Select Team to Manage", list(team_options.keys()))
        
        if selected_team:
            team_id = team_options[selected_team]
            
            # View Roster
            current_players = get_team_players(team_id)
            if current_players:
                st.write("Current Roster:")
                st.table(pd.DataFrame(current_players)[['full_name', 'position', 'team_abbreviation']])
            else:
                st.info("No players in roster.")
                
            # Add Player
            st.write("Add Player")
            add_p_name = st.selectbox("Select Player", options=list(player_map.keys()), key="add_p_sel")
            if st.button("Add to Roster"):
                if add_p_name:
                    p_id = player_map[add_p_name]
                    try:
                        r = requests.post(f"{API_URL}/teams/{team_id}/add_player", json={"player_id": p_id})
                        if r.status_code == 200:
                            st.success(f"Added {add_p_name}")
                            st.rerun()
                        else:
                            st.error(f"Failed to add: {r.text}")
                    except Exception as e:
                         st.error(f"API Error: {e}")

with tab5:
    st.header("Leagues")
    
    st.subheader("League Setup Wizard (Bulk Import)")
    leagues = get_leagues()
    l_opts = {l['name']: l['id'] for l in leagues}
    
    if leagues:
        sel_l_import = st.selectbox("Select League for Import", list(l_opts.keys()), key="import_league")
        st.write("Paste JSON map of teams and rosters: `{\"Team A\": [\"Steph Curry\", \"LeBron James\"], ...}`")
        import_data = st.text_area("Roster JSON")
        
        if st.button("Run Import Wizard"):
            if import_data:
                try:
                    roster_map = json.loads(import_data)
                    lid = l_opts[sel_l_import]
                    with st.spinner("Importing..."):
                        r = requests.post(f"{API_URL}/leagues/{lid}/import_rosters", json={"roster_map": roster_map})
                        if r.status_code == 200:
                            report = r.json()
                            st.success(f"Import Complete! Created {report['teams_created']} teams, added {report['players_added']} players.")
                            if report['players_not_found']:
                                st.warning("The following players were not found:")
                                st.table(pd.DataFrame(report['players_not_found']))
                        else:
                             st.error(f"Import Failed: {r.text}")
                except json.JSONDecodeError:
                    st.error("Invalid JSON format.")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.warning("Create a league first below.")

    st.divider()
    
    st.subheader("Create League")
    l_name = st.text_input("League Name")
    if st.button("Create League"):
        if l_name:
             try:
                r = requests.post(f"{API_URL}/leagues", json={"name": l_name})
                if r.status_code == 200:
                    st.success(f"League '{l_name}' created!")
                    st.rerun()
             except Exception as e:
                st.error(f"API Error: {e}")
                
    st.divider()
    st.subheader("Standings")
    
    if leagues:
        sel_l = st.selectbox("Select League", list(l_opts.keys()), key="standings_league")
        
        if sel_l:
            lid = l_opts[sel_l]
            if st.button("Calculate Standings"):
                with st.spinner("Calculating..."):
                    try:
                        r = requests.get(f"{API_URL}/leagues/{lid}/standings")
                        if r.status_code == 200:
                            standings = r.json()
                            if standings:
                                df = pd.DataFrame(standings)
                                # Show interesting cols
                                show_cols = ['rank', 'team_id', 'total_roto_points', 
                                             'points_pts', 'points_reb', 'points_ast', 'points_stl', 'points_blk', 
                                             'points_tpm', 'points_fg_pct', 'points_ft_pct']
                                st.dataframe(df[show_cols])
                                
                                st.write("Raw Totals")
                                raw_cols = [c for c in df.columns if c.startswith('total_') and c != 'total_roto_points']
                                st.dataframe(df[['team_id'] + raw_cols])
                            else:
                                st.info("No standings data generated. Are there teams with players in this league?")
                    except Exception as e:
                        st.error(f"API Error: {e}")
    else:
        st.info("No leagues found.")
