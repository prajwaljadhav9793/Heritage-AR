from app import create_app

app = create_app()
client = app.test_client()
test_app = create_app()
client = test_app.test_client()
html = client.get("/").get_data(as_text=True)

checks = {
    "Hampi slide present": 'data-title="Hampi"' in html,
    "Hampi slide image": "timeline/virupaksha.jpg" in html,
    "Hampi timeline link": "site=hampi" in html,
    "Hampi story card": "story-label\">Hampi<" in html,
    "5 rail dots": html.count("rail-dot") == 5,
    "rail count 01 / 05": "01 / 05" in html,
    "pagination 05": "<i></i>05</p>" in html,
    "raigad slide still first": 'data-title="Raigad Fort"' in html,
    "story card goTo=4": 'data-go-to="4"' in html,
}
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL"), name)
