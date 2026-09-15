from datetime import datetime
from html import escape

SENDER = "Ahmad Waseem's Script"

SUBJECT = "SMTP Notification Email 📨"

def build_bodies(status: str) -> tuple[str, str]:
    checked_in = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_body = f"""\
<html>
  <body style="font-family: Arial, Helvetica, sans-serif; font-size: 14px; color: #222222;">

    <p style="margin: 0 0 12px 0;">
      This is an SMTP notification message ⚡
    </p>

    <p style="margin: 0 0 12px 0; line-height: 1.5;">
      This text will have information on whether your script has completed
      or an event has occurred on your server.
    </p>

    <p style="margin: 0 0 12px 0; line-height: 1.5;">
      Status: <b>{escape(status)}</b><br>
      Last check-in: <b>{checked_in}</b>
    </p>

    <p style="margin: 16px 0 0 0; font-size: 12px; color: #777777;">
      Sent automatically. No reply needed.
    </p>
  </body>
</html>
"""

    text_body = f"""\
This is an SMTP notification message.

This text will have information on whether your script has completed
or an event has occurred on your server.

Status: {status}
Last check-in: {checked_in}

Sent automatically. No reply needed.
"""

    return html_body, text_body
