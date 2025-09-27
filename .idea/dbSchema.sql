CREATE TABLE public."Node"
(
    "nodeID" integer NOT NULL,
    title text NOT NULL,
    "connectedTitles" text[],
    description text,
    "connectedIDs" integer[],
    "workspaceID" integer NOT NULL,
    PRIMARY KEY ("nodeID")
);

ALTER TABLE IF EXISTS public."Node"
    OWNER to postgres;

CREATE TABLE public."Users"
(
    "userID" integer NOT NULL,
    username text NOT NULL,
    PRIMARY KEY ("userID")
);

ALTER TABLE IF EXISTS public."Users"
    OWNER to postgres;

CREATE TABLE public."Workspaces"
(
    "workspaceID" integer NOT NULL,
    "userID" integer NOT NULL,
    PRIMARY KEY ("workspaceID")
);

ALTER TABLE IF EXISTS public."Workspaces"
    OWNER to postgres;