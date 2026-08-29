from app import create_app

app = create_app()
client = app.test_client()
html = client.get("/timeline/?site=hampi").get_data(as_text=True)

images = [
    "hampi-lakshmi-narasimha.png",
    "hampi-royal-centre-ruins.png",
    "hampi-elephant-stables.png",
    "hampi-hazara-rama-temple.png",
    "hampi-lotus-mahal-interior.png",
]

for image in images:
    in_html = f"/static/images/timeline/{image}" in html
    import os
    exists = os.path.exists(f"app/static/images/timeline/{image}")
    print(f"{image}: in page={in_html} file exists={exists}")

# Every referenced image should exist on disk
import re
refs = re.findall(r'src="(/static/images/timeline/[^"]+)"', html)
missing = [r for r in refs if not os.path.exists("app" + r)]
print("total timeline image refs:", len(refs), "| missing files:", missing)
