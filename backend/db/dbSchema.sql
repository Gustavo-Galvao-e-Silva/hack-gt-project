CREATE TABLE public."Node"
(
    "nodeID" integer NOT NULL,
    title text NOT NULL,
    "connectedTitles" text[],
    description text,
    "connectedIDs" integer[],
    "workspaceID" integer NOT NULL,
    "keywords" text[],
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
    "workspacesID" integer NOT NULL,
    "userID" integer NOT NULL,
    title text,
    description text,
    PRIMARY KEY ("workspacesID")
);

ALTER TABLE IF EXISTS public."Workspaces"
    OWNER to postgres;

ALTER TABLE IF EXISTS public."Node"
    ADD CONSTRAINT "FK_to_Workspaces" FOREIGN KEY ("workspaceID")
    REFERENCES public."Workspaces" ("workspacesID") MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE
    NOT VALID;

ALTER TABLE IF EXISTS public."Workspaces"
    ADD CONSTRAINT "FK_to_Users" FOREIGN KEY ("userID")
    REFERENCES public."Users" ("userID") MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;