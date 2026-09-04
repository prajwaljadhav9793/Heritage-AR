from app import create_app

app = create_app()
client = app.test_client()
test_app = create_app()
client = test_app.test_client()

r1 = client.get("/timeline/")
t1 = r1.get_data(as_text=True)
print("raigad page:", r1.status_code, "| has Hampi link:", 'data-site="hampi"' in t1, "| default heading Raigad:", "RAIGAD" in t1)

r2 = client.get("/timeline/?site=hampi")
t2 = r2.get_data(as_text=True)
print("hampi page:", r2.status_code,
      "| heading:", "HAMPI" in t2 and "THROUGH TIME" in t2,
      "| note:", "Hampi archive is currently open" in t2,
      "| Krishnadevaraya event:", "Krishnadevaraya" in t2,
      "| Talikota event:", "Talikota" in t2,
      "| raigad link present:", 'data-site="raigad"' in t1)

r3 = client.get("/timeline/?site=bogus")
print("bogus site falls back:", r3.status_code, "RAIGAD" in r3.get_data(as_text=True))
