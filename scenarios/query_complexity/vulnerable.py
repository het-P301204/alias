import strawberry
from typing import Optional


@strawberry.type
class Author:
    id: strawberry.ID
    name: str


@strawberry.type
class Comment:
    id: strawberry.ID
    content: str
    author: Author


@strawberry.type
class Post:
    id: strawberry.ID
    title: str

    @strawberry.field
    def comments(self) -> list[Comment]:
        return [
            Comment(id="c1", content="First comment", author=Author(id="2", name="User2")),
            Comment(id="c2", content="Second comment", author=Author(id="3", name="User3")),
        ]


@strawberry.type
class User:
    id: strawberry.ID
    name: str

    @strawberry.field
    def posts(self) -> list[Post]:
        return [
            Post(id=f"p{self.id}1", title=f"Post 1 by {self.name}"),
            Post(id=f"p{self.id}2", title=f"Post 2 by {self.name}"),
        ]


@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> list[User]:
        return [
            User(id="1", name="Alice"),
            User(id="2", name="Bob"),
        ]

    @strawberry.field
    def user(self, id: strawberry.ID) -> Optional[User]:
        users = {"1": User(id="1", name="Alice"), "2": User(id="2", name="Bob")}
        return users.get(str(id))


# Vulnerable: no depth or complexity limits
vulnerable_schema = strawberry.Schema(query=Query)
