from playwright.async_api import async_playwright
from seleniumbase import cdp_driver
import asyncio
import time
import random
import sys

from helpers import (  
    print_json_data, save_to_csv,
    In_stock_items , Duplicate_sku_checker,
    price_change_checker ,modify_csv_list ,
    scrape_product
)
from scraper import (
    pagination , get_total_pages,
    get_id_json_data , get_cards_links,
    get_card_div , get_main_div
)

from emailer import(
    send_summary_email
)

headers = ["sku","name","color","ratings","price","price currency","Availability"]

async def start_driver():
    driver =  await cdp_driver.start_async(
        lang="en",
        browser_executable_path=r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        headless=False,
        uc=True  # Enables undetected-chrome mode for better anti-bot evasion
    )

    await driver.get("about:blank")
    return driver

async def main():
    driver = None
    context = None
    browser = None
    try : 
        driver = await start_driver()
        endpoint_url = driver.get_endpoint_url()
    except Exception as e:
        print(f"❌ Failed to initialize Brave Driver engine: {e}")
        return

    async with async_playwright() as p:

        try:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else await context.new_page()

            model = input("Enter iphone seriers to scrape : ")
            if not model:
                print("⚠️ No model entered. Exiting script gracefully.")
                return

            await page.goto(f"https://www.flipkart.com/search?q=iphone+{model}", wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(0.1,0.7))

            total_pages = await get_total_pages(page)
            if total_pages == 0:
                print("⚠️ No matching pagination pages found on Flipkart. Exiting.")
                return
            
            tab_pages = [await context.new_page() for _ in range(5)]

            ftv = True
            any_changes_detected = False
            final_row_count = 0

            for pages in range(total_pages):

                if not ftv == True:
                
                    url = pagination(pages+1,model)
                    await page.goto(url, wait_until="domcontentloaded")
                    await asyncio.sleep(random.uniform(0.1,0.7)) 
                    
                ftv = False

                main_div = get_main_div(page)
                card = get_card_div(main_div)


                links = []
                if await card.count() > 0:
                    links = await get_cards_links(card)

                if not links:
                    continue

                for batch_start in range(0, len(links), 5):
                    chunk = links[batch_start:batch_start+5]
                    tasks = []

                    for i, link in enumerate(chunk):
                        if i < len(tab_pages):
                            tasks.append(scrape_product(tab_pages[i], link, headers))

                    batch_results = await asyncio.gather(*tasks)

                    for count in batch_results:
                        if count is not None and isinstance(count, int) and count > 0:
                            if count > 0: 
                                any_changes_detected = True
                                final_row_count = count

                                
            if any_changes_detected:
                print("Price changes detected! sending email....")
                try:
                    send_summary_email(final_row_count)
                    print("Email Successfully sent ✅, check your inbox.")
                except Exception as e:
                    print(f"Something went wrong while sending email! - {e}")
            else:
                print("✅ Run complete. No price modifications tracked. Skipping email summary.")


        except KeyboardInterrupt:
            print("\n🛑 Execution interrupted by user (Ctrl+C). Cleaning up workspace resources...")
        
        except Exception as general_err:
            print(f"\n❌ Unexpected runtime loop failure: {general_err}")

        finally:
            print("🔒 Shutting down background network channels and browser contexts...")
            # Pure severance: Closes tabs before shutting down the global driver server process
            try:
                if context:
                    await context.close()
                if browser:
                    await browser.close()
            except Exception:
                pass # Suppress dynamic pipe closure errors
                
            if driver:
                try:
                    driver.stop()
                except Exception:
                    pass
            
            print("👋 System safely terminated. Goodbye!")
            print("\n========================================")
            try:
                input("Press Enter To Exit...")
            except (KeyboardInterrupt, EOFError):
                sys.exit(0) # Exit instantly if they press Ctrl+C again at the final terminal gate

            
if __name__ == "__main__":
    asyncio.run(main())


    