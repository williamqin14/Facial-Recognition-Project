import os
import pickle
from googleapiclient.discovery import build
import urllib.parse as p
import re

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Set the API key
API_KEY = "AIzaSyDK8oXW4DJHbpx4GaqXxIxCI6IPYT_2b4k"

def youtube_authenticate():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    creds = None

    # Build the service with the API key
    youtube = build(api_service_name, api_version, developerKey=API_KEY)
    return youtube

# Authenticate to YouTube API using API key
youtube = youtube_authenticate()
print("Authenticated to YouTube API.")

def get_video_id_by_url(url):
    """
    Return the Video ID from the video `url`
    """
    # split URL parts
    parsed_url = p.urlparse(url)
    # get the video ID by parsing the query of the URL
    video_id = p.parse_qs(parsed_url.query).get("v")
    if video_id:
        return video_id[0]
    else:
        raise Exception(f"Wasn't able to parse video URL: {url}")

# API call to get video info from YouTube
def get_video_details(youtube, **kwargs):
    video_response = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        **kwargs
    ).execute()

    items = video_response.get("items")[0]
    # get the snippet, statistics & content details from the video response
    snippet         = items["snippet"]
    statistics      = items["statistics"]
    content_details = items["contentDetails"]
    # get infos from the snippet
    if "maxres" in snippet["thumbnails"]:
        video_thumbnail = snippet["thumbnails"]["maxres"]["url"]
    elif "high" in snippet["thumbnails"]:
        video_thumbnail = snippet["thumbnails"]["high"]["url"]
    else:
        # Fallback to default thumbnail if neither 'maxres' nor 'high' is available
        video_thumbnail = snippet["thumbnails"]["default"]["url"]
    channel_title   = snippet["channelTitle"]
    title           = snippet["title"]
    description     = snippet["description"]
    publish_time    = snippet["publishedAt"]
    # get stats infos
    comment_count = statistics["commentCount"]
    like_count    = statistics["likeCount"]
    view_count    = statistics["viewCount"]
    # get duration from content details
    duration = content_details["duration"]
    # duration in the form of something like 'PT5H50M15S'
    # parsing it to be something like '5:50:15'
    match = re.search(r"PT(\d+H)?(\d+M)?(\d+S)", duration)
    if match:
        parsed_duration = match.groups()
    else:
        parsed_duration = ("0H", "0M", "0S")
    duration_str = ""
    for d in parsed_duration:
        if d:
            duration_str += f"{d[:-1]}:"
    duration_str = duration_str.strip(":")

    video_info = {
        "video_thumbnail": video_thumbnail,
        "channel_title": channel_title,
        "title": title,
        "description": description,
        "publish_time": publish_time,
        "comment_count": comment_count,
        "like_count": like_count,
        "view_count": view_count,
        "duration": duration_str,
    }

    return video_info

def print_video_infos(video_response):
    v = video_response
    print(f"""\
    Title: {v["title"]}
    Video thumbnail url: {v["video_thumbnail"]}
    Description: {v["description"]}
    Channel Title: {v["channel_title"]}
    Publish time: {v["publish_time"]}
    Duration: {v["duration"]}
    Number of comments: {v["comment_count"]}
    Number of likes: {v["like_count"]}
    Number of views: {v["view_count"]}
    """)

# video_url = "https://www.youtube.com/watch?v=bfC9GWSAQQQ"
# # parse video ID from URL
# video_id = get_video_id_by_url(video_url)
# # make API call to get video info
# response = get_video_details(youtube, id=video_id)
# # print extracted video infos
# print_video_infos(response)

# API call to search for videos matching a search term
def search(youtube, **kwargs):
    return youtube.search().list(
        part="snippet",
        **kwargs
    ).execute()

# # search for the query 'python' and retrieve 2 items only
# response = search(youtube, q="python", maxResults=2)
# items = response.get("items")
# for item in items:
#     # get the video ID
#     video_id = item["id"]["videoId"]
#     # get the video details
#     video_response = get_video_details(youtube, id=video_id)
#     # print the video details
#     print_video_infos(video_response)
#     print("="*50)

def parse_channel_url(url):
    """
    This function takes channel `url` to check whether it includes a
    channel ID, user ID or channel name
    """
    path = p.urlparse(url).path
    id = path.split("/")[-1]
    if "/c/" in path:
        return "c", id
    elif "/channel/" in path:
        return "channel", id
    elif "/user/" in path:
        return "user", id

def get_channel_id_by_url(youtube, url):
    """
    Returns channel ID of a given `id` and `method`
    - `method` (str): can be 'c', 'channel', 'user'
    - `id` (str): if method is 'c', then `id` is display name
        if method is 'channel', then it's channel id
        if method is 'user', then it's username
    """
    # parse the channel URL
    method, id = parse_channel_url(url)
    if method == "channel":
        # if it's a channel ID, then just return it
        return id
    elif method == "user":
        # if it's a user ID, make a request to get the channel ID
        response = get_channel_details(youtube, forUsername=id)
        items = response.get("items")
        if items:
            channel_id = items[0].get("id")
            return channel_id
    elif method == "c":
        # if it's a channel name, search for the channel using the name
        # may be inaccurate
        response = search(youtube, q=id, maxResults=1)
        items = response.get("items")
        if items:
            channel_id = items[0]["snippet"]["channelId"]
            return channel_id
    raise Exception(f"Cannot find ID:{id} with {method} method")

# API call to get videos of a specific channel from YouTube
def get_channel_videos(youtube, **kwargs):
    return youtube.search().list(
        **kwargs
    ).execute()

# API call to get info about a specific channel from YouTube
def get_channel_details(youtube, **kwargs):
    response = youtube.channels().list(
        part="statistics,snippet,contentDetails",
        **kwargs
    ).execute()

    # # the following is grabbing channel info# extract channel infos
    snippet = response["items"][0]["snippet"]
    statistics = response["items"][0]["statistics"]
    channel_country = snippet["country"]
    channel_description = snippet["description"]
    channel_creation_date = snippet["publishedAt"]
    channel_title = snippet["title"]
    channel_subscriber_count = statistics["subscriberCount"]
    channel_video_count = statistics["videoCount"]
    channel_view_count  = statistics["viewCount"]

    channel_info = {
        "channel_country": channel_country,
        "channel_description": channel_description,
        "channel_creation_date": channel_creation_date,
        "channel_title": channel_title,
        "channel_subscriber_count": channel_subscriber_count,
        "channel_video_count": channel_video_count,
        "channel_view_count": channel_view_count,
    }

    return channel_info


# the following is grabbing channel info
channel_url = "https://www.youtube.com/channel/UCijULR2sXLutCRBtW3_WEfA"
# get the channel ID from the URL
channel_id = get_channel_id_by_url(youtube, channel_url)
# get the channel details
# response = get_channel_details(youtube, id=channel_id)

# print(f"""
# Title: {response["channel_title"]}
# Published At: {response["channel_creation_date"]}
# Description: {response["channel_description"]}
# Country: {response["channel_country"]}
# Number of videos: {response["channel_video_count"]}
# Number of subscribers: {response["channel_subscriber_count"]}
# Total views: {response["channel_view_count"]}
# """)


# the following is grabbing channel videos
def get_channel_all_info(youtube, channel_url, n_pages=1):
    channel_id = get_channel_id_by_url(youtube, channel_url)
    # extract video information into lists
    n_videos = 0
    videos = []

    next_page_token = None
    for i in range(n_pages):
        params = {
            'part': 'snippet',
            'q': '',
            'channelId': channel_id,
            'type': 'video',
        }
        if next_page_token:
            params['pageToken'] = next_page_token
        res = get_channel_videos(youtube, **params)
        channel_videos = res.get("items")
        for video in channel_videos:
            n_videos += 1
            video_id = video["id"]["videoId"]
            # easily construct video URL by its ID
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_info = get_video_details(youtube, id=video_id)
            videos.append({"video_response": video_info, "video_url": video_url})
            # print(f"================Video #{n_videos}================")
            # print the video details
            # print_video_infos(video_response)
            # print(f"Video URL: {video_url}")
            # print("="*40)
        # print("*"*100)
        # if there is a next page, then add it to our parameters
        # to proceed to the next page
        if "nextPageToken" in res:
            next_page_token = res["nextPageToken"]
        else:
            break

    return videos

def get_video_thumbnail_urls(channel_url, n_pages=2):
    videos = get_channel_all_info(youtube, channel_url, n_pages)
    urls = []
    for video in videos:
        urls.append(video["video_response"]["video_thumbnail"])
    return urls

# get_video_thumbnail_urls("https://www.youtube.com/channel/UCijULR2sXLutCRBtW3_WEfA")
