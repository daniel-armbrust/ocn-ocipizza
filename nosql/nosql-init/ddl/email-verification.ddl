CREATE TABLE IF NOT EXISTS email_verification ( 
    email STRING,
    token STRING,   
    password_recovery BOOLEAN DEFAULT FALSE,                      
    expiration_ts INTEGER,
PRIMARY KEY (email)) USING TTL 1 DAYS