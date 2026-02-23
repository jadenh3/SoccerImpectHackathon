import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


class ShotDecisionQuality:
    
    def __init__(self):
        self.pitch_length = 120
        self.pitch_width = 80
        self.goal_width = 8
        
        self.zones = {
            'six_yard_box': 6,
            'penalty_box': 18,
            'danger_zone': 24,
            'edge_of_box': 30,
            'long_range': 45
        }
    
    def calculate_distance_to_goal(self, x, y):
        if x >= 60:
            goal_x = 120
            goal_y = self.pitch_width / 2
        else:
            goal_x = 0
            goal_y = self.pitch_width / 2

        distance = np.sqrt((x - goal_x)**2 + (y - goal_y)**2)
        return distance
    
    def calculate_shot_angle(self, x, y):
        if x >= 60: 
            goal_x = 120
        else:
            goal_x = 0

        post_width = self.goal_width / 2
        goal_y_center = 40
        
        post_1_y = goal_y_center - post_width
        post_2_y = goal_y_center + post_width
        
        angle_1 = np.arctan2(abs(y - post_1_y), abs(goal_x - x))
        angle_2 = np.arctan2(abs(y - post_2_y), abs(goal_x - x))
        total_angle = np.degrees(abs(angle_1 - angle_2))
        
        return total_angle
    
    def calculate_location_score(self, x, y):
        distance_score = self.calculate_distance_to_goal(x, y)
        angle = self.calculate_shot_angle(x, y)

        if x >= 60:
            x_from_goal = 120 - x
        else: 
            x_from_goal = x
        
        if x_from_goal <= self.zones['six_yard_box']:
            distance_score = 100

        elif x_from_goal <= self.zones['penalty_box']:
            distance_score = 90 - (x_from_goal - self.zones['six_yard_box']) * 1.5

        elif x_from_goal <= self.zones['danger_zone']:
            distance_score = 75 - (x_from_goal - self.zones['penalty_box']) * 2.5

        elif x_from_goal <= self.zones['edge_of_box']:
            distance_score = 60 - (x_from_goal - self.zones['danger_zone']) * 2

        elif x_from_goal <= self.zones['long_range']:
            distance_score = 40 - (x_from_goal - self.zones['edge_of_box']) * 1.5

        else:
            distance_score = max(10, 40 - (x_from_goal - self.zones['long_range']) * 1.5)
        
        if angle >= 25:
            angle_score = 100
        elif angle >= 15:
            angle_score = 80 + (angle - 15) * 2
        elif angle >= 8:
            angle_score = 60 + (angle - 8) * 2.86
        else:
            angle_score = 40 + angle * 2.5
        
        central_bonus = 1.0
        if abs(y - 40) < 8:
            central_bonus = 1.1
        
        location_score = (distance_score * 0.7 + angle_score * 0.3) * central_bonus
        
        return min(100, location_score)
    
    def calculate_timing_score(self, is_counter_attack=False, is_set_piece=False):
        base_score = 70
        
        if is_counter_attack:
            base_score += 20
        
        if is_set_piece:
            base_score += 10
        
        return min(100, base_score)
    
    def calculate_pressure_score(self, under_pressure):
        return 60 if under_pressure else 85
    
    def calculate_shot_type_score(self, body_part, x, angle):
        base_score = 70

        if x >= 60:
            x_from_goal = 120 - x
        else: 
            x_from_goal = x
        
        if x_from_goal <= self.zones['six_yard_box']:
            base_score = 85
            if body_part == 'HEAD':
                base_score = 90
    
        elif x_from_goal <= self.zones['penalty_box']:
            if body_part in ['RIGHT_FOOT', 'LEFT_FOOT']:
                base_score = 85
            elif body_part == 'HEAD':
                base_score = 80
    
        elif x_from_goal > self.zones['edge_of_box']:
            if body_part in ['RIGHT_FOOT', 'LEFT_FOOT']:
                base_score = 70
            else:
                base_score = 50
    
        if angle < 8 and x_from_goal > self.zones['penalty_box']:
            base_score -= 15
        
        return min(100, base_score)
    
    def calculate_expected_value(self, location_score, x, angle):
        if x >= 60:
            x_from_goal = 120 - x
        else:
            x_from_goal = x

        if x_from_goal <= self.zones['six_yard_box']:
            base_xg = 0.50
        elif x_from_goal <= self.zones['penalty_box']:
            base_xg = 0.25
        elif x_from_goal <= self.zones['danger_zone']:
            base_xg = 0.12
        elif x_from_goal <= self.zones['edge_of_box']:
            base_xg = 0.06
        else:
            base_xg = 0.03
        
        if angle >= 20:
            angle_mult = 1.3
        elif angle >= 10:
            angle_mult = 1.1
        elif angle >= 5:
            angle_mult = 0.9
        else:
            angle_mult = 0.7
        
        xg_adjusted = base_xg * angle_mult
        expected_value = min(100, (xg_adjusted * 150) + (location_score * 0.3))
        
        return expected_value
    
    def calculate_sdq(self, shot_event):
        x = shot_event.get('coordinates_x', 0)
        y = shot_event.get('coordinates_y', 0)
        body_part = shot_event.get('body_part_type', 'RIGHT_FOOT')
        under_pressure = shot_event.get('is_under_pressure', False)
        is_set_piece = shot_event.get('set_piece_type') is not None and pd.notna(shot_event.get('set_piece_type'))
        success = shot_event.get('success', False)
        result = shot_event.get('result', '')
 
        
        location_score = self.calculate_location_score(x, y)
        distance = self.calculate_distance_to_goal(x, y)
        angle = self.calculate_shot_angle(x, y)
        
        timing_score = self.calculate_timing_score(is_set_piece=is_set_piece)
        pressure_score = self.calculate_pressure_score(under_pressure)
        shot_type_score = self.calculate_shot_type_score(body_part, x, angle)
        expected_value = self.calculate_expected_value(location_score, x, angle)
        
        sdq = (
            location_score * 0.40 +
            pressure_score * 0.25 +
            shot_type_score * 0.20 +
            timing_score * 0.15
        )
        
        
        return {
            'sdq': sdq,
            'location_score': location_score,
            'timing_score': timing_score,
            'pressure_score': pressure_score,
            'shot_type_score': shot_type_score,
            'expected_value': expected_value,
            'distance_to_goal': distance,
            'shot_angle': angle,
            'shot_result': 'GOAL' if success else 'NO_GOAL'
        }
    
    def calculate_player_sdq(self, player_shots):
        sdq_scores = []
        component_scores = {
            'location': [],
            'timing': [],
            'pressure': [],
            'shot_type': [],
            'expected_value': []
        }
        
        shot_details = {
            'total_shots': len(player_shots),
            'goals': 0,
            'avg_distance': 0,
            'avg_angle': 0,
            'shots_under_pressure': 0,
            'shots_in_box': 0
        }
        
        distances = []
        angles = []
        
        for _, shot in player_shots.iterrows():
            scores = self.calculate_sdq(shot)
            sdq_scores.append(scores['sdq'])
            component_scores['location'].append(scores['location_score'])
            component_scores['timing'].append(scores['timing_score'])
            component_scores['pressure'].append(scores['pressure_score'])
            component_scores['shot_type'].append(scores['shot_type_score'])
            component_scores['expected_value'].append(scores['expected_value'])
            
            distances.append(scores['distance_to_goal'])
            angles.append(scores['shot_angle'])
            
            if scores['shot_result'] == 'GOAL':
                shot_details['goals'] += 1
            
            if shot.get('is_under_pressure', False):
                shot_details['shots_under_pressure'] += 1
            
            x = shot.get('coordinates_x', 0)
            if x >= 60:
                x_from_goal = 120 - x
            else:
                x_from_goal = x
            if x_from_goal <= self.zones['penalty_box']:
                shot_details['shots_in_box'] += 1
        
        shot_details['avg_distance'] = np.mean(distances) if len(distances) > 0 else 0
        shot_details['avg_angle'] = np.mean(angles) if len(angles) > 0 else 0
        shot_details['conversion_rate'] = (shot_details['goals'] / shot_details['total_shots'] * 100) if shot_details['total_shots'] > 0 else 0
        
        return {
            'overall_sdq': np.mean(sdq_scores),
            'sdq_median': np.median(sdq_scores),
            'sdq_std': np.std(sdq_scores),
            'consistency': 100 - np.std(sdq_scores),
            'avg_location_score': np.mean(component_scores['location']),
            'avg_timing_score': np.mean(component_scores['timing']),
            'avg_pressure_score': np.mean(component_scores['pressure']),
            'avg_shot_type_score': np.mean(component_scores['shot_type']),
            'avg_expected_value': np.mean(component_scores['expected_value']),
            **shot_details
        }


def create_shot_analysis(df):
    shot_events = df[df['event_type'] == 'SHOT'].copy()
    
    if len(shot_events) == 0:
        print("Warning: No shot events found in data")
        return df
    
    sdq_calculator = ShotDecisionQuality()
    
    sdq_results = []
    for idx, row in shot_events.iterrows():
        scores = sdq_calculator.calculate_sdq(row)
        sdq_results.append(scores)
    
    for key in sdq_results[0].keys():
        shot_events[key] = [result[key] for result in sdq_results]
    
    return shot_events


def generate_shot_leaderboard(df, min_shots=3):
    shot_events = df[df['event_type'] == 'SHOT'].copy()
    
    if len(shot_events) == 0:
        print("Warning: No shot events found")
        return pd.DataFrame()
    
    sdq_calculator = ShotDecisionQuality()
    
    player_stats = []
    
    for player_id in shot_events['player_id'].unique():
        player_shots = shot_events[shot_events['player_id'] == player_id]
        
        if len(player_shots) < min_shots:
            continue
        
        stats = sdq_calculator.calculate_player_sdq(player_shots)
        stats['player_id'] = player_id
        player_stats.append(stats)
    
    if len(player_stats) == 0:
        print(f"Warning: No players with at least {min_shots} shots")
        return pd.DataFrame()
    
    leaderboard = pd.DataFrame(player_stats)
    leaderboard = leaderboard.sort_values('overall_sdq', ascending=False)
    
    return leaderboard


