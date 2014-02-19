DROP TABLE IF EXISTS user;
CREATE TABLE user(
	id int AUTO INCREMENT,
	first_name VARCHAR(30) NOT NULL,
	last_name VARCHAR(30) NOT NULL,
	city VARCHAR(30) NOT NULL,
	country VARCHAR(30) NOT NULL,
	email VARCHAR(30) NOT NULL,
	password VARCHAR(30) NOT NULL,
	token VARCHAR(30),
	PRIMARY KEY(email)
);

INSERT INTO user VALUES (
     0,
     'Alexander',
     'Häger',
     'Linköping',
     'Sweden',
     'me@haeger.me',
     'q',
     null
);