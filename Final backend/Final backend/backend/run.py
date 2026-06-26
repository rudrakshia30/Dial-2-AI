"""
Start the voice-call backend.

Usage:
  py run.py           # recommended for Exotel calls (clean Ctrl+C, no reload)
  py run.py --dev     # auto-reload while editing code (noisy Ctrl+C on Windows)
"""
import argparse
import sys

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AI voice backend")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Watch app/ for changes and auto-reload (can interrupt active calls)",
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    print(f"Starting server on http://{args.host}:{args.port}")
    if args.dev:
        print("Dev reload enabled — press Ctrl+C once and wait a second to stop.")
    else:
        print("Press Ctrl+C to stop.")

    try:
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            reload=args.dev,
            reload_dirs=["app"] if args.dev else None,
        )
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
