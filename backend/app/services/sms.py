import logging
from typing import Optional
from app.utils.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


def send_sms(to_phone: str, message: str) -> dict:
    if settings.sms_provider == "africas_talking":
        return _send_africas_talking(to_phone, message)
    elif settings.sms_provider == "twilio":
        return _send_twilio(to_phone, message)
    else:
        logger.warning("No SMS provider configured. SMS not sent to %s", to_phone)
        return {"status": "simulated", "to": to_phone, "message": message}


def _send_africas_talking(to_phone: str, message: str) -> dict:
    try:
        import africastalking

        africastalking.initialize(
            username=settings.sms_username or "sandbox",
            api_key=settings.sms_api_key or ""
        )
        sms = africastalking.SMS
        response = sms.send(
            message=message,
            recipients=[to_phone],
            sender_id=settings.sms_sender_id or None
        )
        logger.info("Africa's Talking SMS sent to %s: %s", to_phone, response)
        return {"status": "sent", "provider": "africas_talking", "response": response}
    except ImportError:
        logger.warning("africastalking SDK not installed. Simulating send.")
        return {"status": "simulated", "provider": "africas_talking", "to": to_phone, "message": message}
    except Exception as e:
        logger.error("Failed to send SMS via Africa's Talking: %s", str(e))
        return {"status": "failed", "provider": "africas_talking", "error": str(e)}


def _send_twilio(to_phone: str, message: str) -> dict:
    try:
        from twilio.rest import Client

        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            logger.warning("Twilio credentials not configured. Simulating send.")
            return {"status": "simulated", "provider": "twilio", "to": to_phone, "message": message}

        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        twilio_msg = client.messages.create(
            body=message,
            from_=settings.twilio_phone_number,
            to=to_phone
        )
        logger.info("Twilio SMS sent to %s: SID=%s", to_phone, twilio_msg.sid)
        return {"status": "sent", "provider": "twilio", "sid": twilio_msg.sid}
    except ImportError:
        logger.warning("twilio SDK not installed. Simulating send.")
        return {"status": "simulated", "provider": "twilio", "to": to_phone, "message": message}
    except Exception as e:
        logger.error("Failed to send SMS via Twilio: %s", str(e))
        return {"status": "failed", "provider": "twilio", "error": str(e)}


def format_alert_sms(alert_title: str, alert_message: str, severity: str) -> str:
    severity_emoji = {"low": "ℹ️", "moderate": "⚠️", "high": "🔴", "critical": "🚨"}
    emoji = severity_emoji.get(severity, "⚠️")
    parts = [
        f"{emoji} ALERT: {alert_title}",
        alert_message[:280],
        "Reply to this SMS to report what you see."
    ]
    return "\n".join(parts)


def broadcast_alert(phone_numbers: list, title: str, message: str, severity: str) -> list:
    results = []
    formatted = format_alert_sms(title, message, severity)
    for phone in phone_numbers:
        result = send_sms(phone, formatted)
        results.append(result)
    return results
