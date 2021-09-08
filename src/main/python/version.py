import requests

marmara_download_url = 'https://github.com/marmarachain/marmara/releases/download/'
app_release_url = 'https://github.com/marmarachain/marmara-connector/releases/'
marmara_api_url = "https://api.github.com/repos/marmarachain/marmara/releases/latest"
app_api_url = "https://api.github.com/repos/marmarachain/marmara-connector/releases/latest"
"""
requests to get the latest releases' tag_name of a git api url
"""


def git_request_tag(api_url):
    response = requests.get(api_url)
    tag_name = response.json()["tag_name"]
    return tag_name


"""
combines the marmara download_url with latest releases' tag name to form the url for linux zip file
"""


def latest_marmara_download_url():
    tag_name = git_request_tag(marmara_api_url)
    latest_download_url = marmara_download_url + tag_name
    return latest_download_url


def latest_app_release_url():
    tag_name = git_request_tag(app_api_url)
    latest_release_url = app_release_url + tag_name
    return latest_release_url

