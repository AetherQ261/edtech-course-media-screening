from src.edtech_screening import CourseMediaScreen, ScreeningDecision, UploadRequest


class StubClient:
    def upload(self, image: bytes, filename: str) -> dict[str, str]:
        return {"id": "asset-42"}


def test_sensitive_caption_is_rejected_before_upload() -> None:
    decision = CourseMediaScreen(StubClient()).screen(
        UploadRequest(b"pixels", "lesson.jpg", "Learner medical record review")
    )
    assert decision == ScreeningDecision("rejected", "sensitive_caption", None)


def test_clear_caption_is_approved_and_upload_id_is_returned() -> None:
    decision = CourseMediaScreen(StubClient()).screen(
        UploadRequest(b"pixels", "lesson.jpg", "Photosynthesis lab notes")
    )
    assert decision == ScreeningDecision("approved", "caption_and_upload_checked", "asset-42")
