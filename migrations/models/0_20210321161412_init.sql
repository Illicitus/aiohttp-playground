-- upgrade --
CREATE TABLE IF NOT EXISTS "accounts_user" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(250) NOT NULL,
    "password" TEXT NOT NULL,
    "first_name" TEXT NOT NULL,
    "last_name" TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_accounts_us_email_0afdb2" ON "accounts_user" ("email");
CREATE TABLE IF NOT EXISTS "blog_article" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(250) NOT NULL,
    "body" TEXT NOT NULL,
    "author_id" INT NOT NULL REFERENCES "accounts_user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_blog_articl_title_8186fa" ON "blog_article" ("title");
CREATE TABLE IF NOT EXISTS "blog_article_comment" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "body" TEXT NOT NULL,
    "article_id" INT NOT NULL REFERENCES "blog_article" ("id") ON DELETE CASCADE,
    "author_id" INT NOT NULL REFERENCES "accounts_user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
