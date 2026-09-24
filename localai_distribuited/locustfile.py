#!/usr/bin/python

import os
import time
from collections import Counter

import requests
from locust import FastHttpUser, TaskSet, between, events

MODEL = os.getenv("MODEL_NAME", "qwen_qwen3.5-0.8b")
CLUSTER_ID = os.getenv("CLUSTER_ID", "cluster-1")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "100"))
API_KEY = os.getenv("API_KEY", "")
# Rete di sicurezza: di norma il modello è già caldo perché il readiness
# probe del frontend lo carica prima del load-gen. ATTENZIONE: il tempo di
# warm-up viene sottratto a --run-time, quindi tienilo corto.
WARMUP_TIMEOUT = int(os.getenv("WARMUP_TIMEOUT", "120"))  # secondi

long_context = "Questo è un test di contesto. " * 10 + "/no_think"

HEADERS = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
node_counter = Counter()


def build_payload(max_tokens):
    return {
        "model": MODEL,
        "messages": [{"role": "user", "content": long_context}],
        "temperature": 0.7,
        "max_tokens": max_tokens,
    }


@events.test_start.add_listener
def warmup(environment, **kwargs):
    """Blocca finché il modello non risponde 200 (fuori dalle statistiche)."""
    url = f"{environment.host.rstrip('/')}/v1/chat/completions"
    deadline = time.time() + WARMUP_TIMEOUT
    print(f"[{CLUSTER_ID}] WARMUP start model={MODEL} url={url}", flush=True)
    while time.time() < deadline:
        try:
            r = requests.post(url, json=build_payload(1), headers=HEADERS, timeout=600)
            if r.status_code == 200:
                print(f"[{CLUSTER_ID}] WARMUP done node={r.headers.get('X-LocalAI-Node', '?')}", flush=True)
                return
            wait = int(r.headers.get("Retry-After", "10"))
            try:
                loading = r.json().get("loading", {})
                info = f"state={loading.get('state')} progress={loading.get('progress')} node={loading.get('node')}"
            except ValueError:
                info = r.text[:200]
            print(f"[{CLUSTER_ID}] WARMUP HTTP {r.status_code} {info} retry in {wait}s", flush=True)
        except requests.RequestException as e:
            wait = 10
            print(f"[{CLUSTER_ID}] WARMUP error {e} retry in {wait}s", flush=True)
        time.sleep(max(wait, 1))
    print(f"[{CLUSTER_ID}] WARMUP TIMEOUT after {WARMUP_TIMEOUT}s: il test parte comunque", flush=True)


@events.test_stop.add_listener
def report_nodes(**kwargs):
    print(f"[{CLUSTER_ID}] REQUESTS PER NODE: {dict(node_counter)}", flush=True)


def ask_llm(l):
    with l.client.post(
        "/v1/chat/completions",
        json=build_payload(MAX_TOKENS),
        headers=HEADERS,
        timeout=3600,
        name=f"/v1/chat/completions [{CLUSTER_ID}]",
        catch_response=True,
    ) as response:
        node_counter[response.headers.get("X-LocalAI-Node", "unknown")] += 1
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"HTTP {response.status_code}: {(response.text or '')[:200]}")


class UserBehavior(TaskSet):
    tasks = {ask_llm: 1}


class WebsiteUser(FastHttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 10)