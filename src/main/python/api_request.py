import requests
import logging

logging.getLogger(__name__)

marmara_download_url = 'https://github.com/marmarachain/marmara/releases/download/'
app_release_url = 'https://github.com/marmarachain/marmara-connector/releases/'
marmara_api_url = "https://api.github.com/repos/marmarachain/marmara/releases/latest"
app_api_url = "https://api.github.com/repos/marmarachain/marmara-connector/releases/latest"

coinpaprika = 'https://api.coinpaprika.com/v1/coins/mcl-marmara-credit-loops/markets'
exchange_market_api_list = {'coinpaprika': coinpaprika}
"""
requests to get the latest releases' tag_name of a git api url
"""


def git_request_tag(api_url):
    try:
        response = requests.get(api_url, timeout=5)
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


def get_marmara_stats():
    try:
        response = requests.get('https://explorer3.marmara.io/insight-api-komodo/stats', timeout=5)
        return response.json()
    except Exception:
        try:
            response = requests.get('https://explorer2.marmara.io/insight-api-komodo/stats', timeout=5)
            return response.json()
        except Exception:
            try:
                response = requests.get('https://explorer.marmara.io/insight-api-komodo/stats', timeout=5)
                return response.json()
            except Exception as e:
                logging.error(e)
                return 'error'


def mcl_exchange_market(api_list_key):
    try:
        response = requests.get(exchange_market_api_list.get(api_list_key), timeout=5)
        return response.json()
    except Exception as e:
        logging.error(e)
        return 'error'
