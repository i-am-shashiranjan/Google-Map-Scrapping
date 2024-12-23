import csv
import time
import re
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class GoogleMapScraper:
    def __init__(self):
        self.output_file_name = "TATA_AIA_LIFE_1.csv"
        self.headless = False
        self.driver = None
        self.unique_check = []

    def config_driver(self):
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        s = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=s, options=options)
        self.driver = driver

    def save_data(self, data):
        header = ['Name', 'Rating', 'Reviews_count', 'Address', 'Pincode', 'City', 'Category', 'Phone', 'Website', 'Google_maps_url', 'Latitude', 'Longitude']
        with open(self.output_file_name, 'a', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if data[0] == 1:
                writer.writerow(header)
            writer.writerow(data)

    def parse_contact(self, business):
        try:
            contact = business.find_elements(By.CLASS_NAME, "W4Efsd")[2].text.split("·")[-1].strip()
        except:
            contact = ""

        if "+91" not in contact:
            try:
                contact = business.find_elements(By.CLASS_NAME, "W4Efsd")[3].text.split("·")[-1].strip()
            except:
                contact = ""

        return contact

    def parse_rating_and_review_count(self, business):
        try:
            reviews_block = business.find_element(By.CLASS_NAME, 'AJB7ye').text.split("(")
            rating = reviews_block[0].strip()
            reviews_count = reviews_block[1].split(")")[0].strip()
        except:
            rating = ""
            reviews_count = ""

        return rating, reviews_count

    def parse_address_and_category(self, business):
        try:
            address_block = business.find_elements(By.CLASS_NAME, "W4Efsd")[2].text.split("·")
            if len(address_block) >= 2:
                address = address_block[1].strip()
                category = address_block[0].strip()
            elif len(address_block) == 1:
                address = ""
                category = address_block[0]
        except:
            address = ""
            category = ""

        return address, category

    def get_lat_long_from_url(self, url):
        match = re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', url)
        if match:
            latitude = match.group(1)
            longitude = match.group(2)
            return latitude, longitude
        return "", ""

    def get_business_info(self):
        time.sleep(2)
        for business in self.driver.find_elements(By.CLASS_NAME, 'THOPZb'):
            name = business.find_element(By.CLASS_NAME, 'fontHeadlineSmall').text
            rating, reviews_count = self.parse_rating_and_review_count(business)
            address, category = self.parse_address_and_category(business)
            contact = self.parse_contact(business)

            try:
                google_maps_url = business.find_element(By.CLASS_NAME, "hfpxzc").get_attribute("href")
            except NoSuchElementException:
                google_maps_url = ""

            latitude, longitude = self.get_lat_long_from_url(google_maps_url)

            try:
                website = business.find_element(By.CLASS_NAME, "lcr4fd").get_attribute("href")
            except NoSuchElementException:
                website = ""

            unique_id = "".join([name, rating, reviews_count, address, category, contact, website, google_maps_url, latitude, longitude])
            if unique_id not in self.unique_check:
                if google_maps_url:
                    self.driver.execute_script(f"window.open('{google_maps_url}');")
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    time.sleep(2)

                    try:
                        address_element = self.driver.find_element(By.CLASS_NAME, 'rogA2c')
                        address = address_element.text
                    except NoSuchElementException:
                        address = ""

                    pincode_match = re.search(r'\b\d{6}\b', address)
                    pincode = pincode_match.group(0) if pincode_match else ""
                    if pincode_match:
                        address = address.replace(pincode, "").strip()

                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])

                    data = [name, rating, reviews_count, address, pincode, city, category, contact, website, google_maps_url, latitude, longitude]
                    self.save_data(data)
                    self.unique_check.append(unique_id)

    def load_companies(self, url):
        print("Getting business info", url)
        self.driver.get(url)
        time.sleep(5)

        panel_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'
        
        flag = True
        i = 0
        while flag:
            try:
                print(f"Page No : {i + 2}")
                scrollable_div = self.driver.find_element(By.XPATH, panel_xpath)  # Re-fetch the scrollable div
                self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                time.sleep(2)

                if "You've reached the end of the list." in self.driver.page_source:
                    flag = False

                self.get_business_info()
                i += 1

            except StaleElementReferenceException:
                print("StaleElementReferenceException encountered. Re-fetching scrollable div.")
                continue  # Retry the loop to re-fetch elements


# Main execution
business_scraper = GoogleMapScraper()
business_scraper.config_driver()

# arunachal_pradesh = [
    
#     "EastSiang",
#     "Itanagar",
#     "KraDaadi",
#     "KurungKumey",
#     "Lohit",
#     "Longding",
#     "LowerDibang Valley",
#     "LowerSubansiri",
#     "Namsai",
#     "PapumPare",
#     "ShiYomi",
#     "Siang",
#     "Tawang",
#     "Tirap",
#     "UpperSiang",
#     "UpperSubansiri",
#     "WestKameng",
#     "WestSiang"
# ]


cities = [
"AndhraPradesh",
# "ArunachalPradesh",
"Assam",    
"bihar",
"Chhattisgarh",
"Goa",
"Gujarat",
"Haryana",
"HimachalPradesh",
"Jharkhand",
"Karnataka",
"Kerala",
"MadhyaPradesh",
"Maharashtra",
"Manipur",
"Meghalaya",
"Mizoram",
"Nagaland",
"Odisha",
"Punjab",
"Rajasthan",
"Sikkim",
"TamilNadu",
"Telangana",
"Tripura",
"UttarPradesh",
"Uttarakhand",
"WestBengal"]


citiess = ["india"]

business_scraper.save_data([1]) 

for city in citiess:
    url = f"https://www.google.co.in/maps/search/TATA+AIA+LIFE+BRANCHES+in+all+{city}/"
    business_scraper.load_companies(url)

business_scraper.driver.quit()

