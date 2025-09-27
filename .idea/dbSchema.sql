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