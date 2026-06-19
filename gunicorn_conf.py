"""Конфигурация Gunicorn для production-запуска (INFRA-10).

Запуск:
    gunicorn app.main:app -c gunicorn_conf.py

Несколько uvicorn-воркеров под менеджером процессов: падение одного воркера
не роняет сервис (в отличие от `uvicorn --reload` с единственным процессом).
"""
import multiprocessing
import os

bind = os.getenv("BIND", "0.0.0.0:8000")
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 60
graceful_timeout = 30
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
