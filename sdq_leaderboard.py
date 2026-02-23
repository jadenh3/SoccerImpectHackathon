from shot_decision_quality import create_shot_analysis, generate_shot_leaderboard
def load_shots(match_id, competition_id=743):
    from kloppy import impect

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
    import polars as pl
    import requests
    import io
    from kloppy.utils import github_resolve_raw_data_url

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
    import pandas as pd

    match_ids = get_match_ids(competition_id=competition_id)
    dfs = []

    for i, mid in enumerate(match_ids, start=1):
        df_match = load_shots(mid, competition_id=competition_id)  

        if df_match is None or df_match.empty:
            continue

        df_match = df_match.copy()
        df_match["match_id"] = mid
        dfs.append(df_match)

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def get_leaderboard(competition_id=743, min_shots=3):
    shots_all = load_all_shots(competition_id=competition_id)

    shot_sdq_df = create_shot_analysis(shots_all)

    leaderboard_df = generate_shot_leaderboard(shot_sdq_df, min_shots=min_shots)

    return leaderboard_df