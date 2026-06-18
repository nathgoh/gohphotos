try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

from immich_client import ImmichClient
from epaper_display import EpaperDisplay


def main() -> None:
    with ImmichClient() as client:
        assets = client.get_random_assets(count=1)
        if not assets:
            raise RuntimeError("No assets returned from Immich")
        asset_id = assets[0]["id"]
        image_bytes = client.get_asset_thumbnail_bytes(asset_id, size="preview")

    EpaperDisplay().show(image_bytes)


if __name__ == "__main__":
    main()
