from flask import Blueprint, request, jsonify
from app.core.persistence import save_engine, load_engine
from app.core.smart_ht_engine import SmartHTEngine
from app.core.indexer import Indexer, DOCS_DIR
import traceback

index_bp = Blueprint("index_bp", __name__)

@index_bp.route("/rebuild", methods=["POST"])
def rebuild():
    """
    Rebuild index from documents folder
    optional ?force=true
    """
    force = request.args.get("force", "false").lower() in ("1","true","yes")
    existing = load_engine()
    if existing and not force:
        return jsonify({"status":"ok","message":"Engine exists. Use force to rebuild."})

    try:
        idx = Indexer()
        count = idx.rebuild_index(dirpath=DOCS_DIR, pattern="*.txt", save=True)
        # create engine rehydrated from indexer
        engine = SmartHTEngine()
        engine.trie = idx.trie
        engine.hash_store = idx.hash_store
        engine.index = idx.index
        engine.ranker = engine.ranker.__class__(engine.index)
        engine.adaptive = idx.adaptive
        save_engine(engine)
        return jsonify({"status":"ok","message":f"Rebuilt {count} docs."})
    except Exception:
        traceback.print_exc()
        return jsonify({"status":"error","message":"rebuild failed"}), 500

@index_bp.route("/status")
def status():
    engine = load_engine()
    if engine is None:
        return jsonify({"status":"empty"})
    # simple info
    try:
        total_docs = len(engine.hash_store.store) if hasattr(engine.hash_store, "store") else "unknown"
    except Exception:
        total_docs = "unknown"
    return jsonify({"status":"ok","documents_indexed": total_docs})
