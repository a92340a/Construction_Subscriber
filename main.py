import functions_framework
import requests
import os
from google.cloud import storage
from difflib import unified_diff
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import TextSendMessage

# Environment variables for GCS and LINE
load_dotenv()

TARGET_URL = 'https://www.delpha.com.tw/service/progress009'
BUCKET_NAME = os.getenv('BUCKET_NAME')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_USER_ID = os.getenv('LINE_USER_ID')
LINE_NOTIFY_API = 'https://notify-api.line.me/api/notify'


def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
        raise
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
        raise
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
        raise
    except requests.exceptions.RequestException as err:
        print(f"Something went wrong: {err}")
        raise

def upload_to_gcs(content, filename):
    try:
        client = storage.Client()
        bucket = client.get_bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(content, content_type='text/plain; charset=utf-8')
    except Exception as e:
        print(f"Error uploading to GCS: {e}")
        raise

def download_from_gcs(filename):
    try:
        client = storage.Client()
        bucket = client.get_bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        return blob.download_as_string()
    except Exception as e:
        print(f"Error downloading from GCS: {e}")
        raise


@functions_framework.http
def main(request):
    taipei_tz = pytz.timezone('Asia/Taipei')
    today = datetime.now(tz=taipei_tz).strftime('%Y-%m-%d')
    yesterday = (datetime.now(tz=taipei_tz) - timedelta(1)).strftime('%Y-%m-%d')
    headers = {'Authorization': 'Bearer ' + LINE_CHANNEL_ACCESS_TOKEN} 

    # step1. fetch the latest html
    current_html = fetch_html(TARGET_URL)

    # step2. upload the latest html to GCS
    upload_to_gcs(current_html, f'website_{today}.html')

    # step3. verify the html if it's different from the previous html 
    # if there's any change between the websites, a notification passed to Line Chat room with the delpha official url
    try:
        previous_html = download_from_gcs(f'website_{yesterday}.html').decode('utf-8')
        if previous_html:
            diff = list(unified_diff(previous_html.splitlines(), current_html.splitlines(), lineterm=''))
            if diff:
                diff_message = '\n'.join(diff[:10])  # Send first 10 lines of diff
                data = {'message':f'[大華昇耕工程進度更新通知]\n新照片上傳了！\nhttps://www.delpha.com.tw/service/progress009\n\n{diff_message}'}
                data = requests.post(LINE_NOTIFY_API, headers=headers, data=data)
            else:
                data = {'message':f'[大華昇耕工程進度更新通知]\n今日 {today} 無新進度上傳。'}
                data = requests.post(LINE_NOTIFY_API, headers=headers, data=data)
        return '{"status":"200", "data": "Delivery to Line Chat room successfully"}'
    except:
        return '{"status":"500", "data": "Fail to delivery"}'


