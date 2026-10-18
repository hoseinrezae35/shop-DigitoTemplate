import requests

from django.conf import settings


class ZarinPalError(Exception):
    pass


class ZarinPalService:

    def __init__(self):
        self.merchant_id = settings.ZARINPAL_MERCHANT_ID
        self.request_url = settings.ZARINPAL_REQUEST_URL
        self.verify_url = settings.ZARINPAL_VERIFY_URL
        self.startpay_url = settings.ZARINPAL_STARTPAY_URL

        if not self.merchant_id:
            raise ZarinPalError(
                "Merchant ID زرین‌پال تنظیم نشده است."
            )

    def request_payment(
        self,
        *,
        amount,
        callback_url,
        description,
        mobile=None,
        email=None,
    ):
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "callback_url": callback_url,
            "description": description,
            "metadata": {},
        }

        if mobile:
            payload["metadata"]["mobile"] = mobile

        if email:
            payload["metadata"]["email"] = email

        try:
            response = requests.post(
                self.request_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=15,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise ZarinPalError(
                "ارتباط با زرین‌پال برقرار نشد."
            ) from exc

        try:
            data = response.json()

        except ValueError as exc:
            raise ZarinPalError(
                "پاسخ نامعتبر از زرین‌پال دریافت شد."
            ) from exc

        result = data.get("data") or {}
        errors = data.get("errors") or {}

        code = result.get("code")

        if code != 100:
            raise ZarinPalError(
                errors.get("message")
                or result.get("message")
                or "درخواست پرداخت توسط زرین‌پال پذیرفته نشد."
            )

        authority = result.get("authority")

        if not authority:
            raise ZarinPalError(
                "Authority از زرین‌پال دریافت نشد."
            )

        return {
            "authority": authority,
            "payment_url": f"{self.startpay_url}{authority}",
        }

    def verify_payment(
        self,
        *,
        amount,
        authority,
    ):
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "authority": authority,
        }

        try:
            response = requests.post(
                self.verify_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=15,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise ZarinPalError(
                "ارتباط با زرین‌پال برای تأیید پرداخت برقرار نشد."
            ) from exc

        try:
            data = response.json()

        except ValueError as exc:
            raise ZarinPalError(
                "پاسخ نامعتبر از زرین‌پال دریافت شد."
            ) from exc

        result = data.get("data") or {}
        errors = data.get("errors") or {}

        code = result.get("code")

        if code in (100, 101):
            return {
                "success": True,
                "code": code,
                "ref_id": result.get("ref_id"),
                "card_pan": result.get("card_pan"),
                "card_hash": result.get("card_hash"),
            }

        return {
            "success": False,
            "code": code or errors.get("code"),
            "message": (
                errors.get("message")
                or result.get("message")
                or "پرداخت تأیید نشد."
            ),
        }