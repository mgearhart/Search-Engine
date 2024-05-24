// from https://stackoverflow.com/questions/901115/how-can-i-get-query-string-values-in-javascript
function getParameterByName(name, url = window.location.href) {
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

async function search(query) {
    let search_url = "http://localhost:8000/api/search?query=" + query;
    const response = await fetch(search_url);
    const urls = await response.json();
    console.log(urls);
    return urls;
}

let query = getParameterByName("query");
console.log(query);

(async () => {
    let urls = await search(query);
    let resulting_urls = document.getElementById("results");

    // Pagination variables
    let currentPage = 1;
    let urlsPerPage = 25;

    function displayResults() {
        // Clear previous results
        resulting_urls.innerHTML = '';

        // Calculate pagination range
        let startIndex = (currentPage - 1) * urlsPerPage;
        let endIndex = Math.min(startIndex + urlsPerPage, urls.length);

        // Display URLs for the current page
        for (let i = startIndex; i < endIndex; ++i) {
            let url_to_append = document.createElement("li");
            let link = document.createElement("a");
            link.href = urls[i];
            link.appendChild(document.createTextNode(urls[i]));
            url_to_append.appendChild(link);
            url_to_append.setAttribute("class", "appended-url"); // Use class instead of id
            resulting_urls.appendChild(url_to_append);
        }

        // Update result statistics
        let resultStats = document.getElementById("result-stats");
        resultStats.textContent = `Showing results ${startIndex + 1} - ${endIndex} of ${urls.length}`;

        // Update pagination buttons
        let paginationButtons = document.getElementById("pagination-buttons");
        paginationButtons.innerHTML = '';

        // Previous button
        let prevButton = document.createElement("button");
        prevButton.textContent = "← Previous";
        prevButton.disabled = currentPage === 1;
        prevButton.addEventListener("click", function() {
            if (currentPage > 1) {
                currentPage--;
                displayResults();
            }
        });
        paginationButtons.appendChild(prevButton);

        // Current page number
        let currentPageNumber = document.createElement("span");
        currentPageNumber.textContent = currentPage;
        paginationButtons.appendChild(currentPageNumber);

        // Next button
        let nextButton = document.createElement("button");
        nextButton.textContent = "Next →";
        nextButton.disabled = endIndex === urls.length;
        nextButton.addEventListener("click", function() {
            if (endIndex < urls.length) {
                currentPage++;
                displayResults();
            }
        });
        paginationButtons.appendChild(nextButton);
    }

    displayResults();
})();
