CREATE TABLE pictures (
    id      VARCHAR(36),
    path    VARCHAR(255) NOT NULL,
    size    INT(11) NOT NULL,
    date    VARCHAR(19) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE tags (
    tag         VARCHAR(50),
    picture_id  VARCHAR(36),
    confidence  FLOAT(7,4) NOT NULL,
    date        VARCHAR(19) NOT NULL,
    PRIMARY KEY (tag, picture_id),
    FOREIGN KEY (picture_id) REFERENCES pictures(id)
)