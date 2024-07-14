import requests
from typing import Dict


def _make_response(
    # keyword: str,
    method: str,
    url: str,
    headers: Dict,
    params: Dict,
    timeout: int,
    success=200
):
    # url = ("{}/v1/hotels/"+keyword).format(url)
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
    func=_make_response,
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
    func=_make_response,
):
    url = "{}/v1/hotels/search".format(url)
    response = func(method, url, headers=headers, params=params, timeout=timeout)
    return response


def _info_hotel(
    method: str,
    url: str,
    headers: Dict,
    params: Dict,
    timeout: int,
    success=200,
    func=_make_response,
):
    url = "{}/v1/hotels/data".format(url)
    response = func(method, url, headers=headers, params=params, timeout=timeout)
    return response


def _hotel_photos(
    method: str,
    url: str,
    headers: Dict,
    params: Dict,
    timeout: int,
    success=200,
    func=_make_response,
):
    url = "{}/v1/hotels/photos".format(url)
    response = func(method, url, headers=headers, params=params, timeout=timeout)
    return response


def _hotel_desc(
    method: str,
    url: str,
    headers: Dict,
    params: Dict,
    timeout: int,
    success=200,
    func=_make_response,
):
    url = "{}/v1/hotels/description".format(url)
    response = func(method, url, headers=headers, params=params, timeout=timeout)
    return response


class APIInterface:

    @staticmethod
    def make_response():
        return _make_response
    @staticmethod
    def get_location():
        return _search_location

    @staticmethod
    def get_best_hotel():
        return _best_city_hotels

    @staticmethod
    def get_hotel_info():
        return _info_hotel

    @staticmethod
    def get_hotel_photo():
        return _hotel_photos

    @staticmethod
    def get_hotel_desc():
        return _hotel_desc


if __name__ == "__main__":
    _make_response()
    _search_location()
    _best_city_hotels()
    _info_hotel()
    _hotel_photos()
    _hotel_desc()
    APIInterface()
