# scripts/scrape_website.py
import asyncio
import time
from playwright.async_api import async_playwright
from pathlib import Path

class WebScraper:
    def __init__(self, start_url: str, output_dir: Path):
        self.start_url = start_url
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Scraper initialized for URL: {self.start_url}")

    async def run(self):
        print("Launching Playwright...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True) # Use headless=False for debugging
            page = await browser.new_page()
            
            print(f"Navigating to {self.start_url}...")
            await page.goto(self.start_url, wait_until="networkidle")
            
            # --- This is the part you customize for each site ---
            # For Wikipedia, the main content is in a div with id="mw-content-text"
            print("Extracting content...")
            content_locator = page.locator("#mw-content-text .mw-parser-output")
            article_text = await content_locator.inner_text()
            # ----------------------------------------------------

            # Save the content to a file
            filename = self.start_url.split("/")[-1] + ".txt"
            output_path = self.output_dir / filename
            
            print(f"Saving content to {output_path}...")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(article_text)
            
            await browser.close()
            print("Scraping complete.")
            return output_path

async def main():
    # --- Configuration ---
    target_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    output_directory = Path("./scraped_data")

    scraper = WebScraper(start_url=target_url, output_dir=output_directory)
    await scraper.run()

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Script finished in {end_time - start_time:.2f} seconds.")