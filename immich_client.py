import os

import httpx
from dotenv import load_dotenv

load_dotenv()


class ImmichClient:
    def __init__(self):
        self.api_key = os.getenv("IMMICH_API_KEY")
        self.base_url = os.getenv("IMMICH_URL")

        if not self.api_key or not self.base_url:
            raise ValueError("IMMICH_API_KEY and IMMICH_URL must be set in .env")

        self.base_url = self.base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=f"{self.base_url}/api",
            headers={"x-api-key": self.api_key},
            timeout=30.0,
        )

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def ping(self) -> bool:
        """Test connection to the Immich server."""
        try:
            response = self._client.get("/server/ping")
            response.raise_for_status()
            return response.json().get("res") == "pong"
        except httpx.HTTPError:
            return False

    def get_random_assets(self, count: int = 1) -> list[dict]:
        """Get random asset metadata from the library."""
        response = self._client.get("/assets/random", params={"count": count})
        response.raise_for_status()
        return response.json()

    def get_asset_thumbnail_bytes(self, asset_id: str, size: str = "preview") -> bytes:
        """
        Download asset thumbnail as raw bytes.

        Args:
            asset_id: The asset ID
            size: 'thumbnail' (blurred, fast) or 'preview' (larger, clearer)
        """
        response = self._client.get(f"/assets/{asset_id}/thumbnail", params={"size": size})
        response.raise_for_status()
        return response.content

    def get_albums(self) -> list[dict]:
        """Get all albums."""
        response = self._client.get("/albums")
        response.raise_for_status()
        return response.json()

    def get_album_assets(self, album_id: str) -> list[dict]:
        """Get all assets in an album."""
        response = self._client.get(f"/albums/{album_id}")
        response.raise_for_status()
        return response.json().get("assets", [])