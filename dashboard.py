import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="SDQ Analysis - Bundesliga 2023/24",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_player_data():
    """
    Load player leaderboard data from SDQ calculations
    """
    from data_loader import get_leaderboard
    
    # Load the leaderboard
    df = get_leaderboard(competition_id=743, min_shots=1)
    
    return df

# ============================================================================
# LOAD DATA
# ============================================================================

with st.spinner("Loading Bundesliga data... This may take a minute on first load."):
    player_df = load_player_data()

# ============================================================================
# HEADER
# ============================================================================

st.markdown('<p class="main-header">⚽ Shot Decision Quality Analysis</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Bundesliga 2023/24 Season</p>', unsafe_allow_html=True)
st.markdown("---")

# ============================================================================
# SIDEBAR - GLOBAL FILTERS
# ============================================================================

st.sidebar.header("Filters")

# Minimum shots filter
min_shots_global = st.sidebar.slider(
    "Minimum Shots",
    min_value=1,
    max_value=50,
    value=5,
    help="Filter players by minimum number of shots taken"
)

# Position filter
all_positions = ['All'] + sorted(player_df['position'].unique().tolist())
position_filter = st.sidebar.multiselect(
    "Position",
    options=all_positions,
    default=['All'],
    help="Filter by player position"
)

# Team filter
all_teams = ['All'] + sorted(player_df['team'].unique().tolist())
team_filter = st.sidebar.multiselect(
    "Team",
    options=all_teams,
    default=['All'],
    help="Filter by team"
)

# Apply filters
filtered_df = player_df[player_df['total_shots'] >= min_shots_global].copy()

if 'All' not in position_filter and len(position_filter) > 0:
    filtered_df = filtered_df[filtered_df['position'].isin(position_filter)]

if 'All' not in team_filter and len(team_filter) > 0:
    filtered_df = filtered_df[filtered_df['team'].isin(team_filter)]

# Reset index to avoid indexing issues
filtered_df = filtered_df.reset_index(drop=True)

st.sidebar.markdown("---")
st.sidebar.info(f"**{len(filtered_df)}** players match current filters")

# ============================================================================
# CREATE TABS
# ============================================================================

tab1, tab2, tab3 = st.tabs(["Leaderboard", "Player Comparison", "SDQ vs Conversion % Analysis"])

# ============================================================================
# TAB 1: LEADERBOARD
# ============================================================================

with tab1:
    st.header("Player Leaderboard")
    
    # Sort options
    col_sort, col_display = st.columns([1, 3])
    
    with col_sort:
        sort_by = st.selectbox(
            "Sort By",
            options=['overall_sdq', 'goals', 'conversion_rate', 'total_shots', 'consistency'],
            format_func=lambda x: {
                'overall_sdq': 'SDQ Score',
                'goals': 'Goals',
                'conversion_rate': 'Conversion Rate (%)',
                'total_shots': 'Total Shots',
                'consistency': 'Consistency'
            }[x]
        )
    
    # Sort dataframe
    display_df = filtered_df.sort_values(sort_by, ascending=False).reset_index(drop=True)
    
    # Top metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Players", len(display_df))
    
    with col2:
        st.metric("Avg SDQ", f"{display_df['overall_sdq'].mean():.1f}")
    
    with col3:
        st.metric("Total Shots", int(display_df['total_shots'].sum()))
    
    with col4:
        st.metric("Total Goals", int(display_df['goals'].sum()))
    
    with col5:
        avg_conversion = (display_df['goals'].sum() / display_df['total_shots'].sum() * 100) if display_df['total_shots'].sum() > 0 else 0
        st.metric("Avg Conversion %", f"{avg_conversion:.1f}%")
    
    st.markdown("---")
    
    # Main leaderboard table
    st.subheader(f"Top {min(20, len(display_df))} Players")
    
    # Prepare table
    table_df = display_df.head(20).copy()
    table_df.insert(0, 'Rank', range(1, len(table_df) + 1))
    
    # Round numeric columns
    numeric_cols = ['overall_sdq', 'conversion_rate', 'consistency']
    for col in numeric_cols:
        if col in table_df.columns:
            table_df[col] = table_df[col].round(1)
    
    # Display table
    st.dataframe(
        table_df[['Rank', 'player_name', 'team', 'position', 'overall_sdq', 
                'total_shots', 'goals', 'conversion_rate']].rename(columns={
            'player_name': 'Player',
            'team': 'Team',
            'position': 'Position',
            'overall_sdq': 'SDQ',
            'total_shots': 'Shots',
            'goals': 'Goals',
            'conversion_rate': 'Conv %'
        }),
        hide_index=True,
        use_container_width=True,
        height=500
    )
    
    # Expandable detailed components
    with st.expander("📊 View Detailed SDQ Components"):
        component_df = table_df[['Rank', 'player_name', 'avg_location_score', 
                                 'avg_pressure_score', 'avg_shot_type_score', 
                                 'avg_timing_score', 'consistency']].copy()
        
        # Round components
        comp_cols = ['avg_location_score', 'avg_pressure_score', 'avg_shot_type_score', 'avg_timing_score', 'consistency']
        for col in comp_cols:
            component_df[col] = component_df[col].round(1)
        
        st.dataframe(
            component_df.rename(columns={
                'player_name': 'Player',
                'avg_location_score': 'Location (40%)',
                'avg_pressure_score': 'Pressure (25%)',
                'avg_shot_type_score': 'Shot Type (20%)',
                'avg_timing_score': 'Timing (15%)',
                'consistency': 'Consistency'
            }),
            hide_index=True,
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Top 5 players component breakdown
    st.subheader("📈 Top 5 Players - SDQ Component Breakdown")
    
    top_5 = display_df.head(5)
    
    # Create grouped bar chart
    fig_components = go.Figure()
    
    components = [
        ('avg_location_score', 'Location (40%)', '#FF6B6B'),
        ('avg_pressure_score', 'Pressure (25%)', '#4ECDC4'),
        ('avg_shot_type_score', 'Shot Type (20%)', '#45B7D1'),
        ('avg_timing_score', 'Timing (15%)', '#FFA07A')
    ]
    
    for comp, name, color in components:
        fig_components.add_trace(go.Bar(
            name=name,
            x=top_5['player_name'],
            y=top_5[comp],
            marker_color=color,
            text=top_5[comp].round(1),
            textposition='auto',
        ))
    
    fig_components.update_layout(
        barmode='group',
        title='Component Scores Comparison',
        xaxis_title='Player',
        yaxis_title='Score (0-100)',
        yaxis=dict(range=[0, 100]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=450,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_components, use_container_width=True)
    
    # Distribution visualization
    col1, col2 = st.columns(2)
    
    with col1:
        # SDQ distribution
        fig_sdq_dist = px.histogram(
            display_df,
            x='overall_sdq',
            nbins=30,
            title='SDQ Score Distribution',
            labels={'overall_sdq': 'SDQ Score', 'count': 'Number of Players'},
            color_discrete_sequence=['#1f77b4']
        )
        fig_sdq_dist.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_sdq_dist, use_container_width=True)
    
    with col2:
        # Goals distribution
        fig_goals_dist = px.histogram(
            display_df,
            x='goals',
            nbins=25,
            title='Goals Scored Distribution',
            labels={'goals': 'Goals', 'count': 'Number of Players'},
            color_discrete_sequence=['#2ca02c']
        )
        fig_goals_dist.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_goals_dist, use_container_width=True)

# ============================================================================
# TAB 2: PLAYER COMPARISON
# ============================================================================

with tab2:
    st.header("Compare Players Side-by-Side")
    
    st.markdown("""
    Select 2-3 players to compare their Shot Decision Quality profiles.
    View component breakdowns, shooting patterns, and key differentiators.
    """)
    
    # Player selection
    col1, col2, col3 = st.columns(3)
    
    player_options = sorted(filtered_df['player_name'].unique().tolist())
    
    with col1:
        player1 = st.selectbox(
            "Player 1",
            options=player_options,
            index=0 if len(player_options) > 0 else None,
            key='player1_select'
        )
    
    with col2:
        player2 = st.selectbox(
            "Player 2",
            options=player_options,
            index=min(1, len(player_options)-1) if len(player_options) > 1 else None,
            key='player2_select'
        )
    
    with col3:
        player3_options = ['None'] + player_options
        player3 = st.selectbox(
            "Player 3 (Optional)",
            options=player3_options,
            index=0,
            key='player3_select'
        )
    
    # Get selected player data
    selected_players = [player1, player2]
    if player3 != 'None':
        selected_players.append(player3)
    
    comparison_df = filtered_df[filtered_df['player_name'].isin(selected_players)].copy()
    
    if len(comparison_df) > 0:
        st.markdown("---")
        
        # Summary stats comparison
        st.subheader("Key Statistics Comparison")
        
        # Create metrics grid
        metrics_to_show = ['overall_sdq', 'total_shots', 'goals', 'conversion_rate', 'consistency']
        metric_names = ['SDQ Score', 'Total Shots', 'Goals', 'Conversion %', 'Consistency']
        
        for metric, name in zip(metrics_to_show, metric_names):
            cols = st.columns(len(selected_players))
            for i, (player_name, col) in enumerate(zip(selected_players, cols)):
                player_data = comparison_df[comparison_df['player_name'] == player_name].iloc[0]
                value = player_data[metric]
                
                if metric in ['conversion_rate', 'overall_sdq', 'consistency']:
                    formatted_value = f"{value:.1f}"
                else:
                    formatted_value = f"{int(value)}"
                
                with col:
                    if i == 0:
                        st.metric(f"{name}", formatted_value, label_visibility="visible")
                    else:
                        # Calculate delta compared to player 1
                        delta = value - comparison_df[comparison_df['player_name'] == selected_players[0]].iloc[0][metric]
                        if metric in ['conversion_rate', 'overall_sdq', 'consistency']:
                            delta_str = f"{delta:+.1f}"
                        else:
                            delta_str = f"{int(delta):+d}"
                        st.metric(f"{name}", formatted_value, delta_str)
        
        st.markdown("---")
        
        # Component comparison - Radar chart
        st.subheader("SDQ Component Profile")
        
        fig_radar = go.Figure()
        
        categories = ['Location', 'Pressure', 'Shot Type', 'Timing', 'Consistency']
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
        
        for idx, player_name in enumerate(selected_players):
            player_data = comparison_df[comparison_df['player_name'] == player_name].iloc[0]
            
            values = [
                player_data['avg_location_score'],
                player_data['avg_pressure_score'],
                player_data['avg_shot_type_score'],
                player_data['avg_timing_score'],
                player_data['consistency']
            ]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=player_name,
                line_color=colors[idx % len(colors)]
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            height=500,
            title="Component Scores Comparison (0-100 scale)"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        st.markdown("---")
        
        # Detailed comparison table
        st.subheader("Detailed Statistics")
        
        detail_cols = ['player_name', 'team', 'position', 'overall_sdq','total_shots', 
                       'goals', 'conversion_rate', 'avg_distance', 'avg_angle',
                       'avg_location_score', 'avg_pressure_score', 'avg_shot_type_score', 
                       'avg_timing_score', 'consistency']
        
        detail_df = comparison_df[detail_cols].copy()
        
        # Round numeric columns
        numeric_cols = [col for col in detail_df.columns if col not in ['player_name', 'team', 'position']]
        for col in numeric_cols:
            detail_df[col] = detail_df[col].round(1)
        
        # Transpose for better comparison view
        detail_df_transposed = detail_df.set_index('player_name').T
        detail_df_transposed.index.name = 'Metric'
        
        st.dataframe(
            detail_df_transposed,
            use_container_width=True,
            height=600
        )
        
    else:
        st.warning("No players selected for comparison. Please select at least 2 players.")

# ============================================================================
# TAB 3: SDQ VS CONVERSION RATE ANALYSIS
# ============================================================================

with tab3:
    st.header("Shot Decision Quality vs Conversion Rate Analysis")
    
    st.markdown("""
    This visualization reveals the relationship between **Shot Decision Quality (SDQ)** and **Conversion Rate**.
    
    ### Four Quadrants Explained:
    
    - Top-Right (Elite Shots): High Conversion Rate + High SDQ = Players who find great positions AND execute well
    - Top-Left (Making the Most): Low Conversion Rate + High SDQ = Creative finishers who maximize tough chances
    - Bottom-Right (Wasted Opportunities): High Conversion Rate + Low SDQ = Players who get into good positions but waste them
    - Bottom-Left (Forced Shots): Low Conversion Rate + Low SDQ = Desperate attempts from poor positions
    """)
    
    st.markdown("---")
    
    # Controls for the scatter plot
    col1, col2, col3 = st.columns(3)
    
    with col1:
        color_by = st.selectbox(
            "Color Points By",
            options=['position', 'goals', 'team'],
            format_func=lambda x: {
                'position': 'Player Position',
                'goals': 'Goals Scored',
                'team': 'Team'
            }[x]
        )
    
    with col2:
        show_labels = st.checkbox("Show Player Names", value=False)
    
    # Calculate quadrant thresholds (median values)
    sdq_threshold = filtered_df['overall_sdq'].median()
    conv_threshold = filtered_df['conversion_rate'].median()
    
    # Create scatter plot
    fig_scatter = go.Figure()
    
    # Color settings
    if color_by in ['position', 'team']:
        # Categorical coloring
        unique_categories = filtered_df[color_by].unique()
        color_map = dict(zip(unique_categories, px.colors.qualitative.Set2[:len(unique_categories)]))
        
        for category in unique_categories:
            category_data = filtered_df[filtered_df[color_by] == category]
            
            fig_scatter.add_trace(go.Scatter(
                x=category_data['conversion_rate'],
                y=category_data['overall_sdq'],
                mode='markers+text' if show_labels else 'markers',
                name=str(category),
                text=category_data['player_name'] if show_labels else None,
                textposition="top center",
                marker=dict(
                    size=14,
                    color=color_map[category],
                    line=dict(width=1, color='white'),
                    opacity=0.7
                ),
                hovertemplate='<b>%{customdata[0]}</b><br>' +
                             'Team: %{customdata[1]}<br>' +
                             'Position: %{customdata[2]}<br>' +
                             'SDQ: %{y:.1f}<br>' +
                             'Conversion %: %{x:.1f}<br>' +
                             'Goals: %{customdata[3]}<br>' +
                             'Shots: %{customdata[4]}<br>' +
                             '<extra></extra>',
                customdata=category_data[['player_name', 'team', 'position', 'goals', 'total_shots']].values
            ))
    else:
        # Continuous coloring (goals)
        fig_scatter.add_trace(go.Scatter(
            x=filtered_df['conversion_rate'],
            y=filtered_df['overall_sdq'],
            mode='markers+text' if show_labels else 'markers',
            text=filtered_df['player_name'] if show_labels else None,
            textposition="top center",
            marker=dict(
                size=14,
                color=filtered_df['goals'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Goals"),
                line=dict(width=1, color='white'),
                opacity=0.7
            ),
            hovertemplate='<b>%{customdata[0]}</b><br>' +
                         'Team: %{customdata[1]}<br>' +
                         'Position: %{customdata[2]}<br>' +
                         'SDQ: %{y:.1f}<br>' +
                         'Conversion %: %{x:.1f}<br>' +
                         'Goals: %{customdata[3]}<br>' +
                         'Shots: %{customdata[4]}<br>' +
                         '<extra></extra>',
            customdata=filtered_df[['player_name', 'team', 'position', 'goals', 'total_shots']].values,
            showlegend=False
        ))
    
    # Add quadrant lines
    fig_scatter.add_hline(
        y=sdq_threshold,
        line_dash="dash",
        line_color="gray",
        opacity=0.5,
        annotation_text=f"Median SDQ: {sdq_threshold:.1f}",
        annotation_position="right"
    )
    
    fig_scatter.add_vline(
        x=conv_threshold,
        line_dash="dash",
        line_color="gray",
        opacity=0.5,
        annotation_text=f"Median Conversion %: {conv_threshold:.1f}",
        annotation_position="top"
    )
    
    # Add quadrant labels
    max_x = filtered_df['conversion_rate'].max()
    max_y = filtered_df['overall_sdq'].max()
    min_x = filtered_df['conversion_rate'].min()
    min_y = filtered_df['overall_sdq'].min()
    
    quadrant_annotations = [
        dict(x=max_x * 0.85, y=max_y * 0.95, text="Elite Shots<br>", showarrow=False, font=dict(size=12, color="green")),
        dict(x=min_x * 1.15, y=max_y * 0.95, text="Making the Most<br>", showarrow=False, font=dict(size=12, color="blue")),
        dict(x=max_x * 0.85, y=min_y * 1.05, text="Wasted Opportunities<br>", showarrow=False, font=dict(size=12, color="orange")),
        dict(x=min_x * 1.15, y=min_y * 1.05, text="Forced Shots<br>", showarrow=False, font=dict(size=12, color="red"))
    ]
    
    fig_scatter.update_layout(
        title='Shot Decision Quality vs Conversion Rate - Bundesliga 2023/24',
        xaxis_title='Conversion Rate (%)',
        yaxis_title='Shot Decision Quality (SDQ, 0-100)',
        height=700,
        hovermode='closest',
        annotations=quadrant_annotations
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("---")
    
    # Insights section
    st.subheader("🔍 Key Insights")
    
    # Calculate quadrant populations
    q1 = len(filtered_df[(filtered_df['conversion_rate'] >= conv_threshold) & (filtered_df['overall_sdq'] >= sdq_threshold)])
    q2 = len(filtered_df[(filtered_df['conversion_rate'] < conv_threshold) & (filtered_df['overall_sdq'] >= sdq_threshold)])
    q3 = len(filtered_df[(filtered_df['conversion_rate'] < conv_threshold) & (filtered_df['overall_sdq'] < sdq_threshold)])
    q4 = len(filtered_df[(filtered_df['conversion_rate'] >= conv_threshold) & (filtered_df['overall_sdq'] < sdq_threshold)])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Elite Shots", q1, help="High Conversion % + High SDQ")
    
    with col2:
        st.metric("Making the Most", q2, help="Low Conversion % + High SDQ")
    
    with col3:
        st.metric("Wasted Opportunities", q4, help="High Conversion % + Low SDQ")
    
    with col4:
        st.metric("Forced Shots", q3, help="Low Conversion % + Low SDQ")
    
    # Top performers in each quadrant
    st.markdown("### Top 3 Players in Each Quadrant")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Elite Shots (Q1)
        q1_players = filtered_df[(filtered_df['conversion_rate'] >= conv_threshold) & 
                                 (filtered_df['overall_sdq'] >= sdq_threshold)].nlargest(3, 'overall_sdq')
        st.markdown("**Elite Shots (High Conversion % + High SDQ)**")
        if len(q1_players) > 0:
            for idx, player in q1_players.iterrows():
                st.write(f"{player['player_name']} - SDQ: {player['overall_sdq']:.1f}, Conversion %: {player['conversion_rate']:.1f}")
        else:
            st.write("No players in this quadrant")
        
        # Forced Shots (Q3)
        q3_players = filtered_df[(filtered_df['conversion_rate'] < conv_threshold) & 
                                 (filtered_df['overall_sdq'] < sdq_threshold)].nsmallest(3, 'overall_sdq')
        st.markdown("**Forced Shots (Low Conversion % + Low SDQ)**")
        if len(q3_players) > 0:
            for idx, player in q3_players.iterrows():
                st.write(f"{player['player_name']} - SDQ: {player['overall_sdq']:.1f}, Conversion %: {player['conversion_rate']:.1f}")
        else:
            st.write("No players in this quadrant")
    
    with col2:
        # Making the Most (Q2)
        q2_players = filtered_df[(filtered_df['conversion_rate'] < conv_threshold) & 
                                 (filtered_df['overall_sdq'] >= sdq_threshold)].nlargest(3, 'overall_sdq')
        st.markdown("**Making the Most (Low Conversion % + High SDQ)**")
        if len(q2_players) > 0:
            for idx, player in q2_players.iterrows():
                st.write(f"{player['player_name']} - SDQ: {player['overall_sdq']:.1f}, Conversion %: {player['conversion_rate']:.1f}")
        else:
            st.write("No players in this quadrant")
        
        # Wasted Opportunities (Q4)
        q4_players = filtered_df[(filtered_df['conversion_rate'] >= conv_threshold) & 
                                 (filtered_df['overall_sdq'] < sdq_threshold)].nsmallest(3, 'overall_sdq')
        st.markdown("**Wasted Opportunities (High Conversion % + Low SDQ)**")
        if len(q4_players) > 0:
            for idx, player in q4_players.iterrows():
                st.write(f"{player['player_name']} - SDQ: {player['overall_sdq']:.1f}, Conversion %: {player['conversion_rate']:.1f}")
        else:
            st.write("No players in this quadrant")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("Data: IMPECT Open Data (Bundesliga 2023/24) | Metric: Shot Decision Quality (SDQ)")