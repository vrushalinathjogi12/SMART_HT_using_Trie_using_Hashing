from flask import Blueprint, request, jsonify
from app.core.persistence import load_engine
from app.core.smart_ht_engine import SmartHTEngine
import traceback

search_bp = Blueprint("search_bp", __name__)

# lazy loader helper
def get_engine():
    engine = load_engine()
    if engine is None:
        # build a fresh engine and index documents from 'documents/' if present
        engine = SmartHTEngine()
        try:
            from pathlib import Path
            docs_path = Path("documents")
            if docs_path.exists():
                for p in docs_path.glob("*.txt"):
                    doc_id = p.name
                    with p.open("r", encoding="utf-8") as f:
                        engine.index_document(doc_id, f.read())
            # persist components
            from app.core.persistence import save_engine
            save_engine(engine)
        except Exception:
            traceback.print_exc()
    return engine

@search_bp.route("/autocomplete")
def autocomplete():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"suggestions": []})
    engine = get_engine()
    try:
        suggestions = engine.autocomplete(q, limit=10)
    except Exception:
        suggestions = []
    return jsonify({"suggestions": suggestions})

@search_bp.route("/search")
def search_api():
    q = request.args.get("q", "").strip()
    top_k = int(request.args.get("k", 10))
    if not q:
        return jsonify({"results": []})
    engine = get_engine()
    try:
        results = engine.search(q, top_k=top_k)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@search_bp.route("/click", methods=["POST"])
def click():
    data = request.get_json() or {}
    q = data.get("query", "")
    doc_id = data.get("doc_id", "")
    engine = get_engine()
    if q and doc_id:
        try:
            engine.record_click(q, doc_id)
            # save click logs already performed by AdaptiveRanker
            return jsonify({"status":"ok"})
        except Exception as e:
            return jsonify({"status":"error","error":str(e)}), 500
    return jsonify({"status":"error","error":"missing query/doc_id"}), 400
