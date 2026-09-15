import logging

from notifier import Notifier, Notification, Priority
from config import settings
from message import SUBJECT, SENDER, build_bodies

def main():
    logging.basicConfig(level=logging.INFO)

    notifier_client = Notifier()
    html_body, text_body = build_bodies(status= 'running')
    # You may omit recipients entirely if the intention is to email yourself - perhaps a notification on your phone is all you need
    ping = Notification(sender= SENDER, subject= SUBJECT, content=html_body, plain_content=text_body, recipients=[settings.target_email])

    ## Use one of the patterns below:

    # 1
    handle = notifier_client.enqueue_notification(ping, Priority.HIGH)
    handle.wait(timeout=60) # blocks until the notification goes through, raises if it failed or timed out

    # 2
    # notifier_client.notify(ping)

    # 3
    # Fire-and-forget also works in scripts, since anything still queued is sent before the interpreter exits
    # notifier_client.enqueue_notification(ping, Priority.LOW)

    # In web services like FastAPI, create one Notifier per worker process (uvicorn --workers N starts N separate processes),
    # ideally in the app's lifespan, and don't block on handle.wait() inside async endpoints

if __name__ == "__main__":
    main()
