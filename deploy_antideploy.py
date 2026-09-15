import json
import os
import pathlib
import subprocess
import sys
import tarfile
import time
import urllib.request
import urllib.error

root = pathlib.Path.cwd()
config_path = pathlib.Path.home() / ".antideploy" / "config.json"
if not config_path.exists():
    print("Error: ~/.antideploy/config.json not found.", file=sys.stderr)
    sys.exit(1)

config = json.loads(config_path.read_text())
token = config.get("token")
if not token:
    print("Error: No token in ~/.antideploy/config.json.", file=sys.stderr)
    sys.exit(1)

app_id = "2891a2a8-464b-42bb-9857-85e6ac95cf25"

# Build tar archive in TEMP
archive = pathlib.Path(os.environ["TEMP"]) / "digital-guardrails-deploy.tar.gz"
print("Packaging project files...")
with tarfile.open(archive, "w:gz") as tar:
    # Add git tracked files except Dockerfile and frontend build tools (to ensure python runtime detection)
    excluded = ("Dockerfile", ".dockerignore", "render.yaml", "package.json", "package-lock.json", "tsconfig.json", "tsconfig.tsbuildinfo", "vite.config.ts", "netlify.toml", "vercel.json")
    for name in subprocess.check_output(["git", "ls-files"], text=True).splitlines():
        if name in excluded:
            continue
        p = root / name
        if p.is_file():
            tar.add(p, arcname=name)
    # Add dist and static web files
    for folder in [root / "dist", root / "backend" / "web_static"]:
        if folder.exists():
            for p in folder.rglob("*"):
                if p.is_file():
                    arcname = str(p.relative_to(root)).replace("\\", "/")
                    if arcname not in tar.getnames():
                        tar.add(p, arcname=arcname)
    # Add root config files
    for name in [".python-version", "requirements.txt", "Procfile", "main.py", ".antideploy.json", "digital_guardrails.db"]:
        p = root / name
        if p.is_file() and name not in tar.getnames():
            tar.add(p, arcname=name)

print(f"Archive ready: {archive.stat().st_size / 1024:.1f} KB")

boundary = "====AntideployDeployBoundary===="
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="archive"; filename="archive.tar.gz"\r\n'
    f"Content-Type: application/gzip\r\n\r\n"
).encode() + archive.read_bytes() + f"\r\n--{boundary}--\r\n".encode()

url = f"https://antideploy.com/api/v1/deploy?applicationId={app_id}"
req = urllib.request.Request(
    url,
    data=body,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    },
)

print(f"Uploading archive to Antideploy...")
try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print(f"Queued. Status: {res.get('status')}")
        task_id = res.get("taskId")
        watch_url = res.get("watch")
except urllib.error.HTTPError as e:
    err_body = e.read().decode()
    print(f"Deploy request error {e.code}: {err_body}", file=sys.stderr)
    sys.exit(1)

poll_url = watch_url if watch_url else f"https://antideploy.com/api/v1/deployments/{task_id}"
print(f"Watching deployment: {poll_url}")

start_time = time.time()
while time.time() - start_time < 600:
    time.sleep(4)
    poll_req = urllib.request.Request(poll_url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(poll_req) as poll_resp:
            dep = json.loads(poll_resp.read().decode())
            status = dep.get("status")
            steps = dep.get("steps", [])
            last_step = next((s for s in reversed(steps) if s.get("status") in ("done", "running", "failed")), None)
            step_desc = f" [{last_step['label']}: {last_step.get('status')}]" if last_step else ""
            print(f"Status: {status}{step_desc}")
            if status in ("succeeded", "failed"):
                if status == "succeeded":
                    app_info = dep.get("application", {})
                    print(f"\nSUCCESS: Deployed successfully!")
                    print(f"Live URL: {app_info.get('url', 'https://digital-guardrails.antideploy.com')}")
                else:
                    print(f"\nFAILED: {dep.get('error')}", file=sys.stderr)
                    if dep.get("deployment", {}).get("buildLog"):
                        print(f"Build Log:\n{dep['deployment']['buildLog']}", file=sys.stderr)
                break
    except urllib.error.HTTPError as e:
        print(f"Polling warning ({e.code}): {e.read().decode()}")

try:
    archive.unlink()
except Exception:
    pass
