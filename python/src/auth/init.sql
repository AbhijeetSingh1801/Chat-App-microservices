CREATE USER 'auth_user'@'%' IDENTIFIED BY 'Aauth123';

CREATE DATABASE auth;

GRANT ALL PRIVILEGES ON auth.* TO 'auth_user'@'%';


USE auth;

CREATE TABLE user(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);


INSERT INTO user (email, password) VALUES ('test@test.com', '$2b$12$oBgtvnR6f0eWIk89ARN7WewsMyea2ZCGLtpcBlDhG5VUnxF5RUnr6');