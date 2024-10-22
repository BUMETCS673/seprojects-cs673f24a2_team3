-- Create additional users and grant privileges
CREATE USER 'selina'@'%' IDENTIFIED BY 'snowBall';

-- Grant all privileges on the movie_data database to the user
GRANT ALL PRIVILEGES ON movie_data.* TO 'selina'@'%';

-- Apply the changes
FLUSH PRIVILEGES;