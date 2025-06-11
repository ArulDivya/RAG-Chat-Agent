CREATE DATABASE IF NOT EXISTS federal_registry;
CREATE USER IF NOT EXISTS 'fedreg_agent'@'localhost' IDENTIFIED BY 'agent_password123';
GRANT ALL PRIVILEGES ON federal_registry.* TO 'fedreg_agent'@'localhost';
FLUSH PRIVILEGES;