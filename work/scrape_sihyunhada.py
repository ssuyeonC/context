import csv
import time
import requests
START_ID = 1
END_ID = 1000
OUTPUT_FILE = "/Users/jeongsuyeon/conductor/workspaces/product/prague/.context/work/sihyunhada_products_1_1000.csv"
BASE_URL = "https://booking-api.sihyunhada.com/api/v1/products/items/{}"
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
})
rows = []
for product_id in range(START_ID, END_ID + 1):
    url = BASE_URL.format(product_id)
    try:
        response = session.get(url, timeout=10)
        if response.status_code != 200:
            print(f"[SKIP] {product_id}: status={response.status_code}")
            continue
        data = response.json()
        item = data.get("data")
        if not item:
            print(f"[EMPTY] {product_id}")
            continue
        row = {
            "id": item.get("id"),
            "categoryName": item.get("categoryName"),
            "groupName": item.get("groupName"),
            "productName": item.get("productName"),
            "price": item.get("price"),
            "durationMinutes": item.get("durationMinutes"),
            "branchId": item.get("branchId"),
            "branchName": item.get("branchName"),
            "productCategoryId": item.get("productCategoryId"),
            "productGroupId": item.get("productGroupId"),
            "description": item.get("description"),
            "isActive": item.get("isActive"),
        }
        rows.append(row)
        print(f"[FOUND] {product_id}: {row['productName']}")
        time.sleep(0.1)
    except requests.RequestException as e:
        print(f"[ERROR] {product_id}: request failed - {e}")
    except ValueError as e:
        print(f"[ERROR] {product_id}: invalid json - {e}")
    except Exception as e:
        print(f"[ERROR] {product_id}: unexpected - {e}")
fieldnames = [
    "id",
    "categoryName",
    "groupName",
    "productName",
    "price",
    "durationMinutes",
    "branchId",
    "branchName",
    "productCategoryId",
    "productGroupId",
    "description",
    "isActive",
]
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
print(f"\n완료: {len(rows)}개 상품 저장됨")
print(f"파일명: {OUTPUT_FILE}")
