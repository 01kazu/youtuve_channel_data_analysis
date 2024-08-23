import numpy as np
import pandas as pd
from datetime import datetime
from os import listdir
from os.path import isfile, join

# DATE = {'month': , 'week': 7}
def extract_data_scraping():
    # df = pd.read_csv('file_2.csv')
    # print(df.head())
    # # Split by THE FARMER’s DAUGHTER and get the first item after the split for the VIDEO TITLE
    # df_other = df['video_data'].str.split('by THE FARMER’s DAUGHTER', expand=True, n=1)
    # df['video_title'] = df_other[0]
    # df_other = df_other[1].str.split('views', expand=True, n=1)
    # df['view_count'] = df_other[0]
    # df['time_posted'] = df_other[1]
    # print(df.head())
    # print(df.info())
    pass

def get_digits(string):
    char_list = [char for char in string if char.isdigit()]
    return ''.join(char_list)

# def get_video_duration(video_len):
#     video_length = ''
#     video_dict = {'H': 0, 'M': 0, 'S': 0}
#     for index, char in enumerate(video_len):
#         if char.isdigit():
#             video_length += char
#         if len(video_length) > 0 and not char.isdigit():
#             key = video_len[index]
#             video_dict[key] = video_length
#             video_length = ''
#     return video_dict


def data_cleaning(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=['date_released_utc'])
    # Extract video duration from string
    df['video_duration_H'] = df['video_duration'].apply(
        lambda duration: duration.split('H')[0] if (duration.find('H') > 0)  else '0' 
        ).apply(get_digits)
    df['video_duration_M'] = df['video_duration'].apply(
        lambda duration: duration.split('M')[0] if (duration.find('M') > 0)  else '0' 
        ).apply(get_digits)
    df['video_duration_S'] = df['video_duration'].apply(
        lambda duration: duration.split('M')[1]
        ).apply(get_digits)
    
    # Replace empty strings '' with '0'
    df = df.replace({'video_duration_H': '', 
                 'video_duration_M': '', 
                 'video_duration_S': ''}, '0') 
    # CHange datatype from string to int
    df = df.astype(
            {'video_duration_H': int, 
             'video_duration_M': int, 
             'video_duration_S': int})
    df = df.drop(columns=['video_duration'])
    return df


def main()-> None:
    for file in listdir('datasets'):
        if isfile(join('datasets', file)):
            df = data_cleaning(join('datasets', file))
            df.to_csv(join('cleaned_datasets', file), index=False )


if __name__ == '__main__':
    main()