import webvtt
import google_auth_oauthlib.flow
# import google.oauth2.credentials

from google.oauth2 import service_account
import googleapiclient.discovery
import googleapiclient.errors
from google.cloud import translate_v2 as translate
import io
import os
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import langcodes, language_data
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

translate_credentials = service_account.Credentials.from_service_account_file(
    os.path.abspath('client_secret_file.json'))
translator = translate.Client(credentials=translate_credentials)

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl", "https://www.googleapis.com/auth/youtubepartner"]
api_service_name = "youtube"
api_version = "v3"
youtube = None
credentials = None
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    os.path.abspath('client_secret_youtube.json'), scopes=scopes)
flow.redirect_uri = 'http://127.0.0.1:5000/'
authorization_url, state = flow.authorization_url(access_type='offline',include_granted_scopes='true')



def create_client(credentials):
    youtube_client = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    return youtube_client


def get_captions(video_id):
    list_request = youtube.captions().list(part="id", videoId=video_id)
    response = list_request.execute()
    print(len(response))
    cap_reqeust = youtube.captions().download(id=response["items"][0]["id"], tfmt="vtt")
    cap_response = cap_reqeust.execute()
    f = io.BytesIO(cap_response)
    # download = MediaIoBaseDownload(f, cap_reqeust)
    # complete = False
    # while not complete:
    #     status, complete = download.next_chunk()
    byte_string = f.read()
    text = byte_string.decode("UTF-8")
    file = io.StringIO(text)
    captions = webvtt.read_buffer(file)

    return captions


def translate_captions(captions, language):
    language = str(langcodes.find(language))
    for caption in captions:
        new_line = translator.translate(caption.text, target_language=language)
        caption.text = new_line["translatedText"]

    return captions


def back_2_bytes(captions):
    f = io.StringIO()
    for caption in captions:
        f.write(caption.start + "-->" + caption.end + "\n")
        f.write(caption.text + "\n")
        f.write("\n")
    f.seek(0)
    bytes_caps = io.BytesIO(f.getvalue().encode('utf8'))
    return bytes_caps


def upload_captions(io_captions, lang_string, video_id):
    lang_code = str(langcodes.find(lang_string))
    request = youtube.captions().insert(
        part="snippet",
        body={
            "snippet": {
                "language": lang_code,
                "name": lang_string + " captions",
                "videoId": video_id
            }
        },
        media_body=MediaIoBaseUpload(io_captions, mimetype="text/vtt")
    )
    response = request.execute()
    return

# pip install -r requirements.txt
