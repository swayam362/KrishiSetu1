#!/usr/bin/env python3
"""
KrushiSetu Secure Administrator Provisioning Script
Creates or promotes an initial administrator account safely in MongoDB.
Ensures zero hardcoded credentials, strong password hashing, and audit logging.

Usage:
  Interactive:
    python backend/scripts/create_admin.py

  Non-interactive / CI / Deployment:
    python backend/scripts/create_admin.py --email admin@krushisetu.com --password YourStrongPassword123! --name "KrushiSetu Owner" --phone 9876543210
"""

import os
import sys
import argparse
import getpass
import datetime

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import get_db, make_id_query
from backend.utils.security import hash_password, validate_email, validate_phone, sanitize_string

def create_or_update_admin(email: str, password: str, full_name: str, phone: str = ""):
    email = email.strip().lower()
    full_name = sanitize_string(full_name.strip() or "KrushiSetu Administrator")
    phone = phone.strip()

    if not validate_email(email):
        print(f"[ERROR] Invalid email format: '{email}'")
        sys.exit(1)

    if not password or len(password) < 8:
        print("[ERROR] Password must be at least 8 characters long for administrative accounts.")
        sys.exit(1)

    if phone and not validate_phone(phone):
        print(f"[ERROR] Invalid mobile number format: '{phone}'. Must be a 10-15 digit phone number.")
        sys.exit(1)

    db = get_db()
    if not db.is_connected:
        print("[WARNING] MongoDB server is not reachable. Operating on fallback store.")

    users_col = db.get_collection("users")
    logs_col = db.get_collection("admin_logs")

    # Check if user already exists
    existing_user = users_col.find_one({"email": email})
    if not existing_user and phone:
        existing_user = users_col.find_one({"phone": phone})

    hashed_pwd = hash_password(password)
    now_iso = datetime.datetime.utcnow().isoformat()

    if existing_user:
        user_id = str(existing_user.get("_id") or existing_user.get("id"))
        update_fields = {
            "email": email,
            "role": "admin",
            "is_active": True,
            "password_hash": hashed_pwd,
            "full_name": full_name,
            "updated_at": now_iso
        }
        if phone:
            update_fields["phone"] = phone

        users_col.update_one(make_id_query(user_id), {"$set": update_fields})
        print(f"[SUCCESS] Existing account '{email}' has been promoted to ADMIN role.")
        action = "ADMIN_PROMOTED"
    else:
        new_admin = {
            "full_name": full_name,
            "email": email,
            "phone": phone or "9800000000",
            "role": "admin",
            "state": "Maharashtra",
            "district": "Pune",
            "is_active": True,
            "password_hash": hashed_pwd,
            "created_at": now_iso,
            "updated_at": now_iso
        }
        insert_res = users_col.insert_one(new_admin)
        user_id = str(getattr(insert_res, "inserted_id", new_admin.get("_id", "")))
        print(f"[SUCCESS] New administrator account created successfully for '{email}'.")
        action = "ADMIN_PROVISIONED"

    # Write audit log without passwords or secrets
    try:
        logs_col.insert_one({
            "action": action,
            "admin_id": user_id,
            "admin_email": email,
            "target_type": "USER",
            "target_id": user_id,
            "details": f"Admin account provisioned for '{full_name}' ({email}).",
            "created_at": now_iso
        })
    except Exception as e:
        print(f"[NOTE] Audit logging note: {e}")

    print("=" * 60)
    print("ADMINISTRATOR CREDENTIALS SUMMARY")
    print("=" * 60)
    print(f"  User ID : {user_id}")
    print(f"  Name    : {full_name}")
    print(f"  Email   : {email}")
    print(f"  Role    : ADMIN")
    print(f"  Status  : Active")
    print("  Password: [SECURELY STORED - BCRYPT ENCRYPTED]")
    print("=" * 60)
    print("You can now log in at /login.html with this administrator account.")

def main():
    parser = argparse.ArgumentParser(description="KrushiSetu Administrator Account Setup")
    parser.add_argument("--email", help="Administrator email address")
    parser.add_argument("--password", help="Administrator password (min 8 characters)")
    parser.add_argument("--name", help="Administrator full name", default="KrushiSetu Owner")
    parser.add_argument("--phone", help="Administrator mobile number", default="")

    args = parser.parse_args()

    email = args.email
    password = args.password
    name = args.name
    phone = args.phone

    # Interactive mode if parameters are omitted
    if not email:
        print("--- KrushiSetu Admin Setup (Interactive Mode) ---")
        email = input("Enter Admin Email: ").strip()
    if not name:
        name = input("Enter Admin Full Name [KrushiSetu Owner]: ").strip() or "KrushiSetu Owner"
    if not phone:
        phone = input("Enter Admin Mobile Number (10 digits) [optional]: ").strip()
    if not password:
        password = getpass.getpass("Enter Admin Password (min 8 chars): ").strip()
        confirm = getpass.getpass("Confirm Admin Password: ").strip()
        if password != confirm:
            print("[ERROR] Passwords do not match.")
            sys.exit(1)

    create_or_update_admin(email=email, password=password, full_name=name, phone=phone)

if __name__ == "__main__":
    main()
