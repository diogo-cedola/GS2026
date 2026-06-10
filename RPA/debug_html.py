import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def debug():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://spaceflightnow.com/launch-schedule/", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # Mostra todas as classes únicas
    classes = set()
    for tag in soup.find_all(class_=True):
        for c in tag.get("class", []):
            classes.add(c)
    print("=== CLASSES ENCONTRADAS ===")
    print(sorted(classes))

    # Mostra primeiros 3000 chars do body
    print("\n=== PRIMEIROS 3000 CHARS DO BODY ===")
    print(soup.body.get_text()[:3000] if soup.body else "sem body")

asyncio.run(debug())
