
# import libraries
from bs4 import BeautifulSoup
import requests
import csv

# Building functions to pull various product data

# function to check the validity of the product URL

def check_link(soup):
    try:
        sub_page = requests.get(soup, headers=headers)
        soup2 = BeautifulSoup(sub_page.content, "html.parser")
        return ""

    except:
        return "bad link"


# retrieving the product title from the product page

def get_title(soup):
    try:
        return soup.find("span", attrs = {'id': 'productTitle'}).text.strip()
    except:
        return "Error, check the link"


# retrieving the product cost from the product page, storing it as a float value
        
def get_price(soup):
    try:    
        return float(soup.find("span", attrs = {'class': 'a-price a-text-price a-size-medium apexPriceToPay'}).find("span", attrs = {'class': 'a-offscreen'}).text.strip("$ "))  
    except:    
        try:
            return float(soup.find("span", attrs = {'class': 'a-price aok-align-center'}).find("span", attrs = {'class': 'a-offscreen'}).text.strip("$ "))
        except:
            return 0


# retrieving the average customer rating for the product from the product page        
        
def get_rating(soup):
    try:
        return (soup.find("i", attrs = {'class': 'a-icon a-icon-star a-star-4-5 cm-cr-review-stars-spacing-big'}).text.strip("out of 5 stars"))
    except:
        return ""


# retrieving the product availability from the product page

def get_stock(soup):
    try:
        return soup.find("span", attrs = {'class': 'a-size-medium a-color-success'}).text.strip()
    except:
        return ""


# filtering the brand name after retrieving the title using get_title function

def get_brand(soup):
    if "head" in get_title(soup).lower():
        return "Head"
    elif "wilson" in get_title(soup).lower():
        return "Wilson"
    elif "babolat" in get_title(soup).lower():
        return "Babolat"
    elif "yonex" in get_title(soup).lower():
        return "Yonex"
    elif get_title(soup) == "":
        return "Title not found"
    else:
        return "Other Brand"


# retrieving the total amazon reviews posted on the product

def get_review_count(soup):
    try:
        return (soup.find("a", attrs = {'id': 'acrCustomerReviewLink'}).text.strip(" ratings"))
    except:
        return ""


# creating a function to store the product data in a csv file

def write_dict_list_to_csv(data_list, filename):
    # Extract column names from the keys of the first dictionary
    fieldnames = list(data_list[0].keys())

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Write each dictionary as a row in the CSV file
        writer.writerows(data_list)

    print(f"Data stored in '{filename}'.")


def main():

    
    # http://httpbin.org/get to get the user agent data for the headers

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

    # creating a list to store product href data from the search page
    product_hrefs = []

    #Pulling product page urls from the first 5 pages and storing them in product_hrefs

    for x in range(1,6):
        URL = f"https://www.amazon.ca/s?k=tennis+racket&i=sporting&rh=n%3A2242989011%2Cp_89%3ABabolat%7CHEAD%7CWilson%7CYONEX&dc&qid=1687390998&rnid=7590290011&ref=sr_nr_p_89_5&ds=v1%3A6ZIJSU2BVM2Kmnzns%2Bglmsz2vut1AmfrJyCEboObpd8&page={x}"
        page = requests.get(URL, headers=headers)
        main_soup = BeautifulSoup(page.content, "html.parser")
        product_hrefs = product_hrefs + (main_soup.find_all("a", attrs={'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'}))
        
    # creating a list to store product url
    product_links = []

    # Converitng collected hrefs into usable links and storing in product_links list

    for product_href in product_hrefs:
        product_links.append("https://amazon.ca" + product_href.get('href'))

    # Creating a list to store data for each product in a dictionary format

    products = []

    # going through each product link and getting product information and storing it as a list of dictionary for each product

    for link in product_links:
        sub_page = requests.get(link, headers=headers)
        soup2 = BeautifulSoup(sub_page.content, "html.parser")
        product = {
        "title": get_title(soup2),
        "brand": get_brand(soup2),
        "price": get_price(soup2),
        "rating": get_rating(soup2),
        "total reviews": get_review_count(soup2),
        "stock": get_stock(soup2),
        "link": link}
        products.append(product)
        
    # ''' After reviewing the above product list, it was determined that the results would need to be filtered to remove the following
    #  1. Remove tennis racquets that are NOT for adults (product titles that contain words such as junior, kids, etc.)
    #  2. Remove tennis accessories that are NOT racquets such as racquet grips (observed value of these products is less than $25)
    #  3. Remove cheap quality products, anything below $25
    # '''

    filtered_products = []

    # filtering products to remove items that are NOT racquets or are racquets for kids

    for product in products:
        if any(keyword in product["title"].lower() for keyword in ["junior", "youth", "child", "kid"]) or (0 < product["price"] < 25):
            continue
        else:
            filtered_products.append(product)
        

    # Calling the function to convert the list of dictionary and save it in a csv file

    write_dict_list_to_csv(filtered_products, "Output_3_1_Tennis_Racquets_Filtered.csv")

    write_dict_list_to_csv(products, "Output_3_2_Tennis_Racquets_all.csv")


if __name__ == "__main__":
    main()


