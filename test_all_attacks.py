"""
Comprehensive Session Security Test Script

This script automates testing of:
1. Session Fixation vulnerability
2. Session Hijacking simulation
3. Session Regeneration protection
4. Cookie security flags check

Usage: python test_all_attacks.py
"""
import requests
from typing import Tuple


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subheader(title: str):
    """Print a formatted subheader."""
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")


def print_result(success: bool, message: str):
    """Print test result with color indication."""
    status = "✅ موفق" if success else "❌ ناموفق"
    print(f"\n{status}: {message}")


def print_step(step_num: int, message: str):
    """Print a step indicator."""
    print(f"\n📌 مرحله {step_num}: {message}")


# =============================================================================
# Test 1: Session Fixation on Vulnerable App
# =============================================================================

def test_session_fixation_vulnerable() -> bool:
    """
    Test Session Fixation attack on the vulnerable app.
    Expected: Attack SUCCEEDS (session ID remains the same)
    """
    print_header("🔴 تست ۱: حمله Session Fixation - نسخه آسیب‌پذیر")
    
    base_url = "http://localhost:8000"
    attacker_token = "ATTACKER_FIXED_TOKEN_XYZ"
    
    try:
        print_step(1, "مهاجم لینک مخرب با توکن انتخابی می‌سازد")
        print(f"   لینک مخرب: {base_url}/vulnerable/login?token={attacker_token}")
        
        # Simulate victim clicking attacker's link
        session = requests.Session()
        response = session.get(
            f"{base_url}/vulnerable/login",
            params={"token": attacker_token}
        )
        
        print(f"   کد وضعیت: {response.status_code}")
        
        cookie_before = session.cookies.get("vulnerable_session")
        print(f"   کوکی تنظیم شده: {cookie_before}")
        
        print_step(2, "قربانی با لینک مخرب وارد سیستم می‌شود")
        
        login_response = session.post(
            f"{base_url}/vulnerable/login",
            data={"username": "admin", "password": "123456"},
            allow_redirects=False
        )
        
        print(f"   کد وضعیت لاگین: {login_response.status_code}")
        
        # Follow redirect
        if login_response.status_code == 302:
            session.get(f"{base_url}/vulnerable/dashboard", allow_redirects=True)
        
        session_id_after = session.cookies.get("vulnerable_session")
        
        print_step(3, "بررسی شناسه نشست پس از ورود")
        print(f"   توکن مهاجم: {attacker_token}")
        print(f"   شناسه نشست: {session_id_after}")
        
        print_step(4, "بررسی موفقیت حمله")
        
        if session_id_after == attacker_token:
            print_result(True, "حمله Session Fixation موفق بود!")
            print("   ⚠️ مهاجم با استفاده از همین توکن می‌تواند به حساب قربانی دسترسی پیدا کند!")
            return True
        else:
            print_result(False, "حمله ناموفق - شناسه تغییر کرده")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ خطا: سرور در دسترس نیست!")
        return False
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        return False


# =============================================================================
# Test 2: Session Hijacking Simulation
# =============================================================================

def test_session_hijacking() -> bool:
    """
    Simulate Session Hijacking attack.
    Shows how an attacker can use a stolen session ID.
    """
    print_header("🔵 تست ۲: شبیه‌سازی حمله Session Hijacking")
    
    base_url = "http://localhost:8000"
    
    try:
        print_step(1, "قربانی به صورت عادی وارد سیستم می‌شود")
        
        victim_session = requests.Session()
        victim_session.post(
            f"{base_url}/vulnerable/login",
            data={"username": "admin", "password": "123456"},
            allow_redirects=True
        )
        
        victim_session_id = victim_session.cookies.get("vulnerable_session")
        print(f"   شناسه نشست قربانی: {victim_session_id}")
        
        # Verify victim is logged in
        dashboard_response = victim_session.get(f"{base_url}/vulnerable/dashboard")
        victim_logged_in = "admin" in dashboard_response.text
        print(f"   وضعیت ورود قربانی: {'✅ وارد شده' if victim_logged_in else '❌ خارج'}")
        
        print_step(2, "مهاجم شناسه نشست را سرقت می‌کند")
        print(f"   (در دنیای واقعی: XSS، شنود شبکه، دسترسی فیزیکی)")
        stolen_session_id = victim_session_id
        print(f"   شناسه سرقت شده: {stolen_session_id}")
        
        print_step(3, "مهاجم با شناسه سرقتی وارد می‌شود")
        
        attacker_session = requests.Session()
        attacker_session.cookies.set("vulnerable_session", stolen_session_id)
        
        attacker_response = attacker_session.get(f"{base_url}/vulnerable/dashboard")
        
        print(f"   کد وضعیت: {attacker_response.status_code}")
        
        print_step(4, "بررسی دسترسی مهاجم")
        
        attacker_has_access = "admin" in attacker_response.text and "داشبورد" in attacker_response.text
        
        if attacker_has_access:
            print_result(True, "حمله Session Hijacking موفق بود!")
            print("   ⚠️ مهاجم بدون رمز عبور به حساب قربانی دسترسی پیدا کرد!")
            return True
        else:
            print_result(False, "مهاجم نتوانست دسترسی پیدا کند")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ خطا: سرور در دسترس نیست!")
        return False
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        return False


# =============================================================================
# Test 3: Session Regeneration on Secure App
# =============================================================================

def test_session_regeneration() -> bool:
    """
    Test Session Regeneration protection on the secure app.
    Expected: Attack FAILS (session ID is regenerated)
    """
    print_header("🟢 تست ۳: محافظت Session Regeneration - نسخه امن")
    
    base_url = "http://localhost:8000"
    attacker_token = "ATTACKER_FIXED_TOKEN_XYZ"
    
    try:
        print_step(1, "تلاش مهاجم برای تثبیت توکن")
        print(f"   لینک مخرب: {base_url}/secure/login?token={attacker_token}")
        
        session = requests.Session()
        response = session.get(
            f"{base_url}/secure/login",
            params={"token": attacker_token}
        )
        
        print(f"   کد وضعیت: {response.status_code}")
        
        if "secure_session" in session.cookies:
            print(f"   ⚠️ کوکی تنظیم شده: {session.cookies.get('secure_session')}")
        else:
            print("   ✅ هیچ کوکی از طریق URL تنظیم نشد")
        
        print_step(2, "کاربر وارد سیستم می‌شود")
        
        login_response = session.post(
            f"{base_url}/secure/login",
            data={"username": "admin", "password": "123456"},
            allow_redirects=False
        )
        
        print(f"   کد وضعیت: {login_response.status_code}")
        
        if login_response.status_code == 302:
            session.get(f"{base_url}/secure/dashboard", allow_redirects=True)
        
        final_session_id = session.cookies.get("secure_session")
        
        print_step(3, "بررسی شناسه نشست")
        print(f"   توکن مهاجم: {attacker_token}")
        print(f"   شناسه تولید شده: {final_session_id}")
        
        print_step(4, "بررسی Session Regeneration")
        
        if final_session_id != attacker_token and final_session_id is not None:
            print_result(True, "Session Regeneration موفق!")
            print("   ✅ شناسه جدید کاملاً متفاوت است - حمله Fixation ناموفق!")
            return True
        else:
            print_result(False, "Session Regeneration ناموفق")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ خطا: سرور در دسترس نیست!")
        return False
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        return False


# =============================================================================
# Test 4: Cookie Security Flags
# =============================================================================

def test_cookie_security_flags() -> Tuple[bool, bool]:
    """
    Check cookie security flags in both versions.
    Returns: (vulnerable_insecure, secure_is_secure)
    """
    print_header("🔒 تست ۴: بررسی پرچم‌های امنیتی کوکی")
    
    base_url = "http://localhost:8000"
    
    try:
        print_subheader("نسخه آسیب‌پذیر")
        
        vuln_session = requests.Session()
        vuln_response = vuln_session.post(
            f"{base_url}/vulnerable/login",
            data={"username": "admin", "password": "123456"},
            allow_redirects=False
        )
        
        vuln_cookies = vuln_response.cookies
        vuln_cookie = vuln_cookies.get("vulnerable_session")
        
        print(f"   کوکی: vulnerable_session")
        print(f"   شناسه: {vuln_cookie[:20]}..." if vuln_cookie and len(vuln_cookie) > 20 else f"   شناسه: {vuln_cookie}")
        
        # Check Set-Cookie header
        set_cookie_header = vuln_response.headers.get("set-cookie", "")
        print(f"   HttpOnly: {'❌ خیر' if 'httponly' not in set_cookie_header.lower() else '✅ بله'}")
        print(f"   SameSite: {'lax' if 'samesite=lax' in set_cookie_header.lower() else 'نامشخص'}")
        
        vuln_insecure = "httponly" not in set_cookie_header.lower()
        
        print_subheader("نسخه امن")
        
        secure_session = requests.Session()
        secure_response = secure_session.post(
            f"{base_url}/secure/login",
            data={"username": "admin", "password": "123456"},
            allow_redirects=False
        )
        
        secure_cookie = secure_response.cookies.get("secure_session")
        
        print(f"   کوکی: secure_session")
        print(f"   شناسه: {secure_cookie[:20]}..." if secure_cookie and len(secure_cookie) > 20 else f"   شناسه: {secure_cookie}")
        
        set_cookie_header = secure_response.headers.get("set-cookie", "")
        has_httponly = "httponly" in set_cookie_header.lower()
        has_samesite = "samesite" in set_cookie_header.lower()
        
        print(f"   HttpOnly: {'✅ بله' if has_httponly else '❌ خیر'}")
        print(f"   SameSite: {'✅ lax' if 'samesite=lax' in set_cookie_header.lower() else '❌ نامشخص'}")
        
        secure_is_secure = has_httponly
        
        print_subheader("نتیجه مقایسه")
        print(f"   نسخه آسیب‌پذیر: {'🔴 ناامن' if vuln_insecure else '🟢 امن'}")
        print(f"   نسخه امن: {'🟢 امن' if secure_is_secure else '🔴 ناامن'}")
        
        return vuln_insecure, secure_is_secure
        
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        return False, False


# =============================================================================
# Test 5: User Registration Test
# =============================================================================

def test_user_registration() -> bool:
    """Test user registration functionality."""
    print_header("📝 تست ۵: سیستم ثبت‌نام کاربر")
    
    base_url = "http://localhost:8000"
    test_username = "testuser_demo"
    test_password = "demo123456"
    
    try:
        print_step(1, "ثبت‌نام کاربر جدید")
        
        session = requests.Session()
        response = session.post(
            f"{base_url}/secure/register",
            data={
                "username": test_username,
                "password": test_password,
                "password_confirm": test_password
            }
        )
        
        print(f"   کد وضعیت: {response.status_code}")
        
        registration_success = "موفقیت" in response.text or response.status_code == 200
        
        if "قبلاً استفاده شده" in response.text:
            print("   ℹ️ کاربر قبلاً وجود دارد")
            registration_success = True
        elif "موفقیت" in response.text:
            print("   ✅ ثبت‌نام موفق")
        
        print_step(2, "ورود با کاربر جدید")
        
        login_response = session.post(
            f"{base_url}/secure/login",
            data={"username": test_username, "password": test_password},
            allow_redirects=True
        )
        
        login_success = test_username in login_response.text or "داشبورد" in login_response.text
        print(f"   ورود موفق: {'✅ بله' if login_success else '❌ خیر'}")
        
        if registration_success and login_success:
            print_result(True, "سیستم ثبت‌نام و ورود کار می‌کند!")
            return True
        else:
            print_result(False, "مشکل در سیستم ثبت‌نام یا ورود")
            return False
            
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        return False


# =============================================================================
# Main Test Runner
# =============================================================================

def main():
    """Run all tests."""
    print("\n" + "🔐" * 35)
    print("\n   آزمایشگاه امنیت نشست - تست جامع")
    print("   Session Security Lab - Comprehensive Test")
    print("\n" + "🔐" * 35)
    
    results = {}
    
    # Test 1: Session Fixation on Vulnerable
    results["fixation_vuln"] = test_session_fixation_vulnerable()
    
    # Test 2: Session Hijacking
    results["hijacking"] = test_session_hijacking()
    
    # Test 3: Session Regeneration on Secure
    results["regeneration"] = test_session_regeneration()
    
    # Test 4: Cookie Security Flags
    vuln_insecure, secure_is_secure = test_cookie_security_flags()
    results["cookie_flags"] = vuln_insecure and secure_is_secure
    
    # Test 5: User Registration
    results["registration"] = test_user_registration()
    
    # Summary
    print_header("📊 خلاصه نتایج تست‌ها")
    
    print("\n┌─────────────────────────────────────────────────────────────────┐")
    print("│ تست                                        │ نتیجه              │")
    print("├─────────────────────────────────────────────────────────────────┤")
    
    test_names = {
        "fixation_vuln": "Session Fixation (آسیب‌پذیر)",
        "hijacking": "Session Hijacking",
        "regeneration": "Session Regeneration (امن)",
        "cookie_flags": "پرچم‌های امنیتی کوکی",
        "registration": "سیستم ثبت‌نام"
    }
    
    all_passed = True
    for key, name in test_names.items():
        passed = results.get(key, False)
        status = "✅ پاس" if passed else "❌ رد"
        print(f"│ {name:<43} │ {status:<18} │")
        if not passed:
            all_passed = False
    
    print("└─────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("\n🎉 همه تست‌ها با موفقیت اجرا شدند!")
        print("   پروژه آماده ارائه است.")
    else:
        print("\n⚠️ برخی تست‌ها ناموفق بودند.")
        print("   لطفاً مشکلات را بررسی کنید.")
    
    print("\n" + "=" * 70)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
