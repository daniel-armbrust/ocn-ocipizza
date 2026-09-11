import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


CHECKS = (
    ("Oracle NoSQL", "http://nosql:8080"),
    ("Object Storage", "http://object-storage:9000/minio/health/live"),
)


def wait_for_service(name, url):
    print(f"Waiting {name}...")

    while True:
        try:
            with urlopen(url, timeout=5):
                print(f"{name} ready")
                return
        except HTTPError as exc:
            if exc.code < 500:
                print(f"{name} ready")
                return

            time.sleep(5)
        except URLError:
            time.sleep(5)


def main():
    for name, url in CHECKS:
        wait_for_service(name, url)


if __name__ == "__main__":
    main()
