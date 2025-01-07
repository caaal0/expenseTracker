-- CMSC 127 PROJECT: Expense Tracker SQL Dump
-- Date Created: 2023-06-04
-- Authors: ST1L - Group 3
	-- Brinas, Sheila Mycah D.
	-- Cabanisas, Joanna Mae P.
	-- Sagun, Justin Carl C.
------------------------------------------------------------------------------------------------
-- Dropping the database if it exists
DROP DATABASE IF EXISTS expensetracker;

-- Creating the database
CREATE DATABASE IF NOT EXISTS expensetracker;
USE expensetracker;

-- Creating the tables

-- Dumping structure for table expensetracker.user: ~4 columns
CREATE TABLE IF NOT EXISTS user (
	user_id INT PRIMARY KEY AUTO_INCREMENT, 
	first_name VARCHAR(14) NOT NULL, 
	middle_init VARCHAR(5) DEFAULT NULL, 
	last_name VARCHAR(14) NOT NULL,
	amount_owed DECIMAL(7,2) DEFAULT 0,
	amount_lent DECIMAL(7,2) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Dumping structure for table expensetracker.egroup: ~2 columns
CREATE TABLE IF NOT EXISTS egroup (
	group_id INT PRIMARY KEY AUTO_INCREMENT, 
	group_name VARCHAR(30) NOT NULL, 
	num_of_members INT(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Dumping structure for table expensetracker.user_group: ~2 columns, ~2 constraints
CREATE TABLE IF NOT EXISTS user_group (
	group_id INT(4), user_id INT(4), 
	CONSTRAINT user_group_group_id_fk FOREIGN KEY(group_id) REFERENCES egroup(group_id) ON DELETE CASCADE,
	CONSTRAINT user_group_id_fk FOREIGN KEY(user_id) REFERENCES user(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Dumping structure for table expensetracker.expense: ~6 columns
CREATE TABLE IF NOT EXISTS expense (
	expense_id INT PRIMARY KEY AUTO_INCREMENT, 
	description VARCHAR(30), -- Food, Travel, etc.
	type VARCHAR(14), -- Group, Friend
	amount DECIMAL(7,2) NOT NULL, 
	payee INT(4) NOT NULL, 
	transaction_date DATE,
	remaining_balance DECIMAL(7,2),
	is_settled INT(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Dumping structure for table expensetracker.has_expense: ~3 columns, ~3 constraints
CREATE TABLE IF NOT EXISTS has_expense (
	user_id INT, 
	group_id INT, 
	expense_id INT, 
	CONSTRAINT has_expense_user_id_fk FOREIGN KEY(user_id) REFERENCES user(user_id) ON DELETE CASCADE, 
	CONSTRAINT has_expense_group_id_fk FOREIGN KEY(group_id) REFERENCES egroup(group_id) ON DELETE CASCADE, 
	CONSTRAINT has_expense_expense_id_fk FOREIGN KEY(expense_id) REFERENCES expense(expense_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Dumping structure for table expensetracker.payment: ~5 columns, ~3 constraints
CREATE TABLE IF NOT EXISTS payment (
	payment_id INT PRIMARY KEY AUTO_INCREMENT,
	user_id INT, 
	group_id INT, 
	expense_id INT,
	amount_paid INT,
	CONSTRAINT payment_user_id_fk FOREIGN KEY(user_id) REFERENCES user(user_id) ON DELETE CASCADE, 
	CONSTRAINT payment_group_id_fk FOREIGN KEY(group_id) REFERENCES egroup(group_id) ON DELETE CASCADE, 
	CONSTRAINT payment_expense_id_fk FOREIGN KEY(expense_id) REFERENCES expense(expense_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO user(user_id, first_name, last_name) VALUES(1, "User", "User")