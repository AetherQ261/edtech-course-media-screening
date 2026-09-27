import argparse
import json
from src.edtech_screening import CourseMediaScreen, InfraiImageClient, UploadRequest


def main() -> None:
    parser = argparse.ArgumentParser(description="Screen one course image before publishing")
    parser.add_argument("filename")
    parser.add_argument("caption")
    args = parser.parse_args()
    with open(args.filename, "rb") as image_file:
        decision = CourseMediaScreen(InfraiImageClient()).screen(
            UploadRequest(image_file.read(), args.filename, args.caption)
        )
    print(json.dumps(decision.__dict__, sort_keys=True))


if __name__ == "__main__":
    main()
