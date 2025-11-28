# app/api/server.py

from flask import Flask, render_template, request, jsonify, send_file
from app.core.index_manager import IndexManager
from app.core.adaptive_ranker import AdaptiveRanker
import os

def create_app():
    # -------------------- Initialize Flask App --------------------
    app = Flask(
        __name__,
        template_folder=os.path.join(os.getcwd(), "templates"),
        static_folder=os.path.join(os.getcwd(), "static")
    )

    # -------------------- Initialize Index and AdaptiveRanker --------------------
    index = IndexManager(data_path=os.path.join("data", "documents"))
    ranker = AdaptiveRanker()

    # -------------------- HOME PAGE --------------------
    @app.route("/")
    def home():
        return render_template("search.html")

    # -------------------- SEARCH API --------------------
    @app.route("/api/search")
    def api_search():
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify([])

        # Get base search results from IndexManager
        results = index.search(query)  # [(doc_id, base_score)]
        boosted = ranker.apply_boosts(results, query)

        output = []
        for doc_id, boosted_score, base_score, total_boost in boosted:
            # Use snippet generator from IndexManager
            snippet = ""
            if hasattr(index, "get_snippet"):
                snippet = index.get_snippet(doc_id, query)
            output.append({
                "doc_id": doc_id,
                "base_score": round(base_score, 6),
                "boosted_score": round(boosted_score, 6),
                "total_boost": round(total_boost, 6),
                "snippet": snippet
            })
        return jsonify(output)

    # -------------------- AUTOCOMPLETE API --------------------
    @app.route("/api/autocomplete")
    def api_autocomplete():
        q = request.args.get("q", "").strip()
        if not q:
            return jsonify([])
        suggestions = index.autocomplete(q, limit=10)
        return jsonify(suggestions)

    # -------------------- CLICK LOGGING --------------------
    @app.route("/api/click", methods=["POST"])
    def click():
        data = request.get_json(force=True)  # safer than request.json
        query = data.get("query", "").strip()
        doc_id = data.get("doc_id", "").strip()

        if query and doc_id:
            ranker.record_click(query, doc_id)
            return jsonify({"status": "ok"})
        return jsonify({"status": "failed", "reason": "missing query or doc_id"}), 400

    # -------------------- DOCUMENT VIEWER --------------------
    @app.route("/doc/<path:doc_id>")
    def view_doc(doc_id):
        file_path = os.path.join("data", "documents", doc_id)
        if not os.path.exists(file_path):
            return "Document not found", 404
        return send_file(file_path)

    return app


# -------------------- RUN SERVER --------------------
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
