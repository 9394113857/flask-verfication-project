use crud_flask;

-- This query creates a table called `accounts` to store user account data.
CREATE TABLE if not exists accounts (
  -- The primary key of the table, which is an auto-incrementing integer.
  id INT NOT NULL AUTO_INCREMENT,
  -- The username of the account.
  username VARCHAR(255) NOT NULL,
  -- The password of the account.
  password VARCHAR(255) NOT NULL,
  -- The email address of the account.
  email VARCHAR(255) NOT NULL,
  -- The first name of the account holder.
  firstname VARCHAR(255) NOT NULL,
  -- The last name of the account holder.
  lastname VARCHAR(255) NOT NULL,
  -- The phone number of the account holder.
  phonenumber VARCHAR(15) NOT NULL,
  -- A boolean value indicating whether the account holder's phone number has been verified.
  phone_verified TINYINT(1) NOT NULL DEFAULT 0,
  -- A boolean value indicating whether the account holder's email address has been verified.
  email_verified TINYINT(1) NOT NULL DEFAULT 0,
  -- The primary key of the table.
  PRIMARY KEY (id)
);

-- Show all tables in the current database.
show tables;

-- Select all rows from the `accounts` table.
select * from accounts;

-- Describe the `accounts` table, showing the column names and data types.
desc accounts;

-- Select the username and phone_verified fields from the last entry in the `accounts` table.
-- This is a comment.
SELECT username, phone_verified FROM accounts ORDER BY id DESC LIMIT 1;

-- This query creates a table called `password_audit` to store password audit data.
CREATE TABLE if not exists password_audit (
    account_id INT,
    timestamp TIMESTAMP,
    new_password VARCHAR(255)
);

#########################

DELIMITER //

-- This trigger will be activated after an update on the `accounts` table.
-- If the password column is changed, it will insert a record into the `password_audit` table
-- with the account ID, timestamp of the change, and the new password.
CREATE TRIGGER password_change_trigger
AFTER UPDATE ON accounts
FOR EACH ROW
BEGIN
    IF NEW.password <> OLD.password THEN
        INSERT INTO password_audit (account_id, timestamp, new_password)
        VALUES (NEW.id, NOW(), NEW.password);
    END IF;
END;

//

DELIMITER ;

#########################

-- Select all records from the `password_audit` table.
SELECT * FROM password_audit;

-- Select all records for a specific account ID (replace 123 with the desired account ID).
SELECT * FROM password_audit WHERE account_id = 123;

-- Select records within a specific date range.
-- The date range is from '2023-09-01 00:00:00' to '2023-09-15 23:59:59'.
SELECT * FROM password_audit WHERE timestamp BETWEEN '2023-09-01 00:00:00' AND '2023-09-15 23:59:59';

#########################

-- Get the latest entry from the `password_audit` table.
SELECT * FROM password_audit ORDER BY timestamp DESC LIMIT 1;
