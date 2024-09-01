import json
from pathlib import Path
import pandas as pd


def get_pkl_standings(season=None, team_id=None, matches=False):
    if season is None:
        season = 10

    file_path = Path(f"../1_DATA/Team-Wise-Data/standings_json/json_s{season}.json")

    with open(file_path, 'r') as f:
        data = json.load(f)

    standings = data['standings']

    team_info_list = []
    matches_list = []

    for group in standings['groups']:
        group_name = group['name'] if 'name' in group else 'Main'
        for team in group['teams']['team']:
            if team_id is None or int(team['team_id']) == team_id:
                team_info = create_team_info(team, season, group_name)
                team_info_list.append(team_info)

                if matches:
                    matches_list.extend(create_matches_list(team, group_name))

    team_info_df = pd.DataFrame(team_info_list)

    if matches:
        matches_df = process_matches(matches_list)
        return team_info_df, matches_df
    else:
        return team_info_df


def create_team_info(team, season, group_name):
    return {
        'Group': group_name,
        'Season': season,
        'Team_Name': team['team_name'],
        'Team_Id': team['team_id'],
        'team_short_name': team['team_short_name'],
        'League_position': team['position'],
        'Matches_played': team['played'],
        'Wins': team['wins'],
        'Lost': team['lost'],
        'Tied': team['tied'],
        'Draws': team['draws'],
        'No Result': team['noresult'],
        'League_points': team['points'],
        'Score_diff': team['score_diff'],
        'Qualified': team['is_qualified'],
    }


def create_matches_list(team, group_name):
    matches = []
    for match in team['match_result']['match']:
        match_info = {
            'Group': group_name,
            'match_id': match['id'],
            'date': match['date'],
            'teama_id': match['teama_id'],
            'result': match['result'],
            'teama_short_name': match['teama_short_name'],
            'teama_score': match['teama_score'],
            'teamb_id': match['teamb_id'],
            'teamb_short_name': match['teamb_short_name'],
            'teamb_score': match['teamb_score'],
            'match_result': match['match_result']
        }
        matches.append(match_info)
    return matches


def process_matches(matches_list):
    matches_df = pd.DataFrame(matches_list)
    matches_df = matches_df[(matches_df['result'].isin(['W', 'T'])) | (matches_df['result'].isnull())]
    matches_df = matches_df.sort_values(by='date', ascending=True)
    matches_df = matches_df.set_index('match_id').rename_axis('match id')
    return matches_df


def get_team_info(team_id, season='overall'):
    file_path_5_plus = Path("../1_DATA/Team-Wise-Data/seasons_5_plus_and_all_rounded.csv")
    file_path_1_to_4 = Path("../1_DATA/Team-Wise-Data/seasons_1_to_4_final.csv")

    if season != 'overall':
        season = int(season)

    if season == 'overall' or 5 <= season <= 10:
        df = pd.read_csv(file_path_5_plus)
    elif 1 <= season <= 4:
        df = pd.read_csv(file_path_1_to_4)
    else:
        print(f"Invalid season: {season}")
        return None, None, None

    df['team_id'] = pd.to_numeric(df['team_id'], errors='coerce')

    team_id = int(team_id)

    if season == 'overall':
        all_row = df[(df['team_id'] == team_id) & (df['season'] == 'all')]
        other_rows = df[(df['team_id'] == team_id) & (df['season'] != 'all')]
        filtered_df = pd.concat([all_row, other_rows]).reset_index(drop=True)
    else:
        filtered_df = df[(df['team_id'] == team_id) & (df['season'] == season)]

    if filtered_df.empty:
        print(f"No data found in CSV for team_id {team_id} in season {season}")
        return None, None, None
    if season == 'overall':
        standings_df, matches_df = get_pkl_standings(season=10, team_id=team_id, matches=True)
    else:
        standings_df, matches_df = get_pkl_standings(season, team_id, matches=True)

    return filtered_df, standings_df, matches_df


if __name__ == '__main__':
    # standings, matches = get_pkl_standings(season=4, matches=True)
    # print(standings)

    df1, df2, df3 = get_team_info('4')
    print(df1)
    print(df2)
    print(df3)