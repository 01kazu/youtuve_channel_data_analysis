import googleapiclient.discovery # type: ignore
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
import dill as pickle # type: ignore
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Union


load_dotenv()
# Youtube Api
API_KEY = os.getenv('API_KEY')  
# BRIGHT DATA (Scraping browser [access parameters])
AUTH = os.getenv('AUTH') 
SBR_WEBDRIVER = os.getenv('SBR_WEBDRIVER')


def get_youtube_video_details(video_id: str) -> List[Union[str,datetime,int]]:
    """
    Returns details about youtube video from the video's id.

    Parameters
    ----------
    video_id : str
        Youtube video id

    Returns
    -------
    list
        a list of video details        
    """
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
    # print(response)
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


def get_youtube_video_id(video_link: str) -> str:
    """
    Returns video id.

    Parameters
    ----------
    video_link : str
        Youtube video link

    Returns
    -------
    str
        Youtube video id. 
    """
    link_parts = video_link.split('=')
    video_id = link_parts[-1]
    return video_id 
    

def get_all_youtubers_videos_links(youtuber_link: str) -> List[str]:
    """
    Returns video links from youtuber's channel.

    Parameters
    ----------
    youtuber_link : str
        Youtuber's channel videos link

    Returns
    -------
    links : list
        List of youtube videos from the Youtuber's channel
    """
    print('Connecting...')  
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome') # type: ignore 
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
        current_links_len = 0
        current_page_loc = 0
        while True:
            driver.execute_script(f"window.scrollBy({current_page_loc}, {current_page_loc+1000})")
            current_page_loc += 1900
            # print(f"{current_page_loc=}") 
            driver.implicitly_wait(10)
            links = driver.find_elements(By.ID, 'video-title-link')
            links_len = len(links)
            print(f"{links_len=}")
            if current_links_len == links_len:
                print("Found all videos")
                break
            current_links_len = links_len
            last_link = links[-1]
            details = last_link.get_attribute('aria-label')            
            if ("9 months" in details) or ("year" in details):
                print("Found for a particular period")
                break
        # links = driver.find_elements(By.ID, 'video-title-link')
        links = [link.get_attribute('href') for link in links]
        return links   
        # store the links object in a pickle to prevent retrieving the data continuously


def save_data(data :List[str], filename :str, filepath: str) -> None:
    """
    Saves video links in pickle format.

    Parameters
    ----------
    data : list[str]
        List containing links to the youtuber's videos
    filename : str
        Name of the file to be created
    filepath : str
        Directory to the file
    """
    if not filepath.endswith('/'):
        filepath = filepath + '/'
    with open(f'{filepath}{filename}', 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_data(filename: str, filepath: str ='') -> List[str]:
    """
    Loads data using pickle

    Parameters
    ----------
    filename : str
        Name of pickle file to be loaded
    filepath : str
        Directory to the file to be loaded

    Returns
    -------
    list
        List containing links to the youtuber's videos
    """
    if not filepath.endswith('/'):
        filepath = filepath + '/'
    with open(f'{filepath}{filename}', 'rb') as handle:
        return pickle.load(handle)
    
    
def remove_names_extracted(txt_file_path: str, name_file_path: str) -> None:
    """
    Removes names from a text file 

    Parameters
    ----------
    txt_file_path : str
        file where names are to be deleted
    name_file_path : str
        file containing the names
    """
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


def youtube_video_details_csv(youtuber_link: str, 
                              channel_name: str ='',
                              dirpath: str = 'datasets', 
                              use_pickled_data: bool = False) -> None:
    """
    Creates a csv file containing various details of different videos of a Youtuber.

    Parameters
    ----------
    youtuber_link : str
        Link to the youtuber's page containing their all their videos
    channel_name : str, optional
        Name of the Youtuber's channel
    dirpath : str, optional
        Directory where csv files created would be saved.  
    use_pickled_data : bool, optional
        If pickled data exists, you can decide if you'd prefer to use it 
        or get new data from the youtuber's link
    """
    if not channel_name:
        link_parts = youtuber_link.split('/')
        channel_name = [link_part for link_part in link_parts if link_part.startswith('@')][0]
        channel_name = channel_name.replace('@', '')
    dir = f'scrapped_data_pickle/'
    filename = f'{channel_name}.pickle'

    with open(f'datasets/{channel_name}.csv', 'a', newline='', encoding='utf-8') as file:
        if os.path.exists(dir+filename) and use_pickled_data:
            video_links = load_data(filename, dir)
        else:
            video_links = get_all_youtubers_videos_links(youtuber_link)
            print('videos are collected using selenium.')
            save_data(video_links, filename, dir)
        writer = csv.writer(file)
        csv_file = os.path.isfile(os.path.join(dirpath, f'{channel_name}.csv'))
        os.path.join
        if not csv_file:  
            writer.writerow(['video_title', 'video_duration', 'date_released_utc', 
                             'view_count', 'like_count', 'comment_count', 'date_collected_utc'])
        for video_link in video_links:
            id = get_youtube_video_id(video_link)
            details = get_youtube_video_details(id)
            current_datetime = datetime.now(timezone.utc)
            details.append(current_datetime)
            writer.writerow(details)


def get_youtuber_channel_details(youtuber_link: str) -> List[str]:
    """
    Returns a div containing the channel name, subscriber count and videos count.

    Parameters
    ----------
    youtuber_link : str
        Link containing the youtuber's channel name, subscriber count and videos count

    Returns
    -------
    div_classes : List[str]
        List of divs containing the channel name, subscriber count and videos count
    """
    print('Connecting...')  
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')  # type: ignore
    with Remote(sbr_connection, options=ChromeOptions()) as driver:  
        print('Connected! Navigating...')  
        driver.get(youtuber_link)
        youtube_details_class = "yt-content-metadata-view-model-wiz__metadata-row.yt-content-metadata-view-model-wiz__metadata-row--metadata-row-inline"
        try:
            WebDriverWait(
                driver, 
                30  # seconds
                        ).until(
                EC.presence_of_element_located((By.CLASS_NAME, youtube_details_class))
            )
        except TimeoutException:
            print("could not find youtube_details class")
        div_classes = driver.find_elements(By.CLASS_NAME, youtube_details_class)
        div_classes = [class_.text for class_ in div_classes]  
        return div_classes 
    

def save_youtuber_channel_details(youtuber_link: str, 
                                  filepath: str, 
                                  details: List[str]= []) -> None:
    """
    Saves Youtube channel details such as channel_name, subscriber count 
    and videos_count to a csv file.

    Parameters
    ----------
    youtuber_link : str
        Link containing the youtuber's channel name, subscriber count and videos count
    filepath : str
        Path where csv file created would be aved
    details : List[str]
        List of divs containing the channel name, subscriber count and videos count
    """
    if not details:
        details = get_youtuber_channel_details(youtuber_link)
    channel_name = details[0]
    subscriber_count, _ , videos_count = details[1].split('\n')
    dir = os.path.join(filepath, f'youtuber_channel_details.csv')        
    # Make a condition that would check if the file exists before overwriting the file
    csv_file = os.path.isfile(dir)
    with open(dir, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not csv_file:
            writer.writerow(['channel_name', 'subscriber_count', 'videos_count'])
            csv_file = False
        writer.writerow([channel_name, subscriber_count, videos_count])



def main()->None:
    with open('top_20_nigerian_food_content_creators.txt', 'r') as file:
        for line in file.readlines():
            _ , channel_link = line.split(',')
            details = get_youtuber_channel_details(channel_link)
            channel_name = details[0]
            
            youtube_video_details_csv(channel_link, channel_name, 'datasets', False)
            # save channel name, total subscribers and total videos uploaded
            # save_youtuber_channel_details(channel_link, 'datasets', details)

if __name__ == '__main__':
    main()
