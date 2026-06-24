import argparse
import logging

from ai_company.adapters.web.server import serve
from ai_company.config import get_settings


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="AI Company Web adapter（dispatch HTTP）")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    serve(get_settings(), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
