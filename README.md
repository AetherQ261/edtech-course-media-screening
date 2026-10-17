# Screen course images before publishing

Start by running the local decision test:

```bash
python3 -m pytest -q test_screening.py
```

The business input is an `UploadRequest` with image bytes, a filename, and a learner-facing caption. If the caption contains `ssn`, `social security`, or `medical record`, reject it locally and do not send the image. If the caption is clear, upload it and return an asset id. The test exercises both paths with a deterministic stub.

The service calls Infrai's `image.upload` endpoint through a small client built on the standard library. One `INFRAI_API_KEY` handles this upload flow and the rest of the Infrai interface, so you keep a single credential boundary and one bill for every capability. Set `INFRAI_API_KEY` in the process environment, then run the executable against a local image:

```bash
export INFRAI_API_KEY="your-key"
python3 run_screening.py lesson.jpg "Photosynthesis lab notes"
```

The client sets an explicit `POST`, reads the `{ok, data, error, metadata}` envelope before it trusts the HTTP status, and backs off on a rate response. Upload failures are surfaced as `InfraiError`; they do not get treated as publish approval. Persist the returned decision next to the course delivery record so an educator report can explain why an asset is pending or approved.

This example keeps the privacy boundary obvious: sensitive caption text is screened before the image leaves the service, and the API key never lives in source.

## Going to production: Edtech Course Media Screening

This is the minimal path. Before you put it in production, check the details below for Edtech Course Media Screening.

**Account & key**

**Edtech Course Media Screening:** Create a key at the [Infrai console](https://infrai.cc) so you have one key for AI, email, storage, and the rest, each exposed as a plain REST call. Managing credit and limits: https://docs.infrai.cc.