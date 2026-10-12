import strawberry
import typing
from typing import Optional

from scenarios.query_complexity.fixtures import USERS, POSTS, COMMENTS


@strawberry.type
class Comment:
    id: strawberry.ID
    content: str

    @strawberry.field
    def author(self) -> Optional["User"]:
        from scenarios.query_complexity.fixtures import COMMENTS as C
        record = C.get(str(self.id))
        if not record:
            return None
        return _make_user(record["author_id"])


@strawberry.type
class Post:
    id: strawberry.ID
    title: str
    content: str

    @strawberry.field
    def author(self) -> Optional["User"]:
        record = POSTS.get(str(self.id))
        if not record:
            return None
        return _make_user(record["author_id"])

    @strawberry.field
    def comments(self) -> typing.List[Comment]:
        record = POSTS.get(str(self.id))
        if not record:
            return []
        return [
            Comment(id=cid, content=COMMENTS[cid]["content"])
            for cid in record["comment_ids"]
            if cid in COMMENTS
        ]


@strawberry.type
class User:
    id: strawberry.ID
    name: str

    @strawberry.field
    def posts(self) -> typing.List[Post]:
        record = USERS.get(str(self.id))
        if not record:
            return []
        return [Post(id=pid, title=POSTS[pid]["title"], content=POSTS[pid]["content"]) for pid in record["post_ids"] if pid in POSTS]

    @strawberry.field
    def friends(self) -> typing.List["User"]:
        record = USERS.get(str(self.id))
        if not record:
            return []
        return [_make_user(fid) for fid in record["friend_ids"]]


def _make_user(uid: str) -> User:
    r = USERS.get(str(uid))
    if not r:
        return User(id=uid, name="Unknown")
    return User(id=r["id"], name=r["name"])


@strawberry.type
class Query:
    @strawberry.field(description="All users with nested relationships")
    def users(self) -> typing.List[User]:
        return [_make_user(uid) for uid in USERS]


vulnerable_schema = strawberry.Schema(query=Query)
