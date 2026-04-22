def mock_lead_capture(name: str, email: str, platform: str) -> dict:
    """
    Mock API function to capture lead information.
    In real world, this would send data to a CRM like HubSpot or Salesforce.
    """
    print("\n" + "="*50)
    print("✅  LEAD CAPTURED SUCCESSFULLY!")
    print("="*50)
    print(f"  Name     : {name}")
    print(f"  Email    : {email}")
    print(f"  Platform : {platform}")
    print("="*50 + "\n")

    return {
        "status": "success",
        "message": "Lead captured successfully",
        "lead": {
            "name": name,
            "email": email,
            "platform": platform
        }
    }


def validate_email(email: str) -> bool:
    """Basic email validation"""
    return "@" in email and "." in email


def validate_name(name: str) -> bool:
    """Basic name validation"""
    return len(name.strip()) >= 2


def validate_platform(platform: str) -> bool:
    """Check if platform is valid"""
    valid_platforms = ["youtube", "instagram", "tiktok", "twitter", "facebook", "linkedin", "other"]
    return any(p in platform.lower() for p in valid_platforms)