"""
Session Fixation Attack Test Script

This script automates testing of:
1. Session Fixation vulnerability in the vulnerable app
2. Session Regeneration protection in the secure app

Usage: python test_attack.py
"""
import requests


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(success: bool, message: str):
    """Print test result with color indication."""
    status = "✅ موفق" if success else "❌ ناموفق"
    print(f"\n{status}: {message}")


def test_vulnerable_app():
    """
    Test Session Fixation attack on the vulnerable app.
    Expected: Attack SUCCEEDS (session ID remains the same)
    """
    print_header("🔴 تست حمله Session Fixation - نسخه آسیب‌پذیر")
    
    base_url = "http://localhost:8000"
    attacker_token = "EVIL_ATTACKER_TOKEN_12345"
    
    try:
        # Step 1: Attacker creates a session with a known ID
        print("\n📌 مرحله 1: مهاجم لینک با توکن انتخابی ارسال می‌کند...")
        print(f"   URL: {base_url}/vulnerable/login?token={attacker_token}")
        
        session = requests.Session()
        response = session.get(
            f"{base_url}/vulnerable/login",
            params={"token": attacker_token}
        )
        
        print(f"   کد وضعیت: {response.status_code}")
        
        # Check if cookie was set
        if "vulnerable_session" in session.cookies:
            cookie_value = session.cookies.get("vulnerable_session")
            print(f"   کوکی تنظیم شده: {cookie_value}")
        
        # Step 2: Victim logs in using the attacker's link
        print("\n📌 مرحله 2: قربانی وارد سیستم می‌شود...")
        
        login_response = session.post(
            f"{base_url}/vulnerable/login",
            data={"username": "admin", "password": "123456"},
            allow_redirects=False
        )
        
        print(f"   کد وضعیت: {login_response.status_code}")
        
        # Step 3: Check the session ID after login
        # Follow redirect to dashboard
        if login_response.status_code == 302:
            dashboard_response = session.get(
                f"{base_url}/vulnerable/dashboard",
                allow_redirects=True
            )
        
        final_session_id = session.cookies.get("vulnerable_session")
        print(f"\n📌 مرحله 3: بررسی شناسه نشست پس از ورود...")
        print(f"   شناسه نشست: {final_session_id}")
        
        # Step 4: Verify if attack succeeded
        print("\n📌 مرحله 4: بررسی موفقیت حمله...")
        
        if final_session_id == attacker_token:
            print_result(True, "حمله Session Fixation موفق بود!")
            print(f"   شناسه نشست همان توکن مهاجم است: {attacker_token}")
            print("   ⚠️ مهاجم اکنون می‌تواند با این توکن به حساب قربانی دسترسی پیدا کند!")
            return True
        else:
            print_result(False, "حمله ناموفق - شناسه نشست تغییر کرده است")
            print(f"   توکن مهاجم: {attacker_token}")
            print(f"   شناسه فعلی: {final_session_id}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ خطا: سرور در دسترس نیست!")
        print("   لطفاً ابتدا سرور را اجرا کنید:")
        print("   uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        return False


def test_secure_app():
    """
    Test Session Fixation attack on the secure app.
    Expected: Attack FAILS (session ID is regenerated)
    """
    print_header("🟢 تست حمله Session Fixation - نسخه امن")
    
    base_url = "http://localhost:8000"
    attacker_token = "EVIL_ATTACKER_TOKEN_12345"
    
    try:
        # Step 1: Try to set a session with attacker's token
        print("\n📌 مرحله 1: تلاش مهاجم برای تنظیم توکن...")
        print(f"   URL: {base_url}/secure/login?token={attacker_token}")
        
        session = requests.Session()
        response = session.get(
            f"{base_url}/secure/login",
            params={"token": attacker_token}
        )
        
        print(f"   کد وضعیت: {response.status_code}")
        
        # Check if cookie was set (shouldn't be in secure version)
        if "secure_session" in session.cookies:
            cookie_value = session.cookies.get("secure_session")
            print(f"   کوکی تنظیم شده: {cookie_value}")
        else:
            print("   ✅ هیچ کوکی از طریق URL تنظیم نشد")
        
        # Step 2: User logs in
        print("\n📌 مرحله 2: کاربر وارد سیستم می‌شود...")
        
        login_response = session.post(
            f"{base_url}/secure/login",
            data={"username": "admin", "password": "123456"},
            allow_redirects=False
        )
        
        print(f"   کد وضعیت: {login_response.status_code}")
        
        # Step 3: Check the session ID after login
        if login_response.status_code == 302:
            # Get the new session cookie from redirect response
            if "set-cookie" in login_response.headers:
                print(f"   کوکی جدید تنظیم شد")
            
            dashboard_response = session.get(
                f"{base_url}/secure/dashboard",
                allow_redirects=True
            )
        
        final_session_id = session.cookies.get("secure_session")
        print(f"\n📌 مرحله 3: بررسی شناسه نشست پس از ورود...")
        print(f"   شناسه نشست: {final_session_id}")
        
        # Step 4: Verify if regeneration worked
        print("\n📌 مرحله 4: بررسی Session Regeneration...")
        
        if final_session_id != attacker_token and final_session_id is not None:
            print_result(True, "Session Regeneration موفق بود!")
            print(f"   توکن مهاجم: {attacker_token}")
            print(f"   شناسه جدید: {final_session_id}")
            print("   ✅ شناسه نشست تغییر کرده و حمله ناموفق است!")
            return True
        else:
            print_result(False, "Session Regeneration ناموفق")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ خطا: سرور در دسترس نیست!")
        print("   لطفاً ابتدا سرور را اجرا کنید:")
        print("   uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "🔐" * 30)
    print("\n   اسکریپت تست خودکار حمله Session Fixation")
    print("\n" + "🔐" * 30)
    
    # Test vulnerable app
    vulnerable_result = test_vulnerable_app()
    
    # Test secure app
    secure_result = test_secure_app()
    
    # Summary
    print_header("📊 خلاصه نتایج")
    
    print("\n نسخه آسیب‌پذیر:")
    if vulnerable_result:
        print("   🔴 حمله Session Fixation موفق بود - سیستم آسیب‌پذیر است!")
    else:
        print("   ⚠️ نتیجه غیرمنتظره")
    
    print("\n نسخه امن:")
    if secure_result:
        print("   🟢 حمله ناموفق بود - Session Regeneration کار می‌کند!")
    else:
        print("   ⚠️ نتیجه غیرمنتظره")
    
    print("\n" + "=" * 60)
    
    # Return overall success
    return vulnerable_result and secure_result


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
