from __future__ import annotations
from settings.logger import get_logger
import gitlab

log = get_logger(__name__)


class Milestone:
    def __init__(self, obj: gitlab.v4.objects.Milestone) -> None:
        self.obj = obj
        self.id = obj.id
        self.title = obj.title
        self.url = obj.web_url

    def close(self):
        try:
            self.obj.state_event = "close"
            self.obj.save()
        except Exception as e:
            log.warning(f"Failed to close {self.title} milestone. Exception: {e}")
        log.info(f"Milestone {self.title} has been closed", url=self.url)

    def delete(self):
        try:
            self.obj.delete()
        except Exception as e:
            log.warning(f"Failed to delete {self.title} milestone. Exception: {e}")
        log.info(f"Milestone {self.title} has been deleted", url=self.url)
