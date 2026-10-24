import argparse
import urllib.request
import zipfile
from pathlib import Path


KITTI_ODOMETRY_URLS = {
    "calib": "https://s3.eu-central-1.amazonaws.com/avg-kitti/data_odometry_calib.zip",
    "gray": "https://s3.eu-central-1.amazonaws.com/avg-kitti/data_odometry_gray.zip",
    "poses": "https://s3.eu-central-1.amazonaws.com/avg-kitti/data_odometry_poses.zip",
    "velodyne": "https://s3.eu-central-1.amazonaws.com/avg-kitti/data_odometry_velodyne.zip",
}


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        print(f"already exists: {destination}")
        return

    temporary = destination.with_suffix(destination.suffix + ".part")
    resume_from = temporary.stat().st_size if temporary.exists() else 0
    request = urllib.request.Request(url)
    if resume_from:
        request.add_header("Range", f"bytes={resume_from}-")

    print(f"downloading {url}")
    print(f"to {destination}")
    if resume_from:
        print(f"resuming from {resume_from / (1024 ** 3):.2f} GiB")

    with urllib.request.urlopen(request) as response:
        content_length = response.headers.get("Content-Length")
        remaining = int(content_length) if content_length is not None else None
        total = resume_from + remaining if remaining is not None else None

        mode = "ab" if resume_from else "wb"
        downloaded = resume_from
        next_report = downloaded
        with temporary.open(mode) as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
                downloaded += len(chunk)
                if downloaded >= next_report:
                    if total:
                        percent = downloaded / total * 100.0
                        print(
                            f"{downloaded / (1024 ** 3):.2f} / "
                            f"{total / (1024 ** 3):.2f} GiB ({percent:.1f}%)"
                        )
                    else:
                        print(f"{downloaded / (1024 ** 3):.2f} GiB")
                    next_report = downloaded + 512 * 1024 * 1024

    temporary.replace(destination)


def extract(zip_path: Path, destination: Path) -> None:
    print(f"extracting {zip_path} -> {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--parts",
        nargs="+",
        choices=sorted(KITTI_ODOMETRY_URLS),
        default=["gray", "calib", "poses"],
        help="gray+calib+poses are enough for visual odometry; add velodyne for LiDAR SLAM.",
    )
    parser.add_argument("--download-dir", type=Path, default=Path("data/downloads/kitti"))
    parser.add_argument("--extract-dir", type=Path, default=Path("data/kitti"))
    parser.add_argument("--no-extract", action="store_true")
    args = parser.parse_args()

    for part in args.parts:
        zip_path = args.download_dir / f"data_odometry_{part}.zip"
        download(KITTI_ODOMETRY_URLS[part], zip_path)
        if not args.no_extract:
            extract(zip_path, args.extract_dir)

    print("done")
    print("expected root for scripts: data/kitti/dataset")


if __name__ == "__main__":
    main()
