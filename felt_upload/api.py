from pathlib import Path
from typing import Any, Callable, List, Optional
from urllib.parse import urljoin

import requests
from requests_toolbelt import MultipartEncoderMonitor


class FeltAPIError(Exception):
    pass


class UnauthorizedError(FeltAPIError):
    pass


def drop_empty(dct: dict[Any, Any]) -> dict[Any, Any]:
    """Drop empty values from a dict."""
    return {key: value for key, value in dct.items() if value}


class Felt:
    def __init__(
        self,
        api_token: str,
        base_url: str = "https://felt.com/api/v1/",
        session: Optional[requests.Session] = None,
    ):
        self.api_token = api_token
        self.base_url = base_url
        self.session = session or requests.Session()

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "authorization": f"Bearer {self.api_token}",
            "content-type": "application/json",
        }

    def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        resp = self.session.request(
            method=method,
            url=urljoin(self.base_url, url),
            headers={
                **kwargs.get("headers", {}),
                **self._headers,
            },
            **kwargs,
        )

        if resp.status_code == 401:
            raise UnauthorizedError
        else:
            resp.raise_for_status()
        return resp.json()

    def user(self) -> dict[str, str]:
        """Make a /user request"""
        json_data = self._request("get", "user")
        return {
            "name": json_data["data"]["attributes"]["name"],
            "email": json_data["data"]["attributes"]["email"],
        }

    def create_map(
        self,
        title: Optional[str] = None,
        *,
        basemap: Optional[str] = None,
        zoom: Optional[float] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ) -> dict[str, str]:
        """Create an empty map."""
        data = self._request(
            "post",
            "maps",
            json=drop_empty(
                {
                    "title": title,
                    "basemap": basemap,
                    "zoom": zoom,
                    "lat": lat,
                    "lon": lon,
                }
            ),
        )
        return {
            "id": data["data"]["id"],
            "title": data["data"]["attributes"]["title"],
            "url": data["data"]["attributes"]["url"],
        }

    def create_layer(
        self,
        map_id: str,
        files: List[Path],
        *,
        name: Optional[str] = None,
        fill_color: Optional[str] = None,
        stroke_color: Optional[str] = None,
        update_file_progress: Optional[Callable[[str, int, int], None]] = None,
    ) -> dict[str, str]:
        """Create a layer and upload files."""
        data = self._request(
            "post",
            f"maps/{map_id}/layers",
            json=drop_empty(
                {
                    "name": name,
                    "fill_color": fill_color,
                    "stroke_color": stroke_color,
                    "file_names": [f.name for f in files],
                }
            ),
        )
        attributes = data["data"]["attributes"]
        url = attributes["url"]
        presigned_attributes = attributes["presigned_attributes"]
        layer_id = attributes["layer_id"]

        for path in files:

            def monitor_callback(monitor: MultipartEncoderMonitor) -> None:
                if update_file_progress:
                    update_file_progress(path.name, monitor.bytes_read, monitor.len)

            m = MultipartEncoderMonitor.from_fields(
                fields={
                    **presigned_attributes,
                    "file": (
                        path.name,
                        path.open("rb"),
                    ),
                },
                callback=monitor_callback,
            )
            resp = self.session.request(
                "post", url, data=m, headers={"Content-Type": m.content_type}
            )
            resp.raise_for_status()

            self._request(
                "post",
                f"maps/{map_id}/layers/{layer_id}/finish_upload",
                json={"filename": path.name},
            )

        return {
            "id": layer_id,
        }

    def import_layer(
        self,
        map_id: str,
        layer_url: str,
        *,
        name: Optional[str] = None,
    ) -> dict[str, str]:
        """Import layer from a url."""
        resp = self._request(
            "post",
            f"maps/{map_id}/layers/url_import",
            json=drop_empty(
                {
                    "layer_url": layer_url,
                    "name": name,
                }
            ),
        )

        return {"id": resp["data"]["id"]}
