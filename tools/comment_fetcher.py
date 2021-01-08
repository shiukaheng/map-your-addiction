from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import multiprocessing.dummy
import time
import itertools
import json

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# I'll try & optimize the parsing. Able to plug in video ID from the dictionary.
#takeout = parse_history.parse_history_file()


# Code modified from: https://python.gotrained.com/youtube-api-extracting-comments/

# Splits a list into n smaller lists. Used for parallelization.
def split_list(input_list, n):
    remainder = len(input_list) % n
    result = []
    if len(input_list) > n:
        sublist_length_without_remainder = int((len(input_list)-remainder) / n)
        for x in range(n):
            result.append(input_list[:sublist_length_without_remainder])
            input_list = input_list[sublist_length_without_remainder:]
        for x in range(remainder):
            result[x].append(input_list.pop(0))
    else:
        result = [[x] for x in input_list]+[[] for x in range(n-len(input_list))]
    return result


# Function that authenticates client with a user and returns credentials
def get_authenticated_service():
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    #  Check if the credentials are invalid or do not exist
    if not credentials or not credentials.valid:
        # Check if the credentials have expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_console()

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


# Function that gets all comments from a video ID
def get_video_comments(service_obj, video_id, max_pages=3):
    page = 1
    comments = []
    try:
        results = service_obj.commentThreads().list(part="snippet", videoId=video_id, textFormat="plainText").execute()
        while results:
            for item in results['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)

            if 'nextPageToken' in results:
                if page >= max_pages:
                    break
                pageToken = results['nextPageToken']
                results = service_obj.commentThreads().list(part="snippet", videoId=video_id, textFormat="plainText", pageToken=pageToken).execute()
                page += 1
            else:
                break
    except HttpError as e:
        error_reason = json.loads(e.content)['error']['errors'][0]['message']
        if not error_reason == "The video identified by the <code><a href=\"/youtube/v3/docs/commentThreads/list#videoId\">videoId</a></code> parameter has disabled comments.":
            raise e
    print(video_id)
    return comments


# Function that gets all comments from a list of video IDs. Runs threaded by default.
def get_video_comments_batch(video_id_list, threads=10, max_pages=3):
    split = split_list(video_id_list, threads)
    def _get_video_comments(split_video_id_list):
        _service = get_authenticated_service()
        result = []
        for video_id in split_video_id_list:
            result.append(get_video_comments(_service, video_id, max_pages=max_pages))
            print(video_id)
        return result

    p = multiprocessing.dummy.Pool(threads)
    results = list(itertools.chain.from_iterable(p.map(_get_video_comments, split)))
    return results


# Function that adds comments to video dictionaries. Runs threaded by default.
def get_video_comments_batch2(video_list, threads=10, max_pages=3):
    split = split_list(video_list, threads)

    def _get_video_comments(split_video_list):
        _service = get_authenticated_service()
        for video in split_video_list:
            video['comments'] = get_video_comments(_service, video['video_id'], max_pages=max_pages)
        return split_video_list

    p = multiprocessing.dummy.Pool(len([x for x in split if len(x) != 0]))
    results = list(itertools.chain.from_iterable(p.map(_get_video_comments, split)))
    return results



if __name__ == '__main__':
    a_time = time.time()
    data = get_video_comments_batch([takeout[0]['vid_id'], "SFYBVGdB7MU", "IaLwrLRpZ1w", "afhSDK5DJqA"], threads=4)
    b_time = time.time()
    print(b_time-a_time)
    print(data)

#print(takeout[0]['vid_url'])
