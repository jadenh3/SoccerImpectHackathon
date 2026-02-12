import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns

def player_shot_chart(df, player_id):
    shots = df[df['event_type'] == 'SHOT'].copy()
    shots = shots[shots['player_id'] == player_id]
    pitch = Pitch()
    fig, ax = pitch.draw(figsize=(6, 6))

    sns.scatterplot (
        data=shots,
        x='coordinates_x',
        y='coordinates_y',
        hue='result',
        ax=ax
    )

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, title='Outcome', loc='upper left')
    plt.title('Shot Outcome by Shot Location')
    plt.tight_layout()
    plt.show()