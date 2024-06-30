from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "content" (
    "id" VARCHAR(36) NOT NULL  PRIMARY KEY,
    "slug" VARCHAR(500) NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT 'now',
    "description" TEXT NOT NULL,
    "image_id" VARCHAR(36),
    "title" VARCHAR(500) NOT NULL,
    "flagged" BOOL NOT NULL  DEFAULT False,
    "generating" BOOL NOT NULL  DEFAULT True,
    "view_count" INT NOT NULL  DEFAULT 0,
    "hot_score" INT NOT NULL  DEFAULT 0,
    "markdown" TEXT,
    "user_input" TEXT NOT NULL,
    "content" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "contentimage" (
    "id" VARCHAR(36) NOT NULL  PRIMARY KEY,
    "content_id" VARCHAR(36) NOT NULL,
    "prompt_hash" VARCHAR(32) NOT NULL,
    "prompt" TEXT NOT NULL,
    "alt_text" VARCHAR(500) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL,
    "flagged" INT NOT NULL,
    "regenerate" INT NOT NULL,
    "fail_count" INT NOT NULL,
    "generator" VARCHAR(500) NOT NULL,
    "model" VARCHAR(500) NOT NULL,
    "seed" VARCHAR(500) NOT NULL,
    "parameters" VARCHAR(500) NOT NULL,
    "view_count" INT NOT NULL
);
CREATE TABLE IF NOT EXISTS "examples" (
    "id" VARCHAR(36) NOT NULL  PRIMARY KEY,
    "user_input" TEXT NOT NULL,
    "title" VARCHAR(500) NOT NULL,
    "description" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "new_id" INT
);
CREATE TABLE IF NOT EXISTS "imagedata" (
    "id" VARCHAR(36) NOT NULL  PRIMARY KEY,
    "jpeg_data" BYTEA NOT NULL
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
