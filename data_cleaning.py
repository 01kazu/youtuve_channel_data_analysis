import pandas as pd
from os import listdir
from os.path import isfile, join
from typing import Dict


def get_digits(string: str) -> str:
    char_list = [char for char in string if char.isdigit()]
    return ''.join(char_list)


def get_video_duration(video_duration_str: str) -> Dict[str, str]:
    video_duration = {'H': '0', 'M': '0', 'S': '0'}
    for time_str in ['H', 'M', 'S']:
        if time_str in video_duration_str:
            result = video_duration_str.split(time_str)
            if len(result) == 2:
                time, video_duration_str = result
                time = ''.join([t for t in time if t.isdigit()])
                video_duration[time_str] = time
            else:
                time = result[0]
                time = ''.join([t for t in time if t.isdigit()])
                video_duration[time_str] = time
    return video_duration


def data_cleaning_video(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=['date_released_utc', 'date_collected_utc'])
    # Extract video duration from string
    df['video_duration_H_M_S'] = df['video_duration'].apply(get_video_duration)
    df['video_duration_H'] = df['video_duration_H_M_S'].apply(lambda time: time['H'])
    df['video_duration_M'] = df['video_duration_H_M_S'].apply(lambda time: time['M'])
    df['video_duration_S'] = df['video_duration_H_M_S'].apply(lambda time: time['S'])
    # Change datatype from string to int
    df = df.astype(
            {'video_duration_H': int, 
             'video_duration_M': int, 
             'video_duration_S': int})
    df = df.drop(columns=['video_duration', 'video_duration_H_M_S'])
    return df


def get_num(string: str) -> float:
    # 1.02M subscribers, 1.3k videos
    first_substring = string.split()[0]
    if first_substring.isdigit():
        return float(first_substring)
    num, abbreviation = first_substring[:-1], first_substring[-1] 
    multiply_dict = {"M": 1000000, "K": 1000}
    abbreviation_int = multiply_dict.get(abbreviation.upper()) # To match the key of the multiply dictionary
    if abbreviation:
        num_int = float(num) * abbreviation_int # type: ignore
        return num_int
    return 0.0 # something went wrong


def data_cleaning_channel_details(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    # New columns
    df['subscriber_count'] = df['subscriber_count'].apply(get_num) 
    df['videos_count'] = df['videos_count'].apply(get_num)
    df = df.astype(
            {'subscriber_count': int, 
             'videos_count': int})
    return df

def main()-> None:
    for file in listdir('datasets'):
        if isfile(join('datasets', file)):
            if file == "youtuber_channel_details.csv":
                df = data_cleaning_channel_details(join('datasets', file))
                df.to_csv(join('cleaned_datasets', file), index=False)
                continue
            df = data_cleaning_video(join('datasets', file))
            df.to_csv(join('cleaned_datasets', file), index=False )

if __name__ == '__main__':
    main()