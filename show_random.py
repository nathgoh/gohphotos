try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

from immich_client import ImmichClient
from epaper_driver.epaper_display import EPD


def main() -> None:
    with ImmichClient() as client:
        assets = client.get_random_assets(count=1)
        if not assets:
            raise RuntimeError("No assets returned from Immich")
        asset_id = assets[0]["id"]
        image_bytes = client.get_asset_bytes(asset_id, size="original")

    EPD().show(image_bytes)


if __name__ == "__main__":
    main()
