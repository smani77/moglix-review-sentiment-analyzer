from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

import time
import re


def create_driver():

    options = Options()

    options.add_argument("--start-maximized")

    options.add_argument("--disable-notifications")

    options.add_argument("--disable-popup-blocking")

    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    options.add_argument(
        "--user-agent=Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        options=options
    )

    return driver


# ----------------------------------------------------------
# CLEAN TEXT
# ----------------------------------------------------------

def clean_text(text):

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ----------------------------------------------------------
# CHECK WHETHER TEXT LOOKS LIKE A REAL REVIEW
# ----------------------------------------------------------

def looks_like_review(text):

    if not text:
        return False

    text = clean_text(text)

    # Too short
    if len(text) < 15:
        return False

    # Too long usually means complete page/container text
    if len(text) > 1200:
        return False

    bad_words = [
        "add to cart",
        "buy now",
        "login",
        "sign up",
        "create account",
        "shopping cart",
        "delivery address",
        "related products",
        "similar products"
    ]

    lower = text.lower()

    for word in bad_words:

        if word in lower:

            return False

    return True


# ----------------------------------------------------------
# GET PRODUCT NAME
# ----------------------------------------------------------

def extract_product_name(soup):

    selectors = [

        "h1",

        "[class*='product-title']",

        "[class*='ProductTitle']",

        "[class*='productName']",

        "[class*='product-name']",

        "[data-testid*='product']"

    ]

    for selector in selectors:

        elements = soup.select(selector)

        for element in elements:

            text = clean_text(
                element.get_text(
                    " ",
                    strip=True
                )
            )

            if (
                text
                and len(text) > 5
                and len(text) < 300
            ):

                return text

    return "Moglix Product"


# ----------------------------------------------------------
# GET PRODUCT IMAGE
# ----------------------------------------------------------

def extract_product_image(soup):

    selectors = [

        "meta[property='og:image']",

        "meta[name='twitter:image']",

        "[class*='product'] img",

        "[class*='Product'] img"

    ]

    for selector in selectors:

        element = soup.select_one(selector)

        if not element:
            continue

        if element.name == "meta":

            image = element.get("content")

        else:

            image = (
                element.get("src")
                or element.get("data-src")
                or element.get("data-lazy-src")
            )

        if image:

            return image

    return ""


# ----------------------------------------------------------
# GET PRODUCT RATING
# ----------------------------------------------------------

def extract_product_rating(soup):

    selectors = [

        "[class*='rating']",

        "[class*='Rating']",

        "[class*='star']",

        "[class*='Star']"

    ]

    for selector in selectors:

        elements = soup.select(selector)

        for element in elements:

            text = clean_text(
                element.get_text(
                    " ",
                    strip=True
                )
            )

            # Find something like 4.5 or 4.0
            match = re.search(
                r"\b([0-5](?:\.\d)?)\b",
                text
            )

            if match:

                return match.group(1)

    return "N/A"


# ----------------------------------------------------------
# FIND REVIEW SECTION
# ----------------------------------------------------------

def find_review_section(soup):

    # Look for headings containing review-related words
    headings = soup.find_all(
        ["h2", "h3", "h4", "div", "span"]
    )

    for heading in headings:

        text = clean_text(
            heading.get_text(
                " ",
                strip=True
            )
        )

        if not text:
            continue

        lower = text.lower()

        review_words = [
            "customer reviews",
            "customer review",
            "product reviews",
            "product review",
            "reviews",
            "review"
        ]

        if any(
            word in lower
            for word in review_words
        ):

            # Try parent containers
            parent = heading

            for _ in range(5):

                if parent is None:
                    break

                children = parent.find_all(
                    recursive=True
                )

                if len(children) >= 2:

                    return parent

                parent = parent.parent

    return None


# ----------------------------------------------------------
# EXTRACT REVIEWS FROM REVIEW SECTION
# ----------------------------------------------------------

def extract_reviews(review_section):

    if review_section is None:

        return []

    reviews = []

    seen = set()

    # ------------------------------------------------------
    # FIRST METHOD:
    # Look for common review containers
    # ------------------------------------------------------

    selectors = [

        "[class*='review-card']",

        "[class*='ReviewCard']",

        "[class*='review-item']",

        "[class*='ReviewItem']",

        "[class*='review-container']",

        "[class*='ReviewContainer']",

        "[data-testid*='review']",

        "article"

    ]

    candidate_elements = []

    for selector in selectors:

        try:

            candidate_elements.extend(
                review_section.select(selector)
            )

        except Exception:
            pass

    # ------------------------------------------------------
    # SECOND METHOD:
    # If no specific cards found,
    # inspect direct children
    # ------------------------------------------------------

    if not candidate_elements:

        candidate_elements = (
            review_section.find_all(
                ["div", "li"],
                recursive=True
            )
        )

    # ------------------------------------------------------
    # PROCESS CANDIDATES
    # ------------------------------------------------------

    for element in candidate_elements:

        text = clean_text(
            element.get_text(
                " ",
                strip=True
            )
        )

        if not looks_like_review(text):
            continue

        # Remove duplicates
        key = text.lower()

        if key in seen:
            continue

        seen.add(key)

        # ----------------------------------------------
        # AUTHOR
        # ----------------------------------------------

        author = ""

        author_selectors = [
            "[class*='author']",
            "[class*='Author']",
            "[class*='user']",
            "[class*='User']",
            "[class*='name']",
            "[class*='Name']"
        ]

        for selector in author_selectors:

            author_element = (
                element.select_one(selector)
            )

            if author_element:

                author = clean_text(
                    author_element.get_text(
                        " ",
                        strip=True
                    )
                )

                if (
                    author
                    and len(author) < 100
                ):

                    break

        # ----------------------------------------------
        # DATE
        # ----------------------------------------------

        date = ""

        date_selectors = [
            "time",
            "[class*='date']",
            "[class*='Date']"
        ]

        for selector in date_selectors:

            date_element = (
                element.select_one(selector)
            )

            if date_element:

                date = clean_text(
                    date_element.get_text(
                        " ",
                        strip=True
                    )
                )

                if date:
                    break

        # ----------------------------------------------
        # RATING
        # ----------------------------------------------

        review_rating = ""

        rating_selectors = [
            "[class*='rating']",
            "[class*='Rating']",
            "[class*='star']",
            "[class*='Star']"
        ]

        for selector in rating_selectors:

            rating_element = (
                element.select_one(selector)
            )

            if rating_element:

                rating_text = clean_text(
                    rating_element.get_text(
                        " ",
                        strip=True
                    )
                )

                match = re.search(
                    r"\b([1-5](?:\.\d)?)\b",
                    rating_text
                )

                if match:

                    review_rating = (
                        match.group(1)
                    )

                    break

        reviews.append({

            "text": text,

            "author": author,

            "date": date,

            "rating": review_rating

        })

        # Maximum 100
        if len(reviews) >= 100:
            break

    return reviews


# ----------------------------------------------------------
# MAIN SCRAPER
# ----------------------------------------------------------

def scrape_moglix_product(url):

    driver = create_driver()

    try:

        # --------------------------------------------------
        # OPEN EXACT URL
        # --------------------------------------------------

        driver.get(url)

        # Wait for page
        WebDriverWait(
            driver,
            20
        ).until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        time.sleep(5)

        # --------------------------------------------------
        # SCROLL SLOWLY
        # --------------------------------------------------

        for position in range(
            0,
            7
        ):

            driver.execute_script(
                f"""
                window.scrollTo(
                    0,
                    document.body.scrollHeight *
                    {position / 6}
                );
                """
            )

            time.sleep(1.5)

        # --------------------------------------------------
        # PAGE SOURCE
        # --------------------------------------------------

        html = driver.page_source

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        # --------------------------------------------------
        # PRODUCT INFORMATION
        # --------------------------------------------------

        product_name = extract_product_name(
            soup
        )

        image = extract_product_image(
            soup
        )

        rating = extract_product_rating(
            soup
        )

        # --------------------------------------------------
        # EXACT REVIEW SECTION
        # --------------------------------------------------

        review_section = find_review_section(
            soup
        )

        if review_section is None:

            return {

                "success": False,

                "message":
                    "The exact Moglix product page was opened, "
                    "but its review section could not be found.",

                "reviews": []

            }

        # --------------------------------------------------
        # REVIEWS
        # --------------------------------------------------

        reviews = extract_reviews(
            review_section
        )

        # --------------------------------------------------
        # NO REVIEWS
        # --------------------------------------------------

        if not reviews:

            return {

                "success": False,

                "message":
                    "No accessible reviews were found "
                    "for this exact Moglix product.",

                "reviews": []

            }

        return {

            "success": True,

            "message":
                "Reviews collected from the exact product page.",

            "url": url,

            "product_name": product_name,

            "rating": rating,

            "image": image,

            "reviews": reviews

        }

    except Exception as e:

        return {

            "success": False,

            "message":
                f"Unable to read this Moglix product page: {str(e)}",

            "reviews": []

        }

    finally:

        driver.quit()