#!/usr/bin/python
import os
import random
from locust import FastHttpUser, TaskSet, between

MODEL = os.getenv("MODEL_NAME", "qwen_qwen3.5-0.8b")
CLUSTER_ID = os.getenv("CLUSTER_ID", "cluster-1")

long_context = "Questo è un test di contesto. " * 10 + "/no_think"


def ask_llm(l):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": long_context}],
        "temperature": 0.7,
        "max_tokens": 600,
    }
    l.client.post(
        "/v1/chat/completions",
        json=payload,
        timeout=3600,
        name=f"/v1/chat/completions [{CLUSTER_ID}]",
    )


class UserBehavior(TaskSet):
    tasks = {ask_llm: 1}


class WebsiteUser(FastHttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 10)