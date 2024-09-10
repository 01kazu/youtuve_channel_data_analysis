from unittest import result
import pandas as pd
from os import listdir
from os.path import isfile, join
from typing import Dict, List


def get_digits(string: str) -> str:
    char_list = [char for char in string if char.isdigit()]
    digits = ''.join(char_list)
    return digits


def get_video_duration(video_duration_str: str) -> Dict[str, str]:
    """
    Returns the appropriate hour, minutes, seconds from a string

    Parameters
    ----------
    video_duration_str : str
        Youtube api video duration string

    Returns
    -------
    video_duration : dict
    """
    video_duration = {'H': '0', 'M': '0', 'S': '0'}
    for time_str in ['H', 'M', 'S']:
        if time_str in video_duration_str:
            result = video_duration_str.split(time_str)
            time, video_duration_str = result
            video_duration[time_str]  = get_digits(time)
    return video_duration


def data_cleaning_video(filepath: str) -> pd.DataFrame:
    """

    """
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
    """
    """
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
    df['channel_name'] = df['channel_name'].str.strip('@')
    df['subscriber_count'] = df['subscriber_count'].apply(get_num) 
    df['videos_count'] = df['videos_count'].apply(get_num)
    df = df.astype(
            {'subscriber_count': int, 
             'videos_count': int})
    return df


def data_compilation(filepath: str, 
                     columns: List[str] = [''], 
                     files_to_exclude: List[str] = ['']) -> pd.DataFrame:
    result_df = pd.DataFrame(columns=columns)
    for file in listdir(filepath):
        file_dir = join(filepath, file) 
        if isfile(file_dir):
            if file not in files_to_exclude:
                df = pd.read_csv(file_dir, parse_dates=['date_released_utc',
                                                        'date_collected_utc'])
                channel_name = file.strip('.csv')
                df['channel_name'] = channel_name
                result_df = pd.concat([result_df, df])
    return result_df
    
    
                
def main()-> None:
    ## Cleaning all datasets
    # for file in listdir('datasets'):
    #     if isfile(join('datasets', file)):
    #         if file == "youtuber_channel_details.csv":
    #             df = data_cleaning_channel_details(join('datasets', file))
    #             df.to_csv(join('cleaned_datasets', file), index=False)
    #             continue
    #         df = data_cleaning_video(join('datasets', file))
    #         df.to_csv(join('cleaned_datasets', file), index=False )
    # print(get_video_duration('PT1H30M17S'))
    ## Cleaning Youtuber_channel_details.csv
    df = data_cleaning_channel_details('datasets/youtuber_channel_details.csv')
    df.to_csv(join('cleaned_datasets', 'youtuber_channel_details.csv' ), index=False )
    ## Compiling all the dataframes
    # df = data_compilation('cleaned_datasets', 
    #                  ['video_title', 'date_released_utc', 'view_count', 'like_count',
    #                   'comment_count', 'date_collected_utc', 'video_duration_H',
    #                   'video_duration_M', 'video_duration_S', 'channel_name'],
    #                   ['youtuber_channel_details.csv'])
    # df.to_csv('compiled_datasets/compiled_df.csv', index=False)


if __name__ == '__main__':
    main()