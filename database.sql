create database project;
\c project;

create table locations(location_id int, location text, listed_in_city text);
create table dishes(dish_id int, dish_liked text);
create table restaurants (restaurant_id int,
   url text, address text , name text, online_order text, book_table text,
   rate_5 float, votes int, phone text, location text, rest_type text,
   approx_cost_for_two int); --, PRIMARY KEY (restaurant_id));
create table rest_dish_links(link_id int, rest_id int, dish_id int);
create table rest_cuisine_links(link_id int, rest_id int, cuisine_id int);
create table cuisines(cuisine_id int, cuisine text);
create table users(user_id int, first_name text, last_name text, email_id text, gender text,
   location text, password text,username text, ph_no text, dob text);

copy locations from '/home/prafful/sem6/DBMS/Project/database/location.csv' with (FORMAT csv, HEADER);
copy dishes from '/home/prafful/sem6/DBMS/Project/database/dishes.csv' with (FORMAT csv, HEADER);
copy restaurants from '/home/prafful/sem6/DBMS/Project/database/restaurant.csv' with (FORMAT csv, HEADER, DELIMITER ',');
copy rest_dish_links from '/home/prafful/sem6/DBMS/Project/database/restaurant_dish_links.csv' with (FORMAT csv, HEADER);
copy rest_cuisine_links from '/home/prafful/sem6/DBMS/Project/database/restaurant_cuisine_links.csv' with (FORMAT csv, HEADER);
copy cuisines from '/home/prafful/sem6/DBMS/Project/database/cuisines.csv' with (FORMAT csv, HEADER);


copy users from '/home/prafful/sem6/DBMS/Project/database/userdata.csv' with (FORMAT csv, HEADER);
