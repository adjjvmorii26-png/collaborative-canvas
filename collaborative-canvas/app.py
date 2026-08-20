#!/usr/bin/env python3
"""Collaborative Canvas - AI and Human Co-creation Platform"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)
STORIES_FILE = "data/stories.json"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
if not os.path.exists(STORIES_FILE):
    with open(STORIES_FILE, "w") as f:
        json.dump({}, f)

def load_stories():
    with open(STORIES_FILE, "r") as f:
        return json.load(f)

def save_stories(stories):
    with open(STORIES_FILE, "w") as f:
        json.dump(stories, f, indent=2)

# In-memory story state (for demo; persistent in stories.json)
story_turns = {}  # story_id -> {"turn": 0, "current_actor": "human"}

@app.route("/")
def index():
    stories = load_stories()
    return render_template("index.html", stories=stories)

@app.route("/api/stories", methods=["GET"])
def list_stories():
    stories = load_stories()
    return jsonify({"stories": stories})

@app.route("/api/stories", methods=["POST"])
def create_story():
    data = request.get_json()
    title = data.get("title", "Untitled Story")
    story_id = data.get("id", datetime.now().strftime("%Y%m%d%H%M%S"))
    
    stories = load_stories()
    stories[story_id] = {
        "id": story_id,
        "title": title,
        "turn": 0,
        "actors": [],  # list of "human" or "ai"
        "content": [],
        "created": datetime.now().isoformat(),
    }
    save_stories(stories)
    
    story_turns[story_id] = {"turn": 0, "current_actor": "human"}
    
    return jsonify({"id": story_id, "title": title, "status": "created"}), 201

@app.route("/api/stories/<story_id>", methods=["GET"])
def get_story(story_id):
    stories = load_stories()
    if story_id not in stories:
        return jsonify({"error": "Story not found"}), 404
    
    story = stories[story_id]
    return jsonify({
        "id": story["id"],
        "title": story["title"],
        "turn": story["turn"],
        "actors": story["actors"],
        "content": story["content"],
    })

@app.route("/api/stories/<story_id>/contribute", methods=["POST"])
def contribute(story_id):
    data = request.get_json()
    message = data.get("message", "")
    
    stories = load_stories()
    if story_id not in stories:
        return jsonify({"error": "Story not found"}), 404
    
    story = stories[story_id]
    story["content"].append({"actor": "human", "message": message})
    story["turn"] += 1
    story["actors"].append("human")
    
    # After human contribution, it's AI's turn
    story_turns[story_id]["turn"] += 1
    story_turns[story_id]["current_actor"] = "ai"
    
    save_stories(stories)
    
    return jsonify({
        "status": "human_contributed",
        "turn": story["turn"],
        "actor": "human",
        "message": message,
    })

@app.route("/api/stories/<story_id>/ai-continue", methods=["POST"])
def ai_continue(story_id):
    stories = load_stories()
    if story_id not in stories:
        return jsonify({"error": "Story not found"}), 404
    
    story = stories[story_id]
    
    # AI generates continuation based on last contribution
    last_content = story["content"][-1]["message"] if story["content"] else ""
    
    # Simple AI continuation - in a real system, this would use an LLM
    continuation = f"AI response to: {last_content[:50] if last_content else 'nothing'}..."
    
    story["content"].append({"actor": "ai", "message": continuation})
    story["turn"] += 1
    story["actors"].append("ai")
    
    # Switch back to human turn
    story_turns[story_id]["turn"] += 1
    story_turns[story_id]["current_actor"] = "human"
    
    save_stories(stories)
    
    return jsonify({
        "status": "ai_continued",
        "turn": story["turn"],
        "actor": "ai",
        "continuation": continuation,
    })

@app.route("/api/stories/<story_id>/reset", methods=["POST"])
def reset_story(story_id):
    stories = load_stories()
    if story_id not in stories:
        return jsonify({"error": "Story not found"}), 404
    
    stories[story_id] = {
        "id": story_id,
        "title": "New Story",
        "turn": 0,
        "actors": [],
        "content": [],
        "created": datetime.now().isoformat(),
    }
    save_stories(stories)
    story_turns[story_id] = {"turn": 0, "current_actor": "human"}
    
    return jsonify({"status": "reset", "story_id": story_id})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "Collaborative Canvas running"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
