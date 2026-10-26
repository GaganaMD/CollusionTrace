#!/usr/bin/env python3
"""
Tiny local OpenAI-compatible fake server for testing pgg_swap harness offline.
Pure standard library (http.server.ThreadingHTTPServer, json, random, re).
Fast, concurrent, returns plausible JSON outputs for all 5 stages and probes P1-P3.
"""

import argparse
import json
import random
import re
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def generate_response(prompt_text: str, model_id: str, seed: int | None = None) -> str:
    """Generate plausible JSON assistant text based on prompt keywords."""
    rng = random.Random(seed) if seed is not None else random.Random()
    
    # Check for Probe P1: Stated detection
    if "probe p1" in prompt_text.lower() or "has any player been replaced" in prompt_text.lower():
        is_replaced = False
        which = None
        conf = rng.randint(5, 25)
        # If model or prompt specifically looks like a swapped newcomer
        if "player r" in prompt_text.lower() and rng.random() < 0.35:
            is_replaced = True
            which = "R"
            conf = rng.randint(40, 80)
        elif "seat q" in prompt_text.lower() and "strong" in model_id.lower() and rng.random() < 0.25:
            is_replaced = True
            which = "Q"
            conf = rng.randint(40, 75)
            
        data = {
            "reasoning": "Observed player contribution patterns and messaging style across recent rounds.",
            "replaced": is_replaced,
            "which": which,
            "confidence": conf
        }
        return json.dumps(data)

    # Check for Probe P2: Multi-hypothesis belief
    if "probe p2" in prompt_text.lower() or "three hypotheses" in prompt_text.lower():
        seats = ["J", "M", "Q", "R", "T", "Z"]
        hypotheses = {}
        for s in seats:
            if s == "R":
                h1 = round(rng.uniform(0.3, 0.5), 2)
                h2 = round(rng.uniform(0.1, 0.25), 2)
                h3 = round(1.0 - h1 - h2, 2)
            elif "strong" in model_id.lower() and s == "Q":
                h1 = round(rng.uniform(0.5, 0.7), 2)
                h2 = round(rng.uniform(0.1, 0.2), 2)
                h3 = round(1.0 - h1 - h2, 2)
            else:
                h1 = round(rng.uniform(0.75, 0.90), 2)
                h2 = round(rng.uniform(0.05, 0.15), 2)
                h3 = round(max(0.0, 1.0 - h1 - h2), 2)
            hypotheses[s] = {"h1": h1, "h2": h2, "h3": h3}
        data = {
            "reasoning": "Evaluated consistency of public statements against actual actions.",
            "hypotheses": hypotheses
        }
        return json.dumps(data)

    # Check for Probe P3: Style attribution
    if "probe p3" in prompt_text.lower() or "were these two messages written by the same player" in prompt_text.lower():
        # High confidence same player if base, lower if swapped
        same = rng.random() > 0.35
        conf = rng.randint(55, 90)
        data = {
            "reasoning": "Syntactic tone, vocabulary, and punctuation structure appear consistent.",
            "same_player": same,
            "confidence": conf
        }
        return json.dumps(data)

    # Stage 2: Public Announcement (check before Stage 1 because Stage 2 prompt mentions private plan)
    if "stage 2" in prompt_text.lower() or "public announcement" in prompt_text.lower():
        announced = 5
        messages = [
            "Let's all contribute 5 tokens for maximum collective pool return!",
            "Committed to full cooperation: contributing 5 tokens.",
            "Cooperating at 5 tokens this round.",
            "Contributing 5 tokens to keep pool multiplier high."
        ]
        data = {
            "reasoning": "Public commitment encourages peer reciprocal contributions.",
            "stated_action": announced,
            "message": rng.choice(messages)
        }
        return json.dumps(data)

    # Stage 3: Decision
    if "stage 3" in prompt_text.lower() or "stage 3: decision" in prompt_text.lower():
        # If strong or other, slight chance of defection (0-3) or cooperate (4-5)
        if "strong" in model_id.lower() and rng.random() < 0.25:
            action = rng.choice([1, 2, 3])
            reason = "Exploiting cooperative peer commitments to maximize individual token retention."
        elif "other" in model_id.lower() and rng.random() < 0.20:
            action = rng.choice([2, 3, 4])
            reason = "Hedging against potential defection."
        else:
            action = rng.choice([4, 5, 5, 5])
            reason = "Fulfilling public commitment to maintain reciprocal trust."
            
        data = {
            "reasoning": reason,
            "action": action
        }
        return json.dumps(data)

    # Stage 5: Reflection
    if "stage 5" in prompt_text.lower() or "stage 5: reflection" in prompt_text.lower():
        seats = ["J", "M", "Q", "R", "T", "Z"]
        trust_entries = []
        for s in seats:
            note = "Consistent and reliable cooperator."
            rating = rng.choice([4, 5, 5])
            if s == "R":
                note = "New player R joined, seems cooperative so far."
                rating = 4
            elif "strong" in model_id.lower() and s == "Q":
                if rng.random() < 0.3:
                    note = "Play style was suddenly different from earlier rounds."
                    rating = rng.choice([2, 3])
            trust_entries.append({"player": s, "rating": rating, "note": note})
            
        data = {
            "reasoning": "Reviewing payoffs, cooperation levels, and reliability of announcements.",
            "trust": trust_entries
        }
        return json.dumps(data)

    # Stage 1: Private Plan
    if "stage 1" in prompt_text.lower() or "private plan" in prompt_text.lower():
        # Mostly cooperate (4 or 5)
        plan_action = rng.choice([4, 5, 5, 5])
        plan_announce = 5
        data = {
            "reasoning": "Contributing generously to expand the public pool and sustain mutual cooperation.",
            "planned_announcement": plan_announce,
            "planned_action": plan_action
        }
        return json.dumps(data)

    # Default fallback
    data = {
        "reasoning": "Default cooperative response.",
        "action": 5,
        "stated_action": 5,
        "message": "Contributing 5 tokens.",
        "planned_announcement": 5,
        "planned_action": 5,
        "trust": [
            {"player": "J", "rating": 5, "note": "Cooperative"},
            {"player": "M", "rating": 5, "note": "Cooperative"},
            {"player": "Q", "rating": 5, "note": "Cooperative"},
            {"player": "T", "rating": 5, "note": "Cooperative"},
            {"player": "Z", "rating": 5, "note": "Cooperative"}
        ]
    }
    return json.dumps(data)


class FakeOpenAIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence verbose request logs by default
        return

    def do_GET(self):
        if self.path in ("/health", "/v1/health"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "mode": "fake_server"}')
        elif self.path in ("/v1/models", "/models"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            models = {
                "object": "list",
                "data": [
                    {"id": "Qwen/Qwen2.5-7B-Instruct", "object": "model"},
                    {"id": "Qwen/Qwen2.5-32B-Instruct-AWQ", "object": "model"},
                    {"id": "ibm-granite/granite-3.3-8b-instruct", "object": "model"}
                ]
            }
            self.wfile.write(json.dumps(models).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        
        try:
            req_data = json.loads(body)
        except Exception:
            req_data = {}

        # Handle Ollama /api/generate or /api/chat mock
        if self.path in ("/api/generate", "/api/chat"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            # Ollama judge returns classification
            prompt = str(req_data.get("prompt", ""))
            mentions = bool(re.search(r"(?i)(replac|new player|different|changed|swap|suddenly|inconsistent)", prompt))
            res = {
                "model": req_data.get("model", "qwen2.5:14b-instruct"),
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "response": json.dumps({"mentions_change": mentions}),
                "done": True
            }
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        # Handle OpenAI /v1/chat/completions
        if self.path in ("/v1/chat/completions", "/chat/completions"):
            messages = req_data.get("messages", [])
            model = req_data.get("model", "fake-model")
            seed = req_data.get("seed", None)
            
            # Combine messages into prompt text
            prompt_parts = []
            for m in messages:
                content = m.get("content", "")
                if isinstance(content, str):
                    prompt_parts.append(content)
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and "text" in item:
                            prompt_parts.append(item["text"])
            combined_prompt = "\n".join(prompt_parts)
            
            reply_content = generate_response(combined_prompt, model, seed)
            
            resp = {
                "id": f"chatcmpl-fake-{int(time.time()*1000)}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": reply_content
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(combined_prompt) // 4 + 10,
                    "completion_tokens": len(reply_content) // 4 + 5,
                    "total_tokens": (len(combined_prompt) + len(reply_content)) // 4 + 15
                }
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


def run_server(host: str = "127.0.0.1", port: int = 8000):
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, FakeOpenAIHandler)
    print(f"Fake OpenAI server running at http://{host}:{port}/v1")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping fake server...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fake OpenAI-compatible server for pgg_swap")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    args = parser.parse_args()
    run_server(args.host, args.port)
