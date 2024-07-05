import requests
from typing import Dict


def _make_responce(
    method: str, url: str, headers: Dict, params: Dict, timeout: int, success=200
):
    response = requests.request(
        method, url, headers=headers, params=params, timeout=timeout
    )
    status_code = response.status_code

    if status_code == success:
        return response
    return status_code


def _search_location(
    method: str,
    url: str,
    headers: Dict,
    params: Dict,
    timeout: int,
    success=200,
    func=_make_responce,
):
    url = "{}/v1/hotels/locations".format(url)
    response = func(method, url, headers=headers, params=params, timeout=timeout)
    return response


def _best_city_hotels(
    method: str,
    url: str,
    headers: Dict,
    params: Dict,
    timeout: int,
    success=200,
    func=_make_responce,
):
    url = "{}/v1/hotels/search".format(url)
    response = func(method, url, headers=headers, params=params, timeout=timeout)
    return response


class APIInterface:

    @staticmethod
    def get_location():
        return _search_location

    @staticmethod
    def get_best_hotel():
        return _best_city_hotels


if __name__ == "__main__":
    _make_responce()
    _search_location()
    _best_city_hotels()
    APIInterface()
