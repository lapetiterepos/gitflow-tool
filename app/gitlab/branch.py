from __future__ import annotations
from app.helpers import type
import gitlab


class Branch:
    def __init__(
        self,
        name: str,
        tag: type.Tag,
        ref: str,
        obj: gitlab.v4.objects.ProjectBranch,
        project: type.Project,
    ) -> None:
        self.name = name
        self.tag = tag
        self.ref = ref
        self.obj = obj
        self.url = obj.web_url
        self.project = project
