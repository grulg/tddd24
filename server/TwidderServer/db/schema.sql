DROP TABLE IF EXISTS user;
CREATE TABLE user(
	id INTEGER PRIMARY KEY,
	first_name VARCHAR(30) NOT NULL,
	last_name VARCHAR(30) NOT NULL,
	city VARCHAR(30) NOT NULL,
	country VARCHAR(30) NOT NULL,
	gender VARCHAR(30) NOT NULL,
	email VARCHAR(30) NOT NULL,
	password VARCHAR(66) NOT NULL,
	token VARCHAR(30)
);

DROP TABLE IF EXISTS message;
CREATE TABLE message(
    id INTEGER PRIMARY KEY,
    reciever INT,
    writer INT,
    content VARCHAR(140),
    FOREIGN KEY(reciever) REFERENCES user(id),
    FOREIGN KEY(writer) REFERENCES user(id)
);

INSERT INTO user VALUES (
     0,
     'Alexander',
     'Haeger',
     'Linkoping',
     'Sweden',
     'Male',
     'me@haeger.me',
     'pbkdf2:sha1:1000$gQbLOVHV$abab53439e4f64f87c3959019e2b6bb08842c591',
     null
);