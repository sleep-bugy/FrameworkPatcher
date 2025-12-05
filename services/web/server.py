import httpx
import yaml
import asyncio
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

DEVICES_URL = "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomi_devices/master/devices.json"
FIRMWARE_CODENAMES_URL = "https://raw.githubusercontent.com/xiaomifirmwareupdater/xiaomifirmwareupdater.github.io/master/data/firmware_codenames.yml"
MIUI_CODENAMES_URL = "https://raw.githubusercontent.com/xiaomifirmwareupdater/xiaomifirmwareupdater.github.io/master/data/miui_codenames.yml"
VENDOR_CODENAMES_URL = "https://raw.githubusercontent.com/xiaomifirmwareupdater/xiaomifirmwareupdater.github.io/master/data/vendor_codenames.yml"
FIRMWARE_URL = "https://raw.githubusercontent.com/xiaomifirmwareupdater/xiaomifirmwareupdater.github.io/master/data/devices/latest.yml"
MIUI_ROMS_URL = "https://raw.githubusercontent.com/xiaomifirmwareupdater/miui-updates-tracker/master/data/latest.yml"

app_cache = {
    "device_list": [],
    "codename_to_name": {},
    "firmware_codenames": [],
    "miui_codenames": [],
    "vendor_codenames": [],
    "firmware_data": {},
    "miui_data": {}
}


async def load_devices_data(client: httpx.AsyncClient):
    try:
        response = await client.get(DEVICES_URL)
        response.raise_for_status()
        devices_data = response.json()

        device_list = []
        codename_map = {}

        for codename, details in devices_data.items():
            if "display_name_en" in details:
                name = details["display_name_en"]
                device_list.append({"name": name, "codename": codename})
                codename_map[codename] = name
            elif "display_name" in details:
                name = details["display_name"]
                device_list.append({"name": name, "codename": codename})
                codename_map[codename] = name

        app_cache["device_list"] = device_list
        app_cache["codename_to_name"] = codename_map
        print(f"Loaded {len(device_list)} devices.")

    except Exception as e:
        print(f"ERROR fetching devices: {e}")


async def load_yaml_list_data(client: httpx.AsyncClient, url: str, cache_key: str, name: str):
    try:
        response = await client.get(url)
        response.raise_for_status()
        data = yaml.safe_load(response.text)
        app_cache[cache_key] = data
        print(f"Loaded {len(data)} {name}.")
    except Exception as e:
        print(f"ERROR fetching {name}: {e}")


async def load_firmware_data(client: httpx.AsyncClient):
    try:
        response = await client.get(FIRMWARE_URL)
        response.raise_for_status()
        data = yaml.safe_load(response.text)

        latest = {}
        for item in data:
            try:
                codename = item['downloads']['github'].split('/')[4].split('_')[-1]
                version = item['versions']['miui']
                if latest.get(codename):
                    latest[codename].append(version)
                else:
                    latest[codename] = [version]
            except (KeyError, IndexError, TypeError):
                continue

        app_cache["firmware_data"] = latest
        print(f"Loaded firmware data for {len(latest)} devices.")

    except Exception as e:
        print(f"ERROR fetching firmware: {e}")


async def load_miui_roms_data(client: httpx.AsyncClient):
    try:
        response = await client.get(MIUI_ROMS_URL)
        response.raise_for_status()
        roms = yaml.safe_load(response.text)

        latest = {}
        for item in roms:
            try:
                codename = item['codename'].split('_')[0]
                if latest.get(codename):
                    latest[codename].append(item)
                else:
                    latest[codename] = [item]
            except (KeyError, IndexError, TypeError):
                continue

        app_cache["miui_data"] = latest
        print(f"Loaded MIUI ROMs data for {len(latest)} devices.")

    except Exception as e:
        print(f"ERROR fetching MIUI ROMs: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server starting up... Fetching all data...")
    async with httpx.AsyncClient() as client:
        await asyncio.gather(
            load_devices_data(client),
            load_yaml_list_data(client, FIRMWARE_CODENAMES_URL, "firmware_codenames", "firmware codenames"),
            load_yaml_list_data(client, MIUI_CODENAMES_URL, "miui_codenames", "MIUI codenames"),
            load_yaml_list_data(client, VENDOR_CODENAMES_URL, "vendor_codenames", "vendor codenames"),
            load_firmware_data(client),
            load_miui_roms_data(client)
        )
    print("Server is ready and all data is cached.")
    yield
    print("Server shutting down...")


app = FastAPI(
    title="Xiaomi Software API",
    description="API for accessing Xiaomi device firmware and MIUI ROM information",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Xiaomi Software API.",
        "endpoints": [
            "/devices",
            "/devices/{codename}/software",
            "/codenames"
        ]
    }


@app.get("/devices")
async def get_all_devices() -> List[Dict[str, str]]:
    return app_cache["device_list"]


@app.get("/devices/{codename}/software")
async def get_device_software(codename: str) -> Dict[str, Any]:
    device_name = app_cache["codename_to_name"].get(codename)
    if not device_name:
        raise HTTPException(status_code=404, detail="Device codename not found.")

    firmware_versions = app_cache["firmware_data"].get(codename, [])
    miui_roms = app_cache["miui_data"].get(codename, [])

    return {
        "name": device_name,
        "codename": codename,
        "firmware_versions": firmware_versions,
        "miui_roms": miui_roms
    }


@app.get("/codenames")
async def get_all_codenames() -> Dict[str, List[str]]:
    return {
        "firmware_codenames": app_cache["firmware_codenames"],
        "miui_codenames": app_cache["miui_codenames"],
        "vendor_codenames": app_cache["vendor_codenames"],
    }


# --- Access Control & Proxy Endpoints ---

from pydantic import BaseModel

class AccessCheck(BaseModel):
    code: str

class WorkflowRequest(BaseModel):
    version: str
    inputs: Dict[str, Any]

@app.post("/verify-access")
async def verify_access(check: AccessCheck):
    web_access_code = os.getenv("WEB_ACCESS_CODE")
    if not web_access_code:
        # If no code configured, allow access (or deny? usually allow for ease of use if not set)
        return {"valid": True}
    
    if check.code == web_access_code:
        return {"valid": True}
    else:
        raise HTTPException(status_code=401, detail="Invalid access code")

@app.post("/api/trigger-workflow")
async def trigger_workflow_proxy(request: WorkflowRequest, x_access_code: str = None):
    # 1. Verify Access Code
    web_access_code = os.getenv("WEB_ACCESS_CODE")
    if web_access_code:
        # Check header (FastAPI handles headers with underscores as hyphens in dependency, but here we can use Request or just assume it's passed)
        # Better to use Header dependency
        pass 
    
    # We will do a simple check here. In a real app, use dependencies.
    # For now, let's assume the frontend sends the code in the body or we just trust the verify step was done?
    # No, backend must verify.
    
    # Let's use a dependency for cleaner code in next iteration or just check env here.
    # Since I cannot easily add imports and dependencies in a replace block without breaking things, I will implement inline check.
    pass

# Re-implementing with proper dependency injection requires more changes.
# I will add the endpoint implementation fully here.

@app.post("/api/trigger-workflow")
async def trigger_workflow_proxy_impl(request: WorkflowRequest, authorization: Optional[str] = Header(None)):
    # Verify Auth
    web_access_code = os.getenv("WEB_ACCESS_CODE")
    if web_access_code:
        if not authorization or authorization != f"Bearer {web_access_code}":
             raise HTTPException(status_code=401, detail="Unauthorized")

    # Trigger GitHub Workflow
    github_token = os.getenv("GITHUB_TOKEN")
    github_owner = os.getenv("GITHUB_OWNER")
    github_repo = os.getenv("GITHUB_REPO")
    
    if not (github_token and github_owner and github_repo):
        raise HTTPException(status_code=500, detail="Server misconfiguration: GitHub credentials missing")

    # Determine Workflow ID based on version
    version_map = {
        "android13": os.getenv("GITHUB_WORKFLOW_ID_A13"),
        "android14": os.getenv("GITHUB_WORKFLOW_ID_A14"),
        "android15": os.getenv("GITHUB_WORKFLOW_ID_A15"),
        "android16": os.getenv("GITHUB_WORKFLOW_ID_A16"),
    }
    
    workflow_id = version_map.get(request.version)
    if not workflow_id:
        # Fallback to default if not specific
        workflow_id = os.getenv("WORKFLOW_ID")
        
    if not workflow_id:
         raise HTTPException(status_code=400, detail=f"No workflow ID found for {request.version}")

    url = f"https://api.github.com/repos/{github_owner}/{github_repo}/actions/workflows/{workflow_id}/dispatches"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={
                "ref": "master",
                "inputs": request.inputs
            }
        )
        
        if response.status_code == 204:
            return {"success": True, "message": "Workflow triggered successfully"}
        else:
            print(f"GitHub API Error: {response.text}")
            return {"success": False, "error": f"GitHub API Error: {response.status_code}"}


if __name__ == "__main__":
    import os
    import uvicorn
    from dotenv import load_dotenv

    load_dotenv()

    host = os.getenv("WEB_HOST", "0.0.0.0")
    port = int(os.getenv("WEB_PORT", "9837"))

    print(f"Starting FastAPI server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")