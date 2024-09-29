from app.gitlab import branch, mr, pipeline, project, tag, milestone
from app.helpers import artifacts, common
from app import cli, gitflow

type Branch = type(branch.Branch)
type Mr = type(mr.Mr)
type Pipeline = type(pipeline.Pipeline)
type Project = type(project.Project)
type Tag = type(tag.Tag)
type DotDict = type(common.DotDict)
type Cli = type(cli.Cli)
type Gitflow = type(gitflow.Gitflow)
type Milestone = type(milestone.Milestone)
