let allReviews = [];


// ======================================================
// ANALYZE PRODUCT
// ======================================================

async function analyzeProduct() {

    const input =
        document.getElementById(
            "productUrl"
        );

    const button =
        document.getElementById(
            "analyzeBtn"
        );

    const loading =
        document.getElementById(
            "loading"
        );

    const error =
        document.getElementById(
            "error"
        );

    const result =
        document.getElementById(
            "resultSection"
        );


    const url =
        input.value.trim();


    // Clear old results

    result.classList.add(
        "hidden"
    );

    error.innerText = "";


    // --------------------------------------------------
    // EMPTY
    // --------------------------------------------------

    if (!url) {

        error.innerText =
            "Please paste a Moglix product URL.";

        return;
    }


    // --------------------------------------------------
    // URL CHECK
    // --------------------------------------------------

    if (
        !url.toLowerCase()
            .includes("moglix.com")
    ) {

        error.innerText =
            "Invalid URL. Please paste a Moglix product link.";

        return;
    }


    // --------------------------------------------------
    // START LOADING
    // --------------------------------------------------

    loading.style.display =
        "block";

    button.disabled = true;

    button.innerText =
        "Analyzing...";


    try {

        const response =
            await fetch(
                "/analyze",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        url: url
                    })

                }
            );


        const data =
            await response.json();


        if (!data.success) {

            throw new Error(
                data.message
            );

        }


        displayResult(data);


    }

    catch (errorObject) {

        error.innerText =
            errorObject.message ||
            "Unable to analyze this product.";

    }


    finally {

        loading.style.display =
            "none";

        button.disabled =
            false;

        button.innerText =
            "Analyze Reviews";

    }

}


// ======================================================
// DISPLAY RESULT
// ======================================================

function displayResult(data) {

    const product =
        data.product;

    const summary =
        data.summary;


    // --------------------------------------------------
    // PRODUCT
    // --------------------------------------------------

    document.getElementById(
        "productName"
    ).innerText =
        product.name;


    document.getElementById(
        "productRating"
    ).innerText =
        product.rating;


    const image =
        document.getElementById(
            "productImage"
        );


    if (product.image) {

        image.src =
            product.image;

        image.style.display =
            "block";

    }

    else {

        image.style.display =
            "none";

    }


    // --------------------------------------------------
    // SUMMARY
    // --------------------------------------------------

    document.getElementById(
        "totalReviews"
    ).innerText =
        summary.total;


    document.getElementById(
        "positiveReviews"
    ).innerText =
        summary.positive;


    document.getElementById(
        "negativeReviews"
    ).innerText =
        summary.negative;


    document.getElementById(
        "neutralReviews"
    ).innerText =
        summary.neutral;


    document.getElementById(
        "positivePercent"
    ).innerText =
        summary.positive_percent +
        "%";


    document.getElementById(
        "negativePercent"
    ).innerText =
        summary.negative_percent +
        "%";


    document.getElementById(
        "neutralPercent"
    ).innerText =
        summary.neutral_percent +
        "%";


    // --------------------------------------------------
    // BAR
    // --------------------------------------------------

    document.getElementById(
        "positiveBar"
    ).style.width =
        summary.positive_percent +
        "%";


    document.getElementById(
        "neutralBar"
    ).style.width =
        summary.neutral_percent +
        "%";


    document.getElementById(
        "negativeBar"
    ).style.width =
        summary.negative_percent +
        "%";


    // --------------------------------------------------
    // REVIEWS
    // --------------------------------------------------

    allReviews =
        data.reviews;


    renderReviews(
        allReviews
    );


    // --------------------------------------------------
    // SHOW
    // --------------------------------------------------

    const result =
        document.getElementById(
            "resultSection"
        );


    result.classList.remove(
        "hidden"
    );


    window.scrollTo({

        top:
            result.offsetTop - 30,

        behavior:
            "smooth"

    });

}


// ======================================================
// RENDER REVIEWS
// ======================================================

function renderReviews(
    reviews
) {

    const container =
        document.getElementById(
            "reviewsContainer"
        );


    container.innerHTML = "";


    if (
        !reviews ||
        reviews.length === 0
    ) {

        container.innerHTML = `
            <p>
                No reviews found for this
                product.
            </p>
        `;

        return;
    }


    reviews.forEach(
        (review, index) => {

            let sentimentClass =
                "sentiment-neutral";

            let icon =
                "😐";


            if (
                review.sentiment ===
                "Positive"
            ) {

                sentimentClass =
                    "sentiment-positive";

                icon =
                    "😊";

            }


            else if (
                review.sentiment ===
                "Negative"
            ) {

                sentimentClass =
                    "sentiment-negative";

                icon =
                    "😞";

            }


            const div =
                document.createElement(
                    "div"
                );


            div.className =
                "review";


            const author =
                review.author
                ? escapeHtml(
                    review.author
                  )
                : "Verified Customer";


            const date =
                review.date
                ? escapeHtml(
                    review.date
                  )
                : "";


            const rating =
                review.rating
                ? `⭐ ${escapeHtml(
                    review.rating
                  )}`
                : "";


            div.innerHTML = `

                <div class="review-top">

                    <div>

                        <strong>
                            Review ${index + 1}
                        </strong>

                        <div class="review-author">

                            ${author}

                            ${date
                                ? " • " + date
                                : ""
                            }

                            ${rating
                                ? " • " + rating
                                : ""
                            }

                        </div>

                    </div>


                    <span
                        class="sentiment ${sentimentClass}"
                    >

                        ${icon}

                        ${escapeHtml(
                            review.sentiment
                        )}

                    </span>

                </div>


                <p class="review-text">

                    ${escapeHtml(
                        review.text
                    )}

                </p>

            `;


            container.appendChild(
                div
            );

        }
    );

}


// ======================================================
// FILTER
// ======================================================

function filterReviews() {

    const value =
        document.getElementById(
            "filter"
        ).value;


    if (value === "all") {

        renderReviews(
            allReviews
        );

        return;
    }


    const filtered =
        allReviews.filter(
            review =>
                review.sentiment ===
                value
        );


    renderReviews(
        filtered
    );

}


// ======================================================
// HTML ESCAPE
// ======================================================

function escapeHtml(text) {

    const div =
        document.createElement(
            "div"
        );

    div.innerText =
        text || "";

    return div.innerHTML;

}


// ======================================================
// ENTER KEY
// ======================================================

document
    .getElementById(
        "productUrl"
    )
    .addEventListener(
        "keydown",
        function(event) {

            if (
                event.key ===
                "Enter"
            ) {

                analyzeProduct();

            }

        }
    );