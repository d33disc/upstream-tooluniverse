#!/usr/bin/env python3
"""
ToolUniverse HTTP API Server CLI

Command-line interface for starting the ToolUniverse HTTP API server.

Usage:
    tooluniverse-http-api --host 0.0.0.0 --port 8080
    tooluniverse-http-api --host 0.0.0.0 --port 8080 --workers 4
"""

import argparse
import sys


def run_http_api_server():
    """Main entry point for the HTTP API server"""
    parser = argparse.ArgumentParser(
        description="Start ToolUniverse HTTP API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start server on default port
  tooluniverse-http-api

  # Start on specific host and port
  tooluniverse-http-api --host 0.0.0.0 --port 8080

  # Start with multiple workers for production
  tooluniverse-http-api --host 0.0.0.0 --port 8080 --workers 4

  # Start with reload for development
  tooluniverse-http-api --reload

Features:
  - Auto-discovers all ToolUniverse methods via introspection
  - No manual updates needed when ToolUniverse changes
  - Thread-safe singleton ToolUniverse instance
  - Full API documentation at /docs
        """,
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1, use 0.0.0.0 for remote access)",
    )

    parser.add_argument(
        "--port", type=int, default=8080, help="Port to bind to (default: 8080)"
    )

    parser.add_argument(
        "--workers", type=int, default=8, help="Number of worker processes (default: 8)"
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development (not for production)",
    )

    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="Log level (default: info)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("🚀 ToolUniverse HTTP API Server")
    print("=" * 70)
    print(f"📡 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"⚙️  Workers: {args.workers}")
    print(f"📝 Log Level: {args.log_level}")
    print(f"🔄 Auto-reload: {'Enabled' if args.reload else 'Disabled'}")
    print()
    print("📚 API Documentation:")
    print(f"   - Swagger UI: http://{args.host}:{args.port}/docs")
    print(f"   - ReDoc: http://{args.host}:{args.port}/redoc")
    print()
    print("🔧 Endpoints:")
    print(f"   - Call method: POST http://{args.host}:{args.port}/api/call")
    print(f"   - List methods: GET http://{args.host}:{args.port}/api/methods")
    print(f"   - Health check: GET http://{args.host}:{args.port}/health")
    print()
    print("💡 Client Usage:")
    print("   from tooluniverse import ToolUniverseClient")
    print(f'   client = ToolUniverseClient("http://{args.host}:{args.port}")')
    print("   client.load_tools(tool_type=['uniprot', 'ChEMBL'])")
    print()
    print("=" * 70)
    print()

    try:
        import uvicorn

        # Use import string when workers > 1 (required by uvicorn)
        if args.workers > 1 and not args.reload:
            app_import = "tooluniverse.http_api_server:app"
            uvicorn.run(
                app_import,
                host=args.host,
                port=args.port,
                workers=args.workers,
                log_level=args.log_level,
            )
        else:
            # Single worker or reload mode: import app directly
            from .http_api_server import app

            uvicorn.run(
                app,
                host=args.host,
                port=args.port,
                workers=1,  # reload requires workers=1
                reload=args.reload,
                log_level=args.log_level,
            )

    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error starting server: {e}")
        print("\nMake sure FastAPI and Uvicorn are installed:")
        print("  pip install fastapi uvicorn")
        sys.exit(1)


if __name__ == "__main__":
    run_http_api_server()
