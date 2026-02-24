import requests
import polars as pl
import io
from kloppy.utils import github_resolve_raw_data_url

players_url = github_resolve_raw_data_url(
    repository="ImpectAPI/open-data",
    branch="main",
    file="data/players/players_743.json"
)

response = requests.get(players_url)
players_df = pl.read_json(io.StringIO(response.text)).to_pandas()

print("Player columns:", players_df.columns.tolist())
print("\nFirst player:")
print(players_df.iloc[0][['id', 'firstname', 'lastname', 'commonname']])