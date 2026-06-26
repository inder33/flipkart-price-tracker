import json

#------------------------------------------------------[ GET MAIN PAGE MAIN DIV ]
def get_main_div(page):

    return page.locator("div#container")

#-------------------------------------------------------[ GET DIV THAT CONATINS ALL DIV's OF PRODUCTS ]
def get_card_div(main_div):

    if main_div :
        #print("div found successfully ..")
        return main_div.locator("div[style*=overflow]")
#-------------------------------------------------------[ GET ALL LINKS FROM ALL TH EPRODUCT DIV's]

async def get_cards_links(card):
    product_links = []
    if card:

        card_list = card.locator("div[data-id]")
        card_count = await card_list.count()
                
        if card_list:
            #print(f"card list found , total card found = {card_count}")

            for i in range(card_count):

                anchor = card_list.nth(i).locator("a[href*='/p/']")
                links = await anchor.get_attribute("href")
                links_found = await anchor.count()

                #print("=============================")
                #print(links)

                product_links.append(links)
    else:
        print("no anchors found for links!")

    return product_links

#----------------------------------------------------------[ GET JSON DATA FROM : SCRIPT TYPE=application/JSON-LD]
async def get_id_json_data(page):
    data_list = []

    # Using .first ensures it doesn't throw an error if multiple script tags match
    script = page.locator("script[type*='application/ld+json']").first

    data = await script.inner_text()
    json_data = json.loads(data)

    print("======================================================================")

    # Safely extract the first item from the JSON array
    product = json_data[0] if isinstance(json_data, list) and json_data else {}

    # Extract nested dictionaries safely, defaulting to an empty dict {} if missing
    offers = product.get("offers", {})
    aggregate_rating = product.get("aggregateRating", {})

    # Safely parse the availability URL string
    availability_url = offers.get("availability", "")
    if "/" in availability_url:
        # Using [-1] gets the last element safely regardless of string length
        availability = availability_url.split("/")[-1]
    else:
        availability = "N/A"

    # Build your data list using .get() for everything
    data_list.append({
        "sku": product.get("sku", "N/A"),
        "name": product.get("name", "N/A"),
        "color": product.get("color", "N/A"),  # <--- This fixes your 'color' error!
        "ratings": aggregate_rating.get("ratingValue", "N/A"),
        "price": offers.get("price", "N/A"),
        "priceCurrency": offers.get("priceCurrency", "N/A"),
        "availability": availability
    })   

    return data_list

#---------------------------------------------------------------[ FIND TOTAL PAGES TO SCRAPE ]
async def get_total_pages(page):
    # 1. Get ALL span elements as a list
    spans = await page.locator("span").all()
    
    total_pages = None  # 2. Initialize variable to avoid scope errors
    
    for span in spans:
        text = (await span.inner_text()).strip() # Strip whitespace for accurate matching
        
        if text.startswith("Page 1 of"): # Note: Flipkart usually capitalizes 'Page'
            total_pages_text = text.split(" ")
            total_pages = int(total_pages_text[3])
            break # Stop once found to save time
    
    return total_pages

#-----------------------------------------------------------------[ PAGINATE THROUGH PAGES ]
def pagination(current_page,model):

    Current_url = f"https://www.flipkart.com/search?q=iphone+{model}+pro+max&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"
    final_page_url = Current_url + f"&page={current_page}"
    return final_page_url