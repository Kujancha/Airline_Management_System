CREATE DATABASE AirlineDB;
USE AirlineDB;

-- Create Tables
CREATE TABLE flights (
    flight_id INT PRIMARY KEY AUTO_INCREMENT,
    flight_number VARCHAR(10),
    source VARCHAR(30),
    destination VARCHAR(30),
    departure_time DATETIME,
    arrival_time DATETIME,
    seats INT,
    seats_booked INT DEFAULT 0 
);

CREATE TABLE passengers (
    passenger_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    gender VARCHAR(10),
    age INT,
    passport_no VARCHAR(20)
);

CREATE TABLE bookings (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    passenger_id INT,
    flight_id INT,
    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Confirmed', 'Cancelled') DEFAULT 'Confirmed', 
    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
);


CREATE TABLE booking_audit_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT,
    old_status ENUM('Confirmed', 'Cancelled'),
    new_status ENUM('Confirmed', 'Cancelled'),
    change_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    action_performed VARCHAR(50)
);

-- Trigger 1: Prevent double bookings for the same passenger on the same flight
DELIMITER $$
CREATE TRIGGER prevent_double_booking
BEFORE INSERT ON bookings
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM bookings 
        WHERE passenger_id = NEW.passenger_id 
        AND flight_id = NEW.flight_id
        AND status = 'Confirmed' 
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Passenger already has a confirmed booking on this flight.';
    END IF;
END$$
DELIMITER ;

-- Trigger 2: Automatically increment the seats_booked counter when a new booking is made
DELIMITER $$
CREATE TRIGGER after_booking_confirmed
AFTER INSERT ON bookings
FOR EACH ROW
BEGIN
    IF NEW.status = 'Confirmed' THEN
        UPDATE flights 
        SET seats_booked = seats_booked + 1 
        WHERE flight_id = NEW.flight_id;
    END IF;
END$$
DELIMITER ;

-- Trigger 3: Prevent overbooking (ensure seats_booked never exceeds total seats)
DELIMITER $$
CREATE TRIGGER prevent_overbooking
BEFORE INSERT ON bookings
FOR EACH ROW
BEGIN
    DECLARE total_seats INT;
    DECLARE booked_seats INT;
    
    -- Get the total seats and currently booked seats for the flight
    SELECT seats, seats_booked INTO total_seats, booked_seats
    FROM flights 
    WHERE flight_id = NEW.flight_id;
    
    -- Check if the new booking would exceed capacity
    IF (booked_seats >= total_seats) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot complete booking. Flight is fully booked.';
    END IF;
END$$
DELIMITER ;

-- Trigger 4: Handle cancellation and free up a seat
DELIMITER $$
CREATE TRIGGER after_booking_cancelled
AFTER UPDATE ON bookings
FOR EACH ROW
BEGIN
    -- If the status was changed from Confirmed to Cancelled
    IF OLD.status = 'Confirmed' AND NEW.status = 'Cancelled' THEN
        UPDATE flights 
        SET seats_booked = seats_booked - 1 
        WHERE flight_id = NEW.flight_id;
    END IF;
END$$
DELIMITER ;

-- Trigger 5: Audit log trigger - tracks status changes in bookings
DELIMITER $$
CREATE TRIGGER audit_booking_changes
AFTER UPDATE ON bookings
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO booking_audit_log (booking_id, old_status, new_status, action_performed)
        VALUES (OLD.booking_id, OLD.status, NEW.status, 'Status Update');
    END IF;
END$$
DELIMITER ;

-- Trigger 6: Validate passenger age before booking (e.g., must be at least 1 year old)
DELIMITER $$
CREATE TRIGGER validate_passenger_age
BEFORE INSERT ON passengers
FOR EACH ROW
BEGIN
    IF NEW.age < 1 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Passenger age must be at least 1 year.';
    END IF;
END$$
DELIMITER ;
