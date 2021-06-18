import requests

download_url = 'https://github.com/marmarachain/marmara/releases/download/'


def git_request_tag():
    response = requests.get("https://api.github.com/repos/marmarachain/marmara/releases/latest")
    tag_name = response.json()["tag_name"]
    return tag_name


def latest_marmara_zip_url():
    tag_name = git_request_tag()
    linux_release_url = download_url + tag_name + '/MCL-linux-' + tag_name + '.zip'
    # print(linux_release_url)
    return linux_release_url
