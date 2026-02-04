import matplotlib.pyplot as plt
from mplsoccer import Pitch

def plot_player(df, player_id):
    fig,ax = plt.subplots(figsize = (13.5, 8))
    fig.set_facecolor('#22312b')
    ax.patch.set_facecolor('#22312b')

    pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
    pitch.draw(ax=ax)


    for x in range(len(df)):
        if df['event_type'][x] == 'PASS' & df['player_id'][x] == player_id:
            if df['success'][x] == True:
                ax.plot(
                    [df['coordinates_x'][x], df['end_coordinates_x'][x]],
                    [df['coordinates_y'][x], df['end_coordinates_y'][x]],
                    color='green'
                )
                ax.scatter(
                    df['coordinates_x'][x],
                    df['coordinates_y'][x],
                    color='green'
                )

            elif df['success'][x] == False:
                ax.plot(
                    [df['coordinates_x'][x], df['end_coordinates_x'][x]],
                    [df['coordinates_y'][x], df['end_coordinates_y'][x]],
                    color='red'
                )
                ax.scatter(
                    df['coordinates_x'][x],
                    df['coordinates_y'][x],
                    color='red'
                )


    plt.title('Pass Map - Player ID {player_id}', color='white', fontsize=20)
            