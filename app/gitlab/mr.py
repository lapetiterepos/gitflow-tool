from __future__ import annotations
from settings import config, errors
from settings.logger import get_logger
from app.helpers import type
from app.gitlab import pipeline
import gitlab
import time

log = get_logger(__name__)


class Mr:
    def __init__(
        self,
        source: type.Branch,
        target: type.Branch,
        obj: gitlab.v4.objects.MergeRequest,
        project: type.Project,
    ) -> None:
        self.source = source
        self.target = target
        self.project = project
        self.obj = obj
        self.iid = self.obj.iid
        self.url = self.obj.web_url
        self.title = config.mr.title_template.format(
            source=f"'{source.name}'",
            target=f"'{target.name}'",
        )
        self.msg = config.mr.msg_template.format(
            source=f"'{source.name}'",
            target=f"'{target.name}'",
        )

    def refresh(self) -> None:
        try:
            self.obj = self.project.obj.mergerequests.get(id=self.iid)
        except Exception as e:
            log.debug(f"Failed to refresh {self.title} status: {e}")

    def is_mergeable(self) -> bool:
        self.refresh()
        fail = f"'{self.title}' is NOT ready to merge. Reason: "
        if self.obj.has_conflicts:
            log.error(fail + "Mr has conflicts.", url=self.url)
            return False
        if config.mr.skip_ci == "true":
            pipeline.skip_for_mr(mr=self)
        timer = 0
        while timer < config.gitlab.timeout:
            time.sleep(config.gitlab.timewait)
            timer += config.gitlab.timewait
            self.refresh()
            mr_status = self.obj.detailed_merge_status
            match mr_status:
                case "mergeable":
                    log.debug(f"'{self.title}' is ready to merge.")
                    return True
                case "not_open":
                    log.debug(f"'{self.title}' is already merged.")
                    return True
                case "blocked_status" | "conflict" | "not_approved" | "broken_status":
                    log.error(fail + f"Mr status: '{mr_status}'.", url=self.url)
                    return False
                case "checking" | "unchecked" | "preparing":
                    log.debug("Waiting while merge request is ready...")
                case "ci_must_pass" | "ci_still_running":
                    log.debug("Merge request CI still running...")
                case _:
                    log.error(
                        fail + f"Unexpected Mr status: '{mr_status}'.", url=self.url
                    )
                    return False
        self.refresh()
        mr_status = self.obj.detailed_merge_status
        log.error(
            fail + f"Timeout exceeded. Last Mr status: '{mr_status}'.",
            url=self.url,
        )
        return False

    def merge(self) -> None:
        fail = f"'{self.title}' failed."
        mr_request = self.project.obj.mergerequests.get(id=self.iid)
        if mr_request.state == "merged":
            return
        try:
            self.obj.merge(merge_commit_message=f"{self.msg}")
        except Exception as e:
            log.error(fail, url=self.url)
            raise errors.GitlabMrError() from e
        timer = 0
        while timer < config.gitlab.timeout:
            time.sleep(config.gitlab.timewait)
            timer += config.gitlab.timewait
            mr_request = self.project.obj.mergerequests.get(id=self.iid)
            if mr_request.state == "merged":
                log.info(f"'{self.title}' merged.", url=self.url)
                return
        mr_request = self.project.obj.mergerequests.get(id=self.iid)
        log.error(
            f"'{self.title}' failed. Mr state: '{mr_request.state}'. Mr status: '{mr_request.status}'.",
            url=self.url,
        )
        raise errors.GitlabMrError("Timeout exceeded.")
