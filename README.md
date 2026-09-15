# SMTP Notifier

Email yourself from scripts and web services through Gmail's SMTP server. The Gmail app on your phone turns each email into a push notification, so there's no paid service or extra infrastructure.

- Sends from a background thread, so queuing a notification never blocks.
- Opens a fresh, certificate-verified TLS connection for every send.
- `HIGH`, `MEDIUM` (default) and `LOW` priorities, with equal priorities sent in the order they were queued.
- Failed sends are logged and raised from `notify()` and `handle.wait()`.

## Setup

1. **Turn on 2-Step Verification** for the Gmail account that will send the emails, at [myaccount.google.com/signinoptions/two-step-verification](https://myaccount.google.com/signinoptions/two-step-verification) (Google Account → Security & sign-in → 2-Step Verification). App passwords require it.
2. **Create an app password** at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords). Enter any name, like `smtp-notifier`, and click **Create**, then copy the 16-character code without the spaces. Google shows the code only once, and revokes it if you change your Google password.
   - If the page says the setting isn't available, 2-Step Verification is off or uses only security keys, or the account is a work, school or Advanced Protection account.
3. **Configure:** run `cp example.env .env` and fill in:
   - `SMTP_ACCOUNT_EMAIL`: the sending Gmail address
   - `SMTP_ACCOUNT_PASSWORD`: the app password
   - `SMTP_TARGET_EMAIL`: the inbox you want notifications in, e.g. your personal Gmail

   The server settings are already filled in for Gmail.
4. **Send a test:** `uv sync && uv run main.py`

An app password gives full access to its mailbox, so sending from a separate Gmail account is safer than using your main one.

## Usage

```python
from notifier import Notifier, Notification, Priority

notifier = Notifier()
done = Notification(
    sender="Nightly Backfill",  # display name on the notification
    subject="Backfill finished ✅",
    plain_content="Processed 1.2M rows in 14m",  # content="<p>...</p>" adds an HTML version
)

notifier.notify(done)  # waits for the send (60s timeout) and raises if it fails

handle = notifier.enqueue_notification(done, Priority.HIGH)  # returns immediately
handle.wait(timeout=30)  # optional: queued sends still go out before the script exits
```

- **Priority** only matters when notifications queue up, such as a burst while an email is still sending.
- **Recipients** default to the sending account itself. To notify your main inbox, pass `recipients=[settings.target_email]` (`from config import settings`).
- **Web services** like FastAPI: create one `Notifier` per worker process in the app's lifespan, and don't call `handle.wait()` inside `async` endpoints.

## Tips and limits

- Add a Gmail filter for the sender with **Never send it to Spam**, **Always mark it as important** and **Categorize as: Primary**, so notifications still arrive when your phone is set to "Primary only" or "High priority only".
- Gmail caps daily sends. This is for notifying yourself, not for customer-facing email.
- Some cloud hosts block outbound SMTP ports.
