from __future__ import annotations
from settings import config, errors
from datetime import datetime, timezone
import semver
import re


class Tag:

    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        prefix: str,
        postfix: str,
        timestamp: str = None,
    ) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.version = f"{major}.{minor}.{patch}"
        self.prefix = prefix
        self.postfix = postfix
        self.message = config.tag.message_template.format(tag=str(self))
        if not timestamp:
            timestamp = (
                datetime.now(timezone.utc)
                .astimezone()
                .isoformat(sep="T", timespec="milliseconds")
            )
        self.timestamp = datetime.fromisoformat(timestamp)

    def __str__(self) -> str:
        return f"{self.prefix}{self.version}{self.postfix}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other) -> bool:
        comp = semver.compare(self.version, other.version)
        if comp == 0 and self.prefix == other.prefix and self.postfix == other.postfix:
            return True
        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other) -> bool:
        comp = semver.compare(self.version, other.version)
        if comp == -1:
            return True
        if comp == 0 and (self.prefix != other.prefix or self.postfix != other.postfix):
            return self.timestamp < other.timestamp
        return False

    def __le__(self, other) -> bool:
        if self == other:
            return True
        return self < other

    def __gt__(self, other) -> bool:
        comp = semver.compare(self.version, other.version)
        if comp == 1:
            return True
        if comp == 0 and (self.prefix != other.prefix or self.postfix != other.postfix):
            return self.timestamp > other.timestamp
        return False

    def __ge__(self, other) -> bool:
        if self == other:
            return True
        return self > other

    @staticmethod
    def parse(raw_tag: str) -> Tag:
        match = re.match(config.tag.regexp, raw_tag)
        if not match:
            raise errors.GitlabTagError(f"Invalid tag: {raw_tag}")
        prefix = match.group("prefix")
        postfix = match.group("postfix")
        raw_version = match.group("version")
        major, minor, patch = Tag._parse_semver(raw_version)
        return Tag(major, minor, patch, prefix, postfix)

    def update_timestamp(self, timestamp: str) -> None:
        self.timestamp = timestamp

    @staticmethod
    def _parse_semver(raw_version: str) -> tuple[int, int, int]:
        match = re.match(config.tag.semver_regexp, raw_version)
        if not match:
            raise errors.GitlabTagError(f"Invalid version: {raw_version}")
        major = int(match.group("major"))
        minor = int(match.group("minor"))
        patch = int(match.group("patch"))
        return major, minor, patch

    @staticmethod
    def increment_major(source: Tag) -> Tag:
        target_major = source.major + 1
        target_minor = 0
        target_patch = 0
        return Tag(
            target_major,
            target_minor,
            target_patch,
            source.prefix,
            source.postfix,
        )

    @staticmethod
    def increment_minor(source: Tag) -> Tag:
        target_minor = source.minor + 1
        target_patch = 0
        return Tag(
            source.major,
            target_minor,
            target_patch,
            source.prefix,
            source.postfix,
        )

    @staticmethod
    def increment_patch(source: Tag) -> Tag:
        target_patch = source.patch + 1
        return Tag(
            source.major,
            source.minor,
            target_patch,
            source.prefix,
            source.postfix,
        )
