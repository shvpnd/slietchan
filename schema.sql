CREATE TABLE posts (
    post_id INTEGER PRIMARY KEY,
    image_file TEXT,
    user TEXT,
    date TEXT,
    board TEXT NOT NULL,
    post_text TEXT
);

CREATE TABLE boards (
    board_id INTEGER PRIMARY KEY,
    board_short_name TEXT NOT NULL UNIQUE,
    board_description TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE replies (
    reply_id INTEGER PRIMARY KEY,
    board TEXT NOT NULL,
    user TEXT,
    date TEXT,
    post_text TEXT,
    replying_to INTEGER
);