import requests
import xml.etree.ElementTree as ET
import re
from urllib.parse import urlparse
import pandas as pd

def main():
    sitemap_index_url = input("Enter sitemap index URL: ").strip()

    try:
        response = requests.get(sitemap_index_url)
        response.raise_for_status()
    except Exception as e:
        print(f"Error getting sitemap index: {e}")
        return

    root = ET.fromstring(response.content)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    # Collect the sitemaps from the index
    sitemaps = [loc.text.strip() for loc in root.findall(".//sm:loc", ns)]

    if not sitemaps:
        print("No sitemaps found")
        return

    print(f"Found {len(sitemaps)} sitemaps. URLS are being collected..")

    # Resultaten groeperen per type
    grouped_urls = {}

    for sm_url in sitemaps:
        path = urlparse(sm_url).path
        match = re.search(r'/([^/-]+(?:_[^/-]+)?)-', path)
        if match:
            sm_type = match.group(1)
        else:
            sm_type = "unknown"

        print(f"Process {sm_url} as type '{sm_type}'")

        try:
            sm_resp = requests.get(sm_url)
            sm_resp.raise_for_status()
            sm_root = ET.fromstring(sm_resp.content)

            urls = [loc.text.strip() for loc in sm_root.findall(".//sm:loc", ns)]

            if sm_type not in grouped_urls:
                grouped_urls[sm_type] = []
            grouped_urls[sm_type].extend(urls)

        except Exception as e:
            print(f"Error retrieving {sm_url}: {e}")

    # Write everything to one .xlsx file with multiple tabs
    excel_filename = "sitemap_urls.xlsx"
    with pd.ExcelWriter(excel_filename, engine="openpyxl") as writer:
        for sm_type, urls in grouped_urls.items():
            df = pd.DataFrame(urls, columns=["url"])
            # (max 31 characters, no special characters)
            sheet_name = sm_type[:31].replace(":", "").replace("/", "_")
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"All urls have been saved in '{excel_filename}' with multiple tabs.")

if __name__ == "__main__":
    main()

# xx GertKnibbe