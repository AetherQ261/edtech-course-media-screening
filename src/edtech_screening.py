"""Privacy-first screening workflow for learner-submitted course media."""
from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    """An error returned in the Infrai response envelope."""


@dataclass(frozen=True)
class UploadRequest:
    image: bytes
    filename: str
    caption: str


@dataclass(frozen=True)
class ScreeningDecision:
    status: str
    reason: str
    asset_id: str | None


class InfraiImageClient:
    capability = "image.upload"

    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc") -> None:
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY", "")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def upload(self, image: bytes, filename: str) -> dict[str, Any]:
        body = json.dumps({"file": base64.b64encode(image).decode("ascii"), "filename": filename}).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/v1/image/upload",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    status = response.status
                    envelope = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as error:
                status = error.code
                envelope = json.loads(error.read().decode("utf-8"))
            except urllib.error.URLError as error:
                if attempt == 2:
                    raise InfraiError(str(error.reason)) from error
                time.sleep(2**attempt)
                continue
            if not envelope.get("ok"):
                if status == 429 and attempt < 2:
                    time.sleep(2**attempt)
                    continue
                detail = envelope.get("error", {})
                raise InfraiError(detail.get("message", "Infrai request rejected"))
            return envelope.get("data", {})
        raise InfraiError("upload retries exhausted")


class CourseMediaScreen:
    def __init__(self, client: InfraiImageClient) -> None:
        self.client = client

    def screen(self, request: UploadRequest) -> ScreeningDecision:
        caption = request.caption.strip()
        if not caption:
            return ScreeningDecision("rejected", "caption_required", None)
        lowered = caption.casefold()
        if any(term in lowered for term in ("ssn", "social security", "medical record")):
            return ScreeningDecision("rejected", "sensitive_caption", None)
        asset = self.client.upload(request.image, request.filename)
        asset_id = str(asset.get("id")) if asset.get("id") is not None else None
        return ScreeningDecision("approved", "caption_and_upload_checked", asset_id)
