from __future__ import annotations
from settings.logger import get_logger
from app.helpers import type
import gitlab

log = get_logger(__name__)


class Pipeline:
    def __init__(
        self,
        obj: gitlab.v4.objects.ProjectPipeline,
        project: type.Project,
    ) -> None:
        self.url = obj.web_url
        self.obj = obj
        self.project = project


def get_schedule_id(project: gitlab.v4.objects.Project, name: str) -> str:
    schedules = project.pipelineschedules.list()
    for schedule in schedules:
        if schedule.description == name:
            return str(schedule.id)
    return ""


def skip_for_mr(mr: type.Mr) -> None:
    pipeline = mr.project.get_latest_pipeline(ref=f"refs/merge-requests/{mr.iid}/head")
    if pipeline:
        try:
            pipeline.obj.cancel()
        except Exception as e:
            log.debug(
                f"Failed to cancel Mr '{mr.title}' pipeline. Exception: {e}",
                url=pipeline.url,
            )
        log.debug(f"Mr '{mr.title}' pipeline canceled.", url=pipeline.url)
    log.debug(f"Failed to get Mr '{mr.title}' pipeline.")
