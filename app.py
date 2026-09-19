from flask import Flask, render_template, request, jsonify
from scraper import scrape_moglix_product
from sentiment import analyze_sentiment

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        data = request.get_json()

        if not data or not data.get("url"):
            return jsonify({
                "success": False,
                "message": "Please enter a Moglix product URL."
            })

        url = data["url"].strip()

        # --------------------------------------------------
        # URL VALIDATION
        # --------------------------------------------------

        if "moglix.com" not in url.lower():

            return jsonify({
                "success": False,
                "message": "Only Moglix product links are supported."
            })

        # --------------------------------------------------
        # SCRAPE EXACT PRODUCT
        # --------------------------------------------------

        product = scrape_moglix_product(url)

        if not product["success"]:

            return jsonify({
                "success": False,
                "message": product["message"]
            })

        reviews = product["reviews"]

        # --------------------------------------------------
        # SENTIMENT ANALYSIS
        # --------------------------------------------------

        analyzed_reviews = []

        positive = 0
        negative = 0
        neutral = 0

        for review in reviews:

            text = review["text"].strip()

            if not text:
                continue

            result = analyze_sentiment(text)

            review_data = {
                "text": text,
                "rating": review.get("rating", ""),
                "author": review.get("author", ""),
                "date": review.get("date", ""),
                "sentiment": result["label"],
                "score": result["score"]
            }

            analyzed_reviews.append(review_data)

            if result["label"] == "Positive":
                positive += 1

            elif result["label"] == "Negative":
                negative += 1

            else:
                neutral += 1

        total = len(analyzed_reviews)

        if total == 0:

            return jsonify({
                "success": False,
                "message":
                    "This exact Moglix product page does not contain accessible reviews."
            })

        positive_percent = round(
            positive / total * 100, 1
        )

        negative_percent = round(
            negative / total * 100, 1
        )

        neutral_percent = round(
            neutral / total * 100, 1
        )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return jsonify({

            "success": True,

            "product": {
                "name": product["product_name"],
                "rating": product["rating"],
                "image": product["image"],
                "url": product["url"]
            },

            "summary": {

                "total": total,

                "positive": positive,

                "negative": negative,

                "neutral": neutral,

                "positive_percent": positive_percent,

                "negative_percent": negative_percent,

                "neutral_percent": neutral_percent
            },

            "reviews": analyzed_reviews

        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        })


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )