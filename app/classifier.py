"""Обёртка над HuggingFace-моделью. Ничего не знает про Telegram."""
import asyncio
import json
import logging
from pathlib import Path

import torch
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from app.config import settings

log = logging.getLogger(__name__)


class InferenceConfig(BaseModel):
    max_len: int = 128
    threshold: float = 0.5
    toxic_class_idx: int = 1


class ToxicClassifier:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        log.info("Устройство: %s", self.device)

        model_dir = Path(settings.model_dir)

        cfg_path = model_dir / "inference_config.json"
        self.cfg = (
            InferenceConfig(**json.loads(cfg_path.read_text()))
            if cfg_path.exists()
            else InferenceConfig()
        )

        log.info("Загружаем токенизатор из %s", model_dir)
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)

        log.info("Загружаем модель из %s", model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.model.to(self.device)
        self.model.eval()

        log.info("Модель готова: классов=%d", self.model.config.num_labels)

    @torch.inference_mode()
    def _predict_sync(self, text: str) -> float:
        """Синхронный инференс. Вызывается из потока через asyncio.to_thread."""
        enc = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.cfg.max_len,
            return_tensors="pt",
        )
        enc = {k: v.to(self.device) for k, v in enc.items()}
        logits = self.model(**enc).logits
        return torch.softmax(logits, dim=-1)[0, self.cfg.toxic_class_idx].item()

    async def predict(self, text: str) -> float:
        """Асинхронный инференс. Не блокирует event loop."""
        return await asyncio.to_thread(self._predict_sync, text)


classifier = ToxicClassifier()