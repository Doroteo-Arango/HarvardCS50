-- Keep a log of any SQL queries you execute as you solve the mystery.

-- Check the crime scene reports table at the known day AND place
SELECT description FROM crime_scene_reports
WHERE year = 2021 AND month = 7 AND day = 28 AND street = "Humphrey Street";
-- Crime occured on July 28, 2021 AND it took place on Humphrey Street

-- Checking the interview transcripts
SELECT name, transcript FROM interviews
WHERE day = "28" AND month = "7" AND year = "2021";

-- How many people named Eugene in the peoples table
SELECT name FROM people WHERE name = 'Eugene';
-- Only one Eugene present

-- Who are the 3 witnesses from the list of names of people who gave interviews on july 28, 2021.
-- According to crime report each of them mentioned bakery in their report

SELECT name, transcript FROM interviews
WHERE year = 2021 AND month = 7 AND day = 28 AND transcript like '%bakery%'
order by name;

-- According to eugene the thief was withdrawing money FROM the ATM on Leggett Street.
-- Check the ATM records
SELECT account_number, amount FROM atm_transactions
WHERE year = 2021 AND month = 7 AND day = 28 AND atm_location= "Leggett Street" AND transaction_type = "withdraw";

-- Find account names from the bank based on their transaction details
SELECT name, atm_transactions.amount, atm_transactions.account_number FROM people
join bank_accounts on people.id = bank_accounts.person_id
join atm_transactions on bank_accounts.account_number = atm_transactions.account_number
WHERE atm_transactions.year=2021
AND atm_transactions.month=7
AND atm_transactions.day=28
AND atm_transactions.atm_location='Leggett Street'
AND atm_transactions.transaction_type = 'withdraw';

-- According to Raymond's lead, gather infomation about the airport in Fiftyville
SELECT abbreviation, full_name, city
FROM airports
WHERE city = 'Fiftyville';

-- What flights were scheduled on the 29th from Fiftyville
SELECT flights.id, full_name, city, flights.hour, flights.minute
FROM airports
join flights
on airports.id = flights.destination_airport_id
WHERE flights.origin_airport_id = (
    SELECT id
    FROM airports
    WHERE city = 'Fiftyville'
)
AND flights.year = 2021
AND flights.month = 7
AND flights.day = 29
order by flights.hour, flights.minute;
-- The first flight was at 8.20 to LaGuardia Airport in New York City (flight id is 36)
-- This could be where the thief went

-- Check passengers list for any names we recognise specifically
SELECT passengers.flight_id, name, passengers.passport_number, passengers.seat
FROM people
join passengers
on people.passport_number = passengers.passport_number
join flights
on passengers.flight_id = flights.id
WHERE flights.year = 2021
AND flights.month = 7
AND flights.day = 29
AND flights.hour = 8
AND flights.minute = 20
order by passengers.passport_number;
-- Check the phone call records to find the person who bought the tickets

-- Check the possible names of the callers, and put the names in the suspect list, ordering them according to the durations of the calls
SELECT name, phone_calls.duration
FROM people
join phone_calls
on people.phone_number = phone_calls.caller
WHERE phone_calls.year = 2021
AND phone_calls.month = 7
AND phone_calls.day = 28
AND phone_calls.duration <= 60
order by phone_calls.duration;

-- Check the possible names of the call-receiver, ordering them by the durations of the calls
SELECT name, phone_calls.duration
FROM people
join phone_calls
on people.phone_number = phone_calls.receiver
WHERE phone_calls.year = 2021
AND phone_calls.month = 7
AND phone_calls.day = 28
AND phone_calls.duration <= 60
order by phone_calls.duration;

-- According to Ruth the thief drove away in a car from the bakery, within 10 minutes from the theft.
-- Check the license plates of cars within that time frame with the respective owners of the vehicles

SELECT name, bakery_security_logs.hour, bakery_security_logs.minute
FROM people
join bakery_security_logs
on people.license_plate = bakery_security_logs.license_plate
WHERE bakery_security_logs.year = 2021
AND bakery_security_logs.month = 7
AND bakery_security_logs.day = 28
AND bakery_security_logs.activity = 'exit'
AND bakery_security_logs.minute >= 15
AND bakery_security_logs.minute <= 25
order by bakery_security_logs.minute;

-- Bruce appear in all queries, he is most likely the thief, fleeing to New York City
-- Robin is the accomplice