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
    # Add new parameters to the constructor
    def __init__(self, start_url: str, output_dir: Path, content_selector: str, output_filename: str, login_details: dict = None):
        self.start_url = start_url
        self.output_dir = output_dir
        self.login_details = login_details
        self.content_selector = content_selector
        self.output_filename = output_filename
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

            await self._login(page)
            
            print(f"Navigating to target page: {self.start_url}...")
            await page.goto(self.start_url, wait_until="networkidle")
            
            print(f"Extracting content using selector: '{self.content_selector}'...")
            # Use the content_selector argument instead of a hardcoded value
            content_elements = await page.locator(self.content_selector).all_inner_texts()
            article_text = "\n---\n".join(content_elements)

            # Use the output_filename argument
            output_path = self.output_dir / self.output_filename
            
            print(f"Saving content to {output_path}...")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(article_text)
            
            await browser.close()
            print("Scraping complete.")
            return output_path

# NEW, MORE FLEXIBLE main() function
async def main():
    import argparse

    # 1. Set up the argument parser
    parser = argparse.ArgumentParser(description="Scrape content from a website.")
    parser.add_argument("--target-url", required=True, help="The URL of the page to scrape.")
    parser.add_argument("--content-selector", required=True, help="CSS selector for the main content to extract.")
    parser.add_argument("--output-filename", required=True, help="Name of the file to save the scraped content.")
    parser.add_argument("--login", action="store_true", help="Set this flag to perform a login before scraping.")

    args = parser.parse_args()
    
    # 2. Prepare configuration
    output_directory = Path("/scraped_data")
    login_config = None
    
    if args.login:
        print("Login flag is set. Preparing login configuration...")
        login_config = {
            "login_url": "http://quotes.toscrape.com/login", # This could also be an argument
            "username": os.getenv("SCRAPER_USERNAME"),
            "password": os.getenv("SCRAPER_PASSWORD")
        }

    # 3. Create and run the scraper with the parsed arguments
    scraper = WebScraper(
        start_url=args.target_url,
        output_dir=output_directory,
        login_details=login_config,
        content_selector=args.content_selector, # Pass the selector to the class
        output_filename=args.output_filename
    )
    await scraper.run()


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Script finished in {end_time - start_time:.2f} seconds.")