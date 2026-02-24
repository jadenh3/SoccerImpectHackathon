"""
Data loader for SDQ Dashboard
Uses only real IMPECT data - no fake data added
"""

from shot_decision_quality import create_shot_analysis, generate_shot_leaderboard
from kloppy import impect
import pandas as pd
import polars as pl
import requests
import io
from kloppy.utils import github_resolve_raw_data_url


def load_metadata(competition_id=743):
    """
    Load player and team metadata from IMPECT
    
    Returns:
        players_df: DataFrame with player_id and player_name
        squads_df: DataFrame with squad_id and team_name
    """
    # Load players
    players_url = github_resolve_raw_data_url(
        repository="ImpectAPI/open-data",
        branch="main",
        file=f"data/players/players_{competition_id}.json"
    )
    
    response = requests.get(players_url)
    players = pl.read_json(io.StringIO(response.text)).to_pandas()
    
    # Load squads (teams)
    squads_url = github_resolve_raw_data_url(
        repository="ImpectAPI/open-data",
        branch="main",
        file=f"data/squads/squads_{competition_id}.json"
    )
    
    response = requests.get(squads_url)
    squads = pl.read_json(io.StringIO(response.text)).to_pandas()
    
    return players, squads


def load_shots(match_id, competition_id=743):
    """
    Load shots from a single match
    """
    dataset = impect.load_open_data(
        match_id=match_id,
        competition_id=competition_id,
    )

    df = (
        dataset
        .transform(to_coordinate_system="statsbomb")  
        .filter(lambda event: event.event_type.name in ["SHOT"])
        .to_df(engine="pandas")
    )

    return df


def get_match_ids(competition_id=743):
    """
    Get list of all match IDs for a competition
    """
    match_url = github_resolve_raw_data_url(
        repository="ImpectAPI/open-data",
        branch="main",
        file=f"data/matches/matches_{competition_id}.json"
    )

    response = requests.get(match_url)
    response.raise_for_status()

    matches = (
        pl.read_json(io.StringIO(response.text))
        .unnest("matchDay")
        .rename({"id": "matchId"})
    )

    return matches["matchId"].to_list()


def load_all_shots(competition_id=743):
    """
    Load shots from ALL matches in the competition
    """
    match_ids = get_match_ids(competition_id=competition_id)
    dfs = []

    print(f"Loading shots from {len(match_ids)} matches...")
    
    for i, mid in enumerate(match_ids, start=1):
        if i % 50 == 0:
            print(f"  Loaded {i}/{len(match_ids)} matches...")
        
        try:
            df_match = load_shots(mid, competition_id=competition_id)  

            if df_match is None or df_match.empty:
                continue

            df_match = df_match.copy()
            df_match["match_id"] = mid
            dfs.append(df_match)
            
        except Exception as e:
            print(f"  Error loading match {mid}: {e}")
            continue

    print(f"Successfully loaded {len(dfs)} matches")
    
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def get_leaderboard(competition_id=743, min_shots=1):
    """
    Generate player leaderboard with SDQ statistics
    Uses only real IMPECT data - no fake columns added
    """
    print("Starting data load for leaderboard...")
    
    # Load metadata (player names and team names)
    print("Loading player and team metadata...")
    players, squads = load_metadata(competition_id=competition_id)
    
    # Load all shots from all matches
    shots_all = load_all_shots(competition_id=competition_id)
    
    if shots_all.empty:
        print("ERROR: No shots loaded!")
        return pd.DataFrame()
    
    print(f"Total shots loaded: {len(shots_all)}")
    
    # Calculate SDQ for each shot
    print("Calculating SDQ scores...")
    shot_sdq_df = create_shot_analysis(shots_all)
    
    # Generate player-level leaderboard
    print("Generating player leaderboard...")
    leaderboard_df = generate_shot_leaderboard(shot_sdq_df, min_shots=min_shots)
    
    print(f"Leaderboard created with {len(leaderboard_df)} players")
    
    # Add player names from metadata
    print("Adding player names...")
    if 'id' in players.columns and 'commonname' in players.columns:
        players_lookup = players[['id', 'commonname']].rename(columns={'id': 'player_id', 'commonname': 'player_name'})
        # Convert player_id to same type (int) in both dataframes
        players_lookup['player_id'] = players_lookup['player_id'].astype(int)
        leaderboard_df['player_id'] = leaderboard_df['player_id'].astype(int)
        leaderboard_df = leaderboard_df.merge(players_lookup, on='player_id', how='left')
    
    # Fill any missing player names with "Player {id}"
    if 'player_name' in leaderboard_df.columns:
        leaderboard_df['player_name'] = leaderboard_df['player_name'].fillna('Player ' + leaderboard_df['player_id'].astype(str))
    
    # Add team names from squads
    # First, get team_id for each player from shots data
    print("Adding team info...")
    player_teams = shot_sdq_df[['player_id', 'team_id']].drop_duplicates()
    player_teams['player_id'] = player_teams['player_id'].astype(int)
    leaderboard_df = leaderboard_df.merge(player_teams, on='player_id', how='left')
    
    # Now add team names - convert team_id to int to match
    if 'id' in squads.columns and 'name' in squads.columns:
        squads_lookup = squads[['id', 'name']].rename(columns={'id': 'team_id', 'name': 'team'})
        squads_lookup['team_id'] = squads_lookup['team_id'].astype(int)
        leaderboard_df['team_id'] = leaderboard_df['team_id'].astype(int)
        leaderboard_df = leaderboard_df.merge(squads_lookup, on='team_id', how='left')
    
    # Add position estimate based on shooting distance
    # (IMPECT doesn't provide position, so we estimate: forwards shoot closer)
    leaderboard_df['position'] = leaderboard_df['avg_distance'].apply(
        lambda x: 'Forward' if x < 18 else 'Midfielder'
    )
    
    print(f"✓ Leaderboard ready with {len(leaderboard_df)} players")
    
    return leaderboard_df


# For testing
if __name__ == "__main__":
    print("Testing data loader...")
    
    # Test metadata loading
    print("\n1. Testing metadata load...")
    players, squads = load_metadata()
    print(f"   ✓ Loaded {len(players)} players")
    print(f"   ✓ Loaded {len(squads)} teams")
    print(f"   Sample player: {players.iloc[0]['name'] if 'name' in players.columns else 'no name column'}")
    print(f"   Sample team: {squads.iloc[0]['name'] if 'name' in squads.columns else 'no name column'}")
    
    # Test single match
    print("\n2. Testing single match load...")
    test_match = get_match_ids()[0]
    shots = load_shots(test_match)
    print(f"   ✓ Loaded {len(shots)} shots from match {test_match}")
    
    print("\n✓ Basic tests complete!")