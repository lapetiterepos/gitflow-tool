import json
from settings import config, errors
from app.helpers.common import DotDict
from datetime import datetime, timezone


def dump(artifacts: dict) -> None:
    iso_timestamp = (
        datetime.now(timezone.utc)
        .astimezone()
        .isoformat(sep="T", timespec="milliseconds")
    )
    artifacts.update(
        {
            "timestamp": iso_timestamp,
        }
    )
    try:
        with open(config.artifacts.path, "w") as artifacts_file:
            json.dump(artifacts, artifacts_file)
    except Exception as e:
        raise errors.HelpersArtifactsError() from e


def load() -> DotDict:
    try:
        with open(config.artifacts.path, "r") as artifacts_file:
            artifacts = json.load(artifacts_file)
            return DotDict(artifacts)
    except Exception as e:
        raise errors.HelpersArtifactsError() from e
