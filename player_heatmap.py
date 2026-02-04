import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns

def heat_map(df, player_id, overlay_passes=False):
    passes = df[(df['event_type'] == 'PASS') & (df['player_id'] == player_id)].copy()
    if passes.empty:
        print(f"No passes found for player_id {player_id}")
        return

    fig, ax = plt.subplots(figsize=(13.5, 8))
    fig.set_facecolor('#22312b')
    ax.set_facecolor('#22312b')

    pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
    pitch.draw(ax=ax)

    # KDE heatmap on pitch
    sns.kdeplot(
        x=passes['coordinates_x'],
        y=passes['coordinates_y'],
        fill=True,
        thresh=0.05,
        alpha=0.5,
        levels=10,
        cmap='magma',
        ax=ax
    )

    if overlay_passes:
        comp = passes[passes['success'] == True]
        inc  = passes[passes['success'] == False]

        pitch.arrows(comp['coordinates_x'], comp['coordinates_y'],
                     comp['end_coordinates_x'], comp['end_coordinates_y'],
                     ax=ax, color='green', alpha=0.5, width=1)

        pitch.arrows(inc['coordinates_x'], inc['coordinates_y'],
                     inc['end_coordinates_x'], inc['end_coordinates_y'],
                     ax=ax, color='red', alpha=0.35, width=1)

    ax.set_title(f'Heat Map — Player ID {player_id}', color='white', fontsize=20)
    plt.show()
