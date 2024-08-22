import googleapiclient.discovery
from selenium.webdriver import Remote, ChromeOptions  
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection  
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timezone
import pandas as pd
import csv
import dill as pickle
import os
from dotenv import load_dotenv


load_dotenv()
# Google Api
API_KEY = os.getenv('API_KEY')  
# BRIGHT DATA (Scraping browser [access parameters])
AUTH = os.getenv('AUTH') 
SBR_WEBDRIVER = os.getenv('SBR_WEBDRIVER')

def get_youtube_video_details(video_id):
    print('Getting youtuber data with the google api')
    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=API_KEY
    )
    # Request body
    # https://www.youtube.com/watch?v=3hKsm3fl0D4
    request = youtube.videos().list(
        part='snippet,contentDetails,statistics',
        id= video_id
    )
    response = request.execute()
    print(response)
    video_title = response.get('items')[0].get('snippet').get('localized').get('title')
    video_duration = response.get('items')[0].get('contentDetails').get('duration')
    date_released = response.get('items')[0].get('snippet').get('publishedAt')
    if date_released is not None:
        date_released = pd.to_datetime(date_released)
    view_count = response.get('items')[0].get('statistics').get('viewCount')
    if view_count is not None:
        view_count = int(view_count)
    like_count = response.get('items')[0].get('statistics').get('likeCount')
    if like_count is not None:
        like_count = int(like_count)
    comment_count = response.get('items')[0].get('statistics').get('commentCount')
    if comment_count is not None:
        comment_count = int(comment_count)
    return [video_title, video_duration, date_released, view_count, like_count, comment_count]


def get_youtube_video_id(link):
    link_parts = link.split('=')
    return link_parts[-1]
    

def get_all_youtubers_videos_links(youtuber_link) :
    print('Connecting to Scraping Browser...')  
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')  
    with Remote(sbr_connection, options=ChromeOptions()) as driver:  
        print('Connected! Navigating...')  
        driver.get(youtuber_link)
        try:
            WebDriverWait(
                driver, 
                30  # seconds
                        ).until(
                EC.presence_of_element_located((By.ID, "video-title-link"))
            )
        except TimeoutException:
            print("could not find video title href link")
            
        links = driver.find_elements(By.ID, 'video-title-link')
        links = [link.get_attribute('href') for link in links]
        return links   
        # store the links object in a pickle to prevent retrieving the data continuously


def save_data(data, filename, file_path='') -> None:
    if not file_path.endswith('/'):
        file_path = file_path + '/'
    with open(f'{file_path}{filename}', 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_data(filename, file_path=''):
    if not file_path.endswith('/'):
        file_path = file_path + '/'
    with open(f'{file_path}{filename}', 'rb') as handle:
        return pickle.load(handle)
    
    
def remove_names_extracted(txt_file_path, name_file_path):
    files_to_remove = []
    for file in os.listdir(name_file_path):
        if file.endswith(".csv"):
            files_to_remove.append(file.split('.csv')[0])
    with open(txt_file_path, "r") as f:
        lines = f.readlines()
    with open(txt_file_path, 'w') as f:
        for line in lines:
            channel_name = line.split(',')[0]
            if channel_name not in files_to_remove:
                f.write(line)


def youtube_video_details_csv(youtuber_link, channel_name=''):
    if not channel_name:
        link_parts = youtuber_link.split('/')
        channel_name = [link_part for link_part in link_parts if link_part.startswith('@')]
        channel_name = channel_name[0].replace('@', '')
    dir = f'scrapped_data_pickle/'
    filename = f'{channel_name}.pickle'

    with open(f'datasets/{channel_name}.csv', 'w+', newline='', encoding='utf-8') as file:
        
        if os.path.exists(dir+filename): 
            print(dir+filename)
            video_links = load_data(filename, dir)
        else:
            video_links = get_all_youtubers_videos_links(youtuber_link)
            print('video are collected using selenium.')
            save_data(video_links, filename, dir)
                
        writer = csv.writer(file)
        writer.writerow(['video_title', 'video_duration', 'date_released_utc', 
                             'view_count', 'like_count', 'comment_count', 'date_collected_utc'])
        for video_link in video_links:
            id = get_youtube_video_id(video_link)
            details = get_youtube_video_details(id)
            current_datetime = datetime.now(timezone.utc)
            details.append(current_datetime)
            writer.writerow(details)


def main()->None:
    # with open('top_20_nigerian_food_content_creators.txt', 'r') as file:
    #     for line in file.readlines():
    #         channel_name, channel_link = line.split(',')
    #         youtube_video_details_csv(channel_link, channel_name)
    # youtube_video_details_csv('https://www.youtube.com/@wonderfulyakubu3599/videos')    
    # print(get_youtube_video_details('xvivHwoUcAc'))
    # remove_names_extracted("top_20_nigerian_food_content_creators.txt", "datasets/")
    get_all_youtubers_videos_links('https://www.youtube.com/@wonderfulyakubu3599/videos')
    
        

if __name__ == '__main__':
    main()
