
import os
import json
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

API_KEY = os.environ["YOUTUBE_API_KEY"]
HANDLE = os.environ["YOUTUBE_HANDLE"]
WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]
STATE_FILE = "last_count.json"

def get_json(url):
    with urllib.request.urlopen(url, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))

params = urllib.parse.urlencode({
    "part": "snippet,statistics",
    "forHandle": HANDLE,
    "key": API_KEY
})

data = get_json(
    "https://www.googleapis.com/youtube/v3/channels?" + params
)

channels = data.get("items", [])
if not channels:
    raise RuntimeError("ไม่พบช่อง YouTube กรุณาตรวจ YOUTUBE_HANDLE")

channel = channels[0]
name = channel["snippet"]["title"]
count = int(channel["statistics"]["subscriberCount"])

previous = None
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        previous = json.load(f).get("count")

with open(STATE_FILE, "w", encoding="utf-8") as f:
    json.dump({"count": count}, f)

if previous is None:
    print("บันทึกยอดเริ่มต้น:", count)

elif count != previous:
    now = datetime.now(ZoneInfo("Asia/Bangkok"))
    message = (
        f"📈 **ยอดซับช่อง {name} เปลี่ยนแล้ว!**\n"
        f"👥 ยอดปัจจุบัน: **{count:,} ซับ**\n"
        f"🕒 เวลา: {now.strftime('%d/%m/%Y %H:%M:%S')} น."
    )

    payload = json.dumps({"content": message}).encode("utf-8")
    request = urllib.request.Request(
        WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        print("Discord status:", response.status)
else:
    print("ยอดยังไม่เปลี่ยน")
