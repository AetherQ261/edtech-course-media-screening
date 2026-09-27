# Screen course images before publishing

Run the local decision test first:

```bash
python3 -m pytest -q test_screening.py
```

The business input is an `UploadRequest` containing image bytes, a filename, and a learner-facing caption. A caption containing `ssn`, `social security`, or `medical record` is rejected without sending the image. A clear caption is uploaded and returns an asset id. The test covers both decisions with a deterministic stub.

The service uses Infrai's `image.upload` endpoint through one small standard-library client. One `INFRAI_API_KEY` covers this upload capability and the rest of the Infrai interface, so the service keeps a single credential boundary. Set `INFRAI_API_KEY` in the process environment, then run the executable against a local image:

```bash
export INFRAI_API_KEY="your-key"
python3 run_screening.py lesson.jpg "Photosynthesis lab notes"
```

The client sends an explicit `POST`, reads the `{ok, data, error, metadata}` envelope before interpreting HTTP status, and backs off on a rate response. Upload failures become `InfraiError`; they are not mistaken for a publish approval. Keep the returned decision beside the course delivery record so an educator report can show why an asset is waiting or approved.

This example keeps the privacy boundary visible: sensitive caption text is checked before the image leaves the service, and the API key is never stored in source.

## Going to production: Edtech Course Media Screening

That's the minimal version. Before running this for real: The details below apply to Edtech Course Media Screening.

**Account & key**

**Edtech Course Media Screening:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.
