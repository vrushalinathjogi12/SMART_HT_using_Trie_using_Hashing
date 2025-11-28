$(document).ready(function() {
    const $searchBox = $("#search-box");
    const $autocomplete = $("#autocomplete-list");
    const $results = $("#results");

    // Autocomplete AJAX
    $searchBox.on("input", function() {
        const query = $(this).val().trim();
        if (!query) {
            $autocomplete.empty();
            return;
        }

        $.get("/api/autocomplete", {q: query}, function(data) {
            $autocomplete.empty();
            data.forEach(function(item) {
                $autocomplete.append(`<li>${item}</li>`);
            });
        });
    });

    // Click suggestion
    $autocomplete.on("click", "li", function() {
        $searchBox.val($(this).text());
        $autocomplete.empty();
        performSearch($(this).text());
    });

    // Enter key triggers search
    $searchBox.on("keypress", function(e) {
        if (e.which === 13) {
            performSearch($(this).val());
            $autocomplete.empty();
        }
    });

    // Perform search
    function performSearch(query) {
        if (!query) return;
        $.get("/api/search", {q: query}, function(data) {
            $results.empty();
            if (!data.length) {
                $results.append("<p>No results found.</p>");
                return;
            }
            data.forEach(function(item) {
                const snippet = highlightQuery(item.snippet, query);
                const html = `
                    <div class="result-item">
                        <h3>${item.doc_id} (Score: ${item.boosted_score.toFixed(2)})</h3>
                        <p class="result-snippet">${snippet}</p>
                    </div>`;
                $results.append(html);

                // Send click to adaptive ranker
                $(`.result-item h3:contains(${item.doc_id})`).click(function() {
                    $.post("/api/click", JSON.stringify({query: query, doc_id: item.doc_id}),
                        function(){}, "json");
                });
            });
        });
    }

    // Highlight keywords
    function highlightQuery(text, query) {
        const tokens = query.split(/\s+/);
        tokens.forEach(function(token) {
            const re = new RegExp(`(${token})`, "gi");
            text = text.replace(re, '<span class="highlight">$1</span>');
        });
        return text;
    }
});
