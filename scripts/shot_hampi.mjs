export default async function run(page, ui) {
  // Wait for the carousel JS to be live (counter element present and wired)
  await page.waitForSelector("[data-heritage-carousel] [data-current-slide]");
  await page.waitForTimeout(300); // let DOMContentLoaded handlers attach

  const card = page.locator('.rail-dot[data-go-to="1"]');
  await card.scrollIntoViewIfNeeded();
  await card.click({ force: false }); // real mouse click at card center

  // Wait until the counter shows 02 (Hampi slide active)
  await page.waitForFunction(
    () =>
      document.querySelector("[data-current-slide]")?.textContent.trim() ===
      "02",
    { timeout: 5000 },
  );
  await page.waitForTimeout(1200); // let the crossfade finish

  await page.screenshot({ path: "scripts/hampi-slide.png" });
  return "Hampi slide is active (counter = 02)";
}
