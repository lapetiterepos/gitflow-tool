from __future__ import annotations
from settings import config, errors
from settings.logger import get_logger
from app.gitlab.pipeline import Pipeline
from app.gitlab.branch import Branch
from app.gitlab.mr import Mr
from app.gitlab.tag import Tag
from app.gitlab.milestone import Milestone
import time
import gitlab


log = get_logger(__name__)


class Project:
    def __init__(
        self,
    ) -> None:
        self.name = config.gitlab.project
        self.bot_id = config.gitlab.bot_id
        self.bot_token = config.gitlab.bot_token
        gitlab_url = config.gitlab.proto + "://" + config.gitlab.host
        glab = gitlab.Gitlab(url=gitlab_url, oauth_token=self.bot_token)
        if config.logger.level.upper() == "DEBUG":
            glab.enable_debug(mask_credentials=True)
        self.url = gitlab_url + "/" + self.name
        self.obj = glab.projects.get(self.name)
        self.latest_tag = self.get_latest_tag()
        self.master = self.get_branch(
            name=config.gitlab.master_name,
            tag=self.latest_tag,
            ref=config.gitlab.master_name,
        )
        self.dev = self.get_branch(
            name=config.gitlab.dev_name,
            tag=self.latest_tag,
            ref=config.gitlab.dev_name,
        )

    def __str__(self) -> str:
        return f"Gitlab Project: {self.name}\nLatest Tag: {self.latest_tag}"

    def __repr__(self) -> str:
        return self.__str__()

    def create_tag(
        self,
        tag: Tag,
        ref: str,
    ) -> None:
        if self.check_tag_exists(tag):
            return
        try:
            self.obj.tags.create(
                {
                    "tag_name": str(tag),
                    "ref": ref,
                    "message": tag.message,
                }
            )
        except Exception as e:
            raise errors.GitlabTagError(f"Failed to create {tag} tag") from e

    def get_latest_tag(self) -> Tag:
        try:
            repo_tags = self.obj.tags.list(
                order_by="updated",
                sort="desc",
                get_all=config.gitlab.get_all_tags,
            )
        except Exception as e:
            raise errors.GitlabTagError("Failed to retrieve tags list") from e
        tag_list = []
        for repo_tag in repo_tags:
            tag = Tag.parse(repo_tag.name)
            tag.update_timestamp(repo_tag.commit["created_at"])
            tag_list += [tag]
        tag_list = sorted(tag_list)
        return tag_list[-1]

    def check_tag_exists(self, check_tag: Tag) -> bool:
        try:
            repo_tags = self.obj.tags.list(
                get_all=config.gitlab.get_all_tags,
            )
        except Exception as e:
            raise errors.GitlabTagError("Failed to retrieve tags list") from e
        tag_list = []
        for repo_tag in repo_tags:
            tag = Tag.parse(repo_tag.name)
            tag.update_timestamp(repo_tag.commit["created_at"])
            tag_list += [tag]
        if check_tag not in tag_list:
            return False
        return True

    def create_branch(
        self,
        name: str,
        tag: Tag,
        ref: str,
    ) -> Branch:
        try:
            exist = self.get_branch(name, tag, ref)
            if exist:
                return exist
        except errors.GitlabBranchError:
            pass
        try:
            obj = self.obj.branches.create({"branch": name, "ref": ref})
        except Exception as e:
            raise errors.GitlabBranchError(f"Failed to create branch '{name}'") from e
        return Branch(name, tag, ref, obj, self)

    def get_branch(
        self,
        name: str,
        tag: Tag,
        ref: str,
    ) -> Branch:
        try:
            obj = self.obj.branches.get(name)
        except Exception as e:
            raise errors.GitlabBranchError(f"Failed to get {name} branch") from e
        return Branch(name, tag, ref, obj, self)

    def create_milestone(self, title: str) -> Milestone:
        exist = self.get_milestone_by_title(title)
        if exist:
            return exist
        try:
            milestone = self.obj.milestones.create(
                {
                    "title": title,
                }
            )
        except Exception as e:
            raise errors.GitlabMilestoneError(
                f"Failed to create {title} milestone"
            ) from e
        log.info(f"Milestone for {title} created", url=milestone.web_url)
        return Milestone(milestone)

    def get_milestone(self, milestone_id: str) -> Milestone:
        try:
            milestone = self.obj.milestones.get(id=milestone_id)
        except Exception as e:
            raise errors.GitlabMilestoneError(
                f"Failed to get milestone with milestone_id={milestone_id}"
            ) from e
        return Milestone(milestone)

    def get_milestone_by_title(self, milestone_title: str) -> Milestone | None:
        try:
            milestone = self.obj.milestones.list(title=milestone_title)
        except Exception as e:
            raise errors.GitlabMilestoneError(
                f"Failed to get {milestone_title} milestone"
            ) from e
        if not milestone:
            return None
        return Milestone(milestone[0])

    def create_mr(
        self,
        source: Branch,
        target: Branch,
        milestone: Milestone,
    ) -> Mr:
        title = config.mr.title_template.format(source=source.name, target=target.name)
        assignee = config.mr.assignee
        if not assignee:
            assignee = config.gitlab.bot_id
        exist = self.get_mr(
            source,
            target,
            milestone,
        )
        if exist:
            return exist
        try:
            obj = self.obj.mergerequests.create(
                {
                    "title": title,
                    "source_branch": source.name,
                    "target_branch": target.name,
                    "assignee_id": assignee,
                    "reviewer_ids": config.mr.reviewers,
                    "remove_source_branch": config.mr.rm_source,
                    "squash": config.mr.squash,
                    "labels": config.mr.labels,
                    "milestone_id": milestone.id,
                }
            )
        except Exception as e:
            raise errors.GitlabMrError(
                f"Failed to create from {source.name} to {target.name} merge request"
            ) from e
        return Mr(source, target, obj, self)

    def get_mr(
        self,
        source: Branch,
        target: Branch,
        milestone: Milestone,
    ) -> Mr | None:
        try:
            obj = self.obj.mergerequests.list(
                milestone=milestone.title,
                source_branch=source.name,
                target_branch=target.name,
            )
        except Exception as e:
            raise errors.GitlabMrError(
                f"Failed to get from {source.name} to {target.name} merge request with {milestone.title} milestone"
            ) from e
        if obj:
            return Mr(source, target, obj[0], self)
        return None

    def get_latest_pipeline(self, ref: str) -> Pipeline | None:
        timer = 0
        while timer < config.gitlab.timeout:
            time.sleep(config.gitlab.timewait)
            timer += config.gitlab.timewait
            pipelines = self.obj.pipelines.list(ref=ref)
            if pipelines:
                pipeline = pipelines[0]
                return Pipeline(pipeline, self)
        return None

    def prune_schedule(
        self,
        name: str,
        var_name: str,
    ) -> None:
        name = name.upper()
        schedule_id = None
        try:
            schedules = self.obj.pipelineschedules.list()
            for schedule in schedules:
                if schedule.description == name:
                    schedule_id = str(schedule.id)
        except Exception as e:
            log.warning(f"Failed to get schedule list: {e}")
        if not schedule_id:
            log.warning(f"Failed to get '{name}' pipeline schedule")
        schedule = self.obj.pipelineschedules.get(schedule_id)
        url = f"{self.url}/-/pipeline_schedules/{str(schedule_id)}/edit?id={str(schedule_id)}"
        try:
            schedule.variables.delete(var_name)
        except Exception as e:
            log.warning(
                f"Failed to remove '{var_name}' variable at '{name}' pipeline schedule. Exception: {e}.",
                url=url,
            )
        log.debug(
            f"'{var_name}' variable successfully deleted at '{name}' pipeline schedule",
            url=url,
        )
