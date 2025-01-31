import asyncio
import threading
import queue
from urllib.parse import urlparse
import aiohttp
import re
import os
import orchestration

targetDir = "./Storage/Downloads"

def download(url: str, fileName = None, job_data = None):
    orchestration.queue_add("download_request", {
            'url':url, 
            'file': fileName, 
            'jobData': job_data,
        })

def init():
    pass

def process_job(job: dict):
    asyncio.run(fetch(job['url'], job['file'], job['jobData']))


async def fetch(url, fileName = None, job_data = None):
    async with aiohttp.ClientSession() as client:
        async with client.get(url) as resp:
            print(url)
            path = urlparse(url).path

            if fileName == None:
                fileName = os.path.basename(path)
                if "Content-Disposition" in resp.headers:
                    headerMatch = re.match("filename=\"?([^\s\"/\\]+)\"?", resp.headers['Content-Disposition'])
                    if headerMatch:
                        fileName = headerMatch[0]
            
            
            targetFile = os.path.join(targetDir, fileName)

            try:
                with open(targetFile, "wb") as pkg:
                    while True:
                        data = await resp.content.read()
                        if not data:
                            break
                        pkg.write(data)
                orchestration.queue_add("download_complete", {
                        'url': url,
                        'file': fileName,
                        'filePath': targetFile,
                        'jobData': job_data,
                    })
            except Exception:
                pass

def isDownloaded(fileName):
    targetFile = os.path.join(targetDir, fileName)
    return os.path.exists(targetFile)

def getDownloadedPath(fileName):
    return os.path.join(targetDir, fileName)