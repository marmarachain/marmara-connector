import requests

marmara_download_url = 'https://github.com/marmarachain/marmara/releases/download/'
app_download_url = 'https://github.com/marmarachain/marmara-connector/releases/download/'
marmara_api_url = "https://api.github.com/repos/marmarachain/marmara/releases/latest"
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


def latest_marmara_zip_url():
    tag_name = git_request_tag()
    latest_release_url = marmara_download_url + tag_name  # should be added + '/MCL-linux.zip' or '/MCL-win.zip according to OS
    # print(linux_release_url)
    return latest_release_url
