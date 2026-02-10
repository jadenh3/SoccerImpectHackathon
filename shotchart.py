import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns

def shot_chart(df, player_id):
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
        #palette={True: 'green', False: 'red'}
    )

    handles, labels = ax.get_legend_handles_labels()
    labels = ['No Goal', 'Goal']
    ax.legend(handles, labels, title='Outcome', loc='upper left')
    plt.title('Shot Outcome by Shot Location')
    plt.tight_layout()
    plt.show()