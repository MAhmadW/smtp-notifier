import atexit
import logging
import math
import smtplib as mail
from email.message import EmailMessage
from email.utils import formataddr
from enum import IntEnum
from itertools import count
from queue import PriorityQueue
from ssl import create_default_context
from threading import Thread, Event

from pydantic import BaseModel
from typing import List
from config import settings

logger = logging.getLogger(__name__)

class Priority(IntEnum):
    # Lower values are sent first. IntEnum keeps members comparable inside the PriorityQueue
    HIGH = 1
    MEDIUM = 2
    LOW = 3

class Notification(BaseModel):
    sender: str
    subject: str
    content: str | None = None
    plain_content: str
    recipients: List[str] = []

class NotificationHandle():
    error: Exception | None

    def __init__(self):
        self._done = Event()
        self.error = None

        return

    def _finish(self, error: Exception | None = None):
        self.error = error
        self._done.set()

        return

    def wait(self, timeout: float | None = None):
        if not self._done.wait(timeout):
            raise TimeoutError(f'Notification was not sent within {timeout} seconds')

        if self.error is not None:
            raise self.error

        return

class Notifier():
    _queue: PriorityQueue

    def __init__(self):
        self._queue = PriorityQueue()
        self._seq = count()
        self._ssl_context = create_default_context()

        self._thread = Thread(target=self._run, daemon= True)
        self._thread.start()

        # Send anything still queued before the interpreter exits
        atexit.register(self.stop)

        return

    def _build_message(self, notification: Notification) -> EmailMessage:
        message = EmailMessage()
        message['Subject'] = notification.subject
        message['From'] = formataddr((notification.sender, settings.account_email))
        message['To'] = ', '.join(notification.recipients) if len(notification.recipients) else settings.account_email

        message.set_content(notification.plain_content)
        if (notification.content):
            message.add_alternative(notification.content, subtype="html")

        return message

    def _send_notification(self, notification: Notification):
        message = self._build_message(notification)

        # A fresh connection per send, since servers drop idle ones
        with mail.SMTP_SSL(settings.provider_domain, settings.provider_port, context=self._ssl_context, timeout=30) as client:
            client.login(settings.account_email, settings.account_password.get_secret_value())
            client.send_message(message)

        logger.info('Sent notification: %s', notification.subject)

        return

    def _run(self):
        while(True):
            priority, _, notification, handle = self._queue.get()

            # Only stop() queues a task without a handle
            if handle is None:
                break

            try:
                self._send_notification(notification)
                handle._finish()
            except Exception as error:
                logger.exception('Error sending notification')
                handle._finish(error)

        return

    def notify(self, notification: Notification, priority: Priority = Priority.MEDIUM, timeout: float | None = 60):
        self.enqueue_notification(notification, priority).wait(timeout)

        return

    def enqueue_notification(self, notification: Notification, priority: Priority = Priority.MEDIUM) -> NotificationHandle:
        if not self._thread.is_alive():
            raise RuntimeError('Notifier has been stopped')

        priority = Priority(priority)

        # Higher priorities are sent first. The sequence number keeps equal priorities in FIFO order
        handle = NotificationHandle()
        self._queue.put((priority, next(self._seq), notification, handle))

        return handle

    def stop(self):
        if not self._thread.is_alive():
            return

        # Same shape as a real task, with infinite priority so everything already queued is sent first
        self._queue.put((math.inf, next(self._seq), None, None))
        self._thread.join()

        return
