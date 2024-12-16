-- SQLite
INSERT INTO Task (name, category, priority, deadline) VALUES
--('Buy birthday gifts', 'Personal', 'Medium', '2024-12-20 10:00:00');
('Team meeting preparation', 'Work', 'Medium', '2024-12-18 09:30:00'),
('Pay utility bills', 'Personal', 'Low', '2024-12-21 12:00:00'),
('Client presentation', 'Work', 'High', '2024-12-19 14:00:00'),
('Submit tax documents', 'Work', 'High', '2024-12-22 15:00:00'),
('Read a book', 'Personal', 'Low', '2024-12-25 19:00:00'),
('Organize desk', 'Work', 'Low', '2024-12-23 11:00:00');
SELECT * FROM Reminder;

INSERT INTO Reminder (name, category, priority, time) VALUES
('Morning workout', 'Personal', 'High', '07:00:00'),
('Weekly team sync', 'Work', 'Medium', '10:00:00'),
('Pick up laundry', 'Personal', 'Low', '18:00:00'),
('Submit project draft', 'Work', 'High', '15:00:00'),
('Meditation', 'Personal', 'Medium', '06:30:00'),
('Code review session', 'Work', 'Medium', '11:00:00'),
('Grocery shopping', 'Personal', 'Low', '17:30:00'),
('Update project plan', 'Work', 'High', '14:00:00'),
('Call best friend', 'Personal', 'Medium', '20:00:00'),
('Client follow-up call', 'Work', 'High', '16:00:00');