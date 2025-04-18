import logging

# Убираем шум
for noisy_logger in ["httpx", "httpcore", "urllib3"]:
    logging.getLogger(noisy_logger).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Если логгер ещё не настроен — добавляем хендлер
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Чтобы логи не дублировались
logger.propagate = False
