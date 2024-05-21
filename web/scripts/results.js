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

    let resulting_urls = document.getElementById("results");
    for (let i=0; i < urls.length; ++i) {
        let url_to_append = document.createElement("li");
        url_to_append.appendChild(document.createTextNode(urls[i]));
        url_to_append.setAttribute("id", "appended-url");
        resulting_urls.appendChild(url_to_append);
    }
    
}


let query = getParameterByName("query");
console.log(query);
search(query);