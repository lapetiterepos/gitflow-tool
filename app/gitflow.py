from __future__ import annotations
from app.gitlab.milestone import Milestone
from settings import config, errors
from settings.logger import get_logger
from app.helpers import artifacts
from app.gitlab.project import Project
from app.gitlab.branch import Branch
from app.gitlab.tag import Tag
import typing

log = get_logger(__name__)


class Gitflow:

    def __init__(
        self,
    ) -> None:
        self.project = Project()

    def __str__(self) -> str:
        return f"Gitlab Project: {self.project}"

    def __repr__(self) -> str:
        return self.__str__()

    def _get_target_tag(self, increment_func: typing.Callable) -> Tag:
        target_tag = increment_func(self.project.latest_tag)
        raw_target_tag = config.tag.target
        if raw_target_tag:
            target_tag = Tag.parse(raw_target_tag)
        if self.project.check_tag_exists(target_tag):
            raise errors.GitflowError(
                f"Tag '{target_tag}' is already present in the project"
            )
        return target_tag

    def _get_source_tag(self) -> Tag:
        raw_source_tag = config.tag.source
        if not raw_source_tag:
            raise errors.GitflowError("Source tag is empty. Please provide a valid tag")
        source_tag = Tag.parse(
            raw_tag=raw_source_tag,
        )
        if not self.project.check_tag_exists(source_tag):
            raise errors.GitflowError(
                f"Tag '{source_tag}' is not present in the project"
            )
        return source_tag

    def start_release(
        self,
    ):
        target_tag = self._get_target_tag(Tag.increment_minor)
        name = config.release.prefix + str(target_tag)
        ref = config.release.ref
        release = self.project.create_branch(name, target_tag, ref)
        milestone = self.project.create_milestone(release.name)
        artifacts.dump(
            {
                "branch": name,
                "tag": str(target_tag),
                "ref": ref,
                "milestone_id": milestone.id,
            }
        )
        if config.tag.target:
            self.project.prune_schedule(
                name=config.release.schedule,
                var_name=config.Config.env_names.tag.target,
            )
        log.info(f"Release '{target_tag}' has been started", url=release.url)

    def start_hotfix(
        self,
    ):
        target_tag = self._get_target_tag(Tag.increment_patch)
        name = config.hotfix.prefix + str(target_tag)
        ref = config.hotfix.ref
        hotfix = self.project.create_branch(name, target_tag, ref)
        milestone = self.project.create_milestone(hotfix.name)
        artifacts.dump(
            {
                "branch": name,
                "tag": str(target_tag),
                "ref": ref,
                "milestone_id": milestone.id,
            }
        )
        if config.tag.target:
            self.project.prune_schedule(
                name=config.hotfix.schedule,
                var_name=config.Config.env_names.tag.target,
            )
        log.info(f"Hotfix '{target_tag}' has been started", url=hotfix.url)

    def start_support(
        self,
    ):
        source_tag = self._get_source_tag()
        target_tag = Tag.increment_patch(source_tag)
        name = config.support.prefix + str(target_tag)
        if self.project.check_tag_exists(target_tag):
            log.error(f"Failed to start {name}")
            raise errors.GitflowError(
                f"Tag '{target_tag}' is already present in the project"
            )
        ref = self.project.obj.tags.get(source_tag).commit["id"]
        support = self.project.create_branch(name, target_tag, ref)
        milestone = self.project.create_milestone(support.name)
        artifacts.dump(
            {
                "branch": name,
                "tag": str(target_tag),
                "ref": ref,
                "milestone_id": milestone.id,
            }
        )
        if config.tag.source:
            self.project.prune_schedule(
                name=config.support.schedule,
                var_name=config.Config.env_names.tag.source,
            )
        log.info(f"Support '{target_tag}' has been started", url=support.url)

    def _finish(
        self,
        source: Branch,
        milestone: Milestone,
    ) -> None:
        loaded = artifacts.load()
        to_master = self.project.create_mr(
            source=source,
            target=self.project.master,
            milestone=milestone,
        )
        to_master_mergeable = to_master.is_mergeable()
        if not to_master_mergeable:
            raise errors.GitflowError("Failed to finish gitflow")
        to_master.merge()
        source = self.project.get_branch(
            name=loaded.branch,
            tag=Tag.parse(loaded.tag),
            ref=loaded.ref,
        )
        mr = self.project.get_mr(
            source=source,
            target=self.project.master,
            milestone=milestone,
        )
        self.project.create_tag(
            tag=mr.source.tag,
            ref=mr.obj.merge_commit_sha,
        )
        master_to_dev = self.project.create_mr(
            source=self.project.master,
            target=self.project.dev,
            milestone=milestone,
        )
        if not master_to_dev.is_mergeable():
            log.error(
                "Failed to merge 'master' to 'dev' for tag propagation",
                url=master_to_dev.url,
            )
            raise errors.GitflowError()
        master_to_dev.merge()
        milestone.delete()
        log.info(
            f"Tag {mr.source.tag} created and propagated to 'dev' successfully",
            url=self.project.url + "/-/tags/" + str(mr.source.tag),
        )

    def finish_release(
        self,
    ) -> None:
        loaded = artifacts.load()
        release = self.project.get_branch(
            name=loaded.branch,
            tag=Tag.parse(loaded.tag),
            ref=loaded.ref,
        )
        milestone = self.project.get_milestone(loaded.milestone_id)
        self._finish(source=release, milestone=milestone)
        log.info(f"Release '{release.name}' has been finished")

    def finish_hotfix(
        self,
    ) -> None:
        loaded = artifacts.load()
        hotfix = self.project.get_branch(
            name=loaded.branch,
            tag=Tag.parse(loaded.tag),
            ref=loaded.ref,
        )
        milestone = self.project.get_milestone(loaded.milestone_id)
        self._finish(source=hotfix, milestone=milestone)
        log.info(f"Hotfix '{hotfix.name}' has been finished")

    def finish_support(
        self,
    ) -> None:
        loaded = artifacts.load()
        support = self.project.get_branch(
            name=loaded.branch,
            tag=Tag.parse(loaded.tag),
            ref=loaded.ref,
        )
        milestone = self.project.get_milestone(loaded.milestone_id)
        self._finish(source=support, milestone=milestone)
        log.info(f"Support '{support.name}' has been finished")
