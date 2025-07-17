# DEPRECATED, DOES NOT WORK WITH IFRAME + EDGE BROWSER, GETS BLOCKED, NEED TO BE FROM SAME SOCKET

# from fastapi import FastAPI, Request, Response
# from fastapi.responses import FileResponse
# from starlette.middleware.base import BaseHTTPMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware

# import uvicorn
# from pathlib import Path

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # or ["http://localhost:8501"]
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Custom middleware to add headers for all static files responses
# class AddHeadersMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         response = await call_next(request)

#         # Add headers only on static files responses (optionally check path)
#         if request.url.path.startswith("/files/"):
#             response.headers["X-Frame-Options"] = "ALLOWALL"
#             response.headers["Content-Security-Policy"] = "frame-ancestors *"

#         return response

# # ✅ Option 1: Serve the entire "Downloads" directory (quick way)

# app.add_middleware(AddHeadersMiddleware)

# downloads_path = Path("C:/Users/bvbraak/Downloads")
# app.mount("/files", StaticFiles(directory=str(downloads_path)), name="files")

# # ✅ Option 2: Serve a single file explicitly (safer way)
# # @app.get("/pdf")
# # def get_pdf():
# #     file_path = downloads_path / "2506.05176v3.pdf"
# #     return FileResponse(file_path, media_type="application/pdf")

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)