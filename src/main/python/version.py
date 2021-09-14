import requests

marmara_download_url = 'https://github.com/marmarachain/marmara/releases/download/'
app_release_url = 'https://github.com/marmarachain/marmara-connector/releases/'
marmara_api_url = "https://api.github.com/repos/marmarachain/marmara/releases/latest"
app_api_url = "https://api.github.com/repos/marmarachain/marmara-connector/releases/latest"
"""
requests to get the latest releases' tag_name of a git api url
"""


def git_request_tag(api_url):
    try:
        response = requests.get(api_url)
        tag_name = response.json()["tag_name"]
        return tag_name
    except Exception as e:
        return e



"""
combines the marmara latest download_url with latest releases' tag name to form the latest download url
"""


def latest_marmara_download_url():
    tag_name = git_request_tag(marmara_api_url)
    if type(tag_name) == str:
        latest_download_url = marmara_download_url + tag_name
        return latest_download_url
    else:
        return 'Connection Error'


"""
combines the app's latest release url with latest releases' tag name to form the latest release url
"""


def latest_app_release_url():
    tag_name = git_request_tag(app_api_url)
    if type(tag_name) == str:
        latest_release_url = app_release_url + tag_name
        return latest_release_url
    else:
        return 'Connection Error'

