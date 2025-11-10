# scripts/scrape_website.py
import asyncio
import time
import os
from playwright.async_api import async_playwright
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class WebScraper:
    # Add optional login_details parameter
    def __init__(self, start_url: str, output_dir: Path, login_details: dict = None):
        self.start_url = start_url
        self.output_dir = output_dir
        self.login_details = login_details
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Scraper initialized for URL: {self.start_url}")

    async def _login(self, page):
        """Performs the login action if login_details are provided."""
        if not self.login_details:
            return
        
        login_url = self.login_details.get("login_url")
        username = self.login_details.get("username")
        password = self.login_details.get("password")

        if not all([login_url, username, password]):
            print("Login details incomplete. Skipping login.")
            return

        print(f"Navigating to login page: {login_url}")
        await page.goto(login_url)

        # --- Customize these locators for the specific site ---
        print("Entering credentials...")
        await page.fill("#username", username)
        await page.fill("#password", password)
        await page.click("input[type='submit']")
        # ----------------------------------------------------
        
        print("Waiting for login to complete...")
        await page.wait_for_url("http://quotes.toscrape.com/", wait_until="networkidle")
        print("Login successful.")


    async def run(self):
        print("Launching Playwright...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Perform login first if needed
            await self._login(page)
            
            print(f"Navigating to target page: {self.start_url}...")
            await page.goto(self.start_url, wait_until="networkidle")
            
            # --- Customize for the target page ---
            print("Extracting content...")
            # For quotes.toscrape.com, each quote is in a div with class="quote"
            quotes = await page.locator(".quote").all_inner_texts()
            article_text = "\n---\n".join(quotes)
            # ------------------------------------

            filename = self.start_url.split("/")[-2] + ".txt" # a better filename
            output_path = self.output_dir / filename
            
            print(f"Saving content to {output_path}...")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(article_text)
            
            await browser.close()
            print("Scraping complete.")
            return output_path

async def main():
    # --- Configuration for a site that REQUIRES LOGIN ---
    login_config = {
        "login_url": "http://quotes.toscrape.com/login",
        "username": os.getenv("SCRAPER_USERNAME"),
        "password": os.getenv("SCRAPER_PASSWORD")
    }
    
    # We want to scrape the main page, which shows different content when logged in
    target_url = "http://quotes.toscrape.com/"
    output_directory = Path("./scraped_data")

    scraper = WebScraper(start_url=target_url, output_dir=output_directory, login_details=login_config)
    await scraper.run()

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Script finished in {end_time - start_time:.2f} seconds.")