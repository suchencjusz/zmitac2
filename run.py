import multiprocessing

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5000,
        workers=multiprocessing.cpu_count(),
        reload=True,
        log_level="info",
        access_log=True,
        proxy_headers=True,
        forwarded_allow_ips="*",
        interface="wsgi",
    )
