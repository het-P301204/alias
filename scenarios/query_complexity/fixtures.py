from typing import TypedDict


class CommentRecord(TypedDict):
    id: str
    content: str
    author_id: str


class PostRecord(TypedDict):
    id: str
    title: str
    content: str
    author_id: str
    comment_ids: list[str]


class UserRecord(TypedDict):
    id: str
    name: str
    friend_ids: list[str]
    post_ids: list[str]


COMMENTS: dict[str, CommentRecord] = {
    f"c{u}{p}{c}": {"id": f"c{u}{p}{c}", "content": f"Comment {c} on post {p}", "author_id": str((int(c) % 3) + 1)}
    for u in range(1, 4) for p in range(1, 4) for c in range(1, 4)
}

POSTS: dict[str, PostRecord] = {
    f"p{u}{p}": {
        "id": f"p{u}{p}",
        "title": f"Post {p} by user {u}",
        "content": f"Content of post {p}",
        "author_id": str(u),
        "comment_ids": [f"c{u}{p}{c}" for c in range(1, 4)],
    }
    for u in range(1, 4) for p in range(1, 4)
}

USERS: dict[str, UserRecord] = {
    str(u): {
        "id": str(u),
        "name": f"User{u}",
        "friend_ids": [str(i) for i in range(1, 4) if i != u],
        "post_ids": [f"p{u}{p}" for p in range(1, 4)],
    }
    for u in range(1, 4)
}
