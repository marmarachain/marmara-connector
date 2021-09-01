import requests

download_url = 'https://github.com/marmarachain/marmara/releases/download/'

"""
requests to get the latest releases' tag_name of marmarachain user's marmara repo
"""


def git_request_tag():
    response = requests.get("https://api.github.com/repos/marmarachain/marmara/releases/latest")
    tag_name = response.json()["tag_name"]
    return tag_name


"""
combines the marmara download_url with latest releases' tag name to form the url for linux zip file
"""


def latest_marmara_zip_url():
    tag_name = git_request_tag()
    latest_release_url = download_url + tag_name  # should be added + '/MCL-linux.zip' or '/MCL-win.zip according to OS
    # print(linux_release_url)
    return latest_release_url
