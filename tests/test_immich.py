from immich_client import ImmichClient

def main():
    """Test the connection."""
    with ImmichClient() as client:
        print("Testing connection to Immich server...")
        if client.ping():
            print("Connected successfully!")
        else:
            print("Failed to connect")
            return

        print("\nFetching random asset metadata...")
        assets = client.get_random_assets(1)
        if assets:
            asset = assets[0]
            print(f"Asset ID: {asset['id']}")
            print(f"Type: {asset['type']}")
            print(f"Original filename: {asset.get('originalFileName', 'N/A')}")
        else:
            print("No assets found")


if __name__ == "__main__":
    main()
