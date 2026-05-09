-- Database Schema for Smart Task Manager System

-- 1. Users Table
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL
);

-- 2. Tasks Table
CREATE TABLE task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    priority VARCHAR(20) NOT NULL DEFAULT 'Medium',
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    created_date TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key linking the task to the user who created it
    user_id INTEGER NOT NULL,
    CONSTRAINT fk_user
      FOREIGN KEY(user_id) 
      REFERENCES "user"(id)
      ON DELETE CASCADE
);