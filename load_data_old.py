def load_shots(match_id):
    import polars as pl
    import requests
    import io
    from kloppy import impect
    from kloppy.utils import github_resolve_raw_data_url

    # Load matches and squads data from IMPECT Open Data repository
    match_url = github_resolve_raw_data_url(
        repository="ImpectAPI/open-data",
        branch="main",
        file="data/matches/matches_743.json"
    )
    squads_url = github_resolve_raw_data_url(
        repository="ImpectAPI/open-data",
        branch="main",
        file="data/squads/squads_743.json"
    )

    # Load and process matches data
    response = requests.get(match_url)
    matches = (
        pl.read_json(io.StringIO(response.text))
        .unnest("matchDay")
        .rename({'iterationId': 'competitionId', 'id': 'matchId'})
        .drop(['idMappings', 'lastCalculationDate', 'name', 'available'])
        .with_columns([
            (pl.col("index") + 1).alias("matchDay")
        ])
        .drop("index")
    )

    response = requests.get(squads_url)
    squads = (
        pl.read_json(io.StringIO(response.text))
        .drop(['type', 'gender', 'imageUrl', 'idMappings', 'access', 'countryId'])
    )

    matches = (
        matches
        .join(
            squads.rename({"name": "homeTeam"}),
            left_on="homeSquadId",
            right_on="id",
            how="left"
        )
        .join(
            squads.rename({"name": "awayTeam"}),
            left_on="awaySquadId",
            right_on="id",
            how="left"
        )
    )


    match_id = match_id 
    dataset = impect.load_open_data(
        match_id=match_id,
        competition_id=743,
    )

    df = (
    dataset
    .transform(to_coordinate_system="statsbomb")  
    .filter(lambda event: event.event_type.name in ["SHOT"])
    .to_df(engine="pandas")
    )

    return df
