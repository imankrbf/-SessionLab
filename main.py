"""
Session Security Lab - Main Application Entry Point

This FastAPI application demonstrates:
- Session Fixation vulnerability (Vulnerable mode)
- Session Regeneration fix (Secure mode)

For educational purposes only!
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from utils import hash_password

from database import engine, Base, SessionLocal
from models import User, SessionData
from routers import vulnerable, secure, hacker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Creates database tables and seeds initial data on startup.
    """
    # Create all database tables
    Base.metadata.create_all(bind=engine)
    
    # Seed the database with a test user
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == "admin").first()
        if not existing_user:
            # Create admin user with hashed password
            hashed_password = hash_password("123456")
            admin_user = User(username="admin", password_hash=hashed_password)
            db.add(admin_user)
            db.commit()
            print("✅ کاربر admin ایجاد شد (رمز: 123456)")
        else:
            print("ℹ️ کاربر admin قبلاً وجود دارد")
    finally:
        db.close()
    
    print("=" * 50)
    print("🔐 آزمایشگاه امنیت نشست - Version 2.0")
    print("=" * 50)
    print("📌 نسخه آسیب‌پذیر: http://localhost:8000/vulnerable/login")
    print("📌 نسخه امن: http://localhost:8000/secure/login")
    print("📌 پنل مهاجم: http://localhost:8000/hacker/dashboard")
    print("=" * 50)
    print("🎯 تست حمله Session Fixation:")
    print("   http://localhost:8000/vulnerable/login?token=HACKER_TOKEN_123")
    print("🎯 تست حمله XSS:")
    print("   http://localhost:8000/vulnerable/xss-demo")
    print("=" * 50)
    
    yield
    
    # Cleanup on shutdown (if needed)
    print("👋 سرور در حال خاموش شدن...")


# Create FastAPI application
app = FastAPI(
    title="آزمایشگاه امنیت نشست",
    description="نمایش آسیب‌پذیری Session Fixation و راه‌حل Session Regeneration",
    version="2.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(vulnerable.router)
app.include_router(secure.router)
app.include_router(hacker.router)

# Templates for home page
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Home page - redirects to a selection page or directly to vulnerable login.
    """
    return """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>آزمایشگاه امنیت نشست</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css">
        <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
        <style>
            * { font-family: 'Vazirmatn', sans-serif; }
            body {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .card-glass {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 24px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            .btn-vulnerable {
                background: linear-gradient(135deg, #dc3545, #c82333);
                border: none;
                padding: 20px 40px;
                border-radius: 16px;
                font-size: 1.2rem;
                transition: all 0.3s ease;
            }
            .btn-vulnerable:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(220, 53, 69, 0.4);
            }
            .btn-secure {
                background: linear-gradient(135deg, #198754, #157347);
                border: none;
                padding: 20px 40px;
                border-radius: 16px;
                font-size: 1.2rem;
                transition: all 0.3s ease;
            }
            .btn-secure:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(25, 135, 84, 0.4);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card-glass p-5 text-center">
                        <h1 class="mb-4">🔐 آزمایشگاه امنیت نشست</h1>
                        <p class="lead mb-5">
                            این پروژه برای نمایش آسیب‌پذیری <strong>Session Fixation</strong> 
                            و راه‌حل <strong>Session Regeneration</strong> طراحی شده است.
                        </p>
                        
                        <div class="row g-4">
                            <div class="col-md-6">
                                <a href="/vulnerable/login" class="btn btn-vulnerable text-white w-100">
                                    ⚠️ نسخه آسیب‌پذیر
                                    <br>
                                    <small>Session Fixation</small>
                                </a>
                            </div>
                            <div class="col-md-6">
                                <a href="/secure/login" class="btn btn-secure text-white w-100">
                                    ✅ نسخه امن
                                    <br>
                                    <small>Session Regeneration</small>
                                </a>
                            </div>
                        </div>
                        
                        <div class="mt-5 p-4 bg-light rounded-3">
                            <h5>📋 اطلاعات ورود نمایشی</h5>
                            <p class="mb-0">
                                نام کاربری: <code>admin</code> | رمز عبور: <code>123456</code>
                            </p>
                        </div>
                        
                        <div class="mt-4 p-4 border rounded-3">
                            <h5>🎯 تست حمله Session Fixation</h5>
                            <p class="mb-2">این لینک را امتحان کنید:</p>
                            <code class="d-block p-2 bg-dark text-success rounded" style="direction: ltr;">
                                http://localhost:8000/vulnerable/login?token=HACKER_TOKEN_123
                            </code>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
