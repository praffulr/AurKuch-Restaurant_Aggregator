create database project;
\c project;

create table locations(location_id int, location text, listed_in_city text, PRIMARY KEY(location, listed_in_city));
create table dishes(dish_id int, dish_liked text, PRIMARY KEY(dish_liked));
create table restaurants (restaurant_id int,
   url text, address text , name text, online_order text, book_table text,
   rate_5 float, votes int, phone text, location text, rest_type text,
   approx_cost_for_two int, PRIMARY KEY (address, name));
create table rest_dish_links(link_id int, rest_id int, dish_id int, price float, PRIMARY KEY(rest_id, dish_id));
create table rest_cuisine_links(link_id int, rest_id int, cuisine_id int, PRIMARY KEY(rest_id, cuisine_id));
create table cuisines(cuisine_id int, cuisine text, PRIMARY KEY(cuisine));
create table users(first_name text, last_name text, email_id text, gender text,
   location text, password text,username text, ph_no text, dob timestamp, reg_time timestamp, PRIMARY KEY(username)
 );
 -- CONSTRAINT loc_in_locations FOREIGN KEY(location) REFERENCES locations(listed_in_city));

copy locations from '/home/prafful/sem6/DBMS/Project/database/location.csv' with (FORMAT csv, HEADER);
copy dishes from '/home/prafful/sem6/DBMS/Project/database/dishes.csv' with (FORMAT csv, HEADER);
copy restaurants from '/home/prafful/sem6/DBMS/Project/database/restaurant.csv' with (FORMAT csv, HEADER, DELIMITER ',');
copy rest_dish_links from '/home/prafful/sem6/DBMS/Project/database/restaurant_dish_links.csv' with (FORMAT csv, HEADER);
copy rest_cuisine_links from '/home/prafful/sem6/DBMS/Project/database/restaurant_cuisine_links.csv' with (FORMAT csv, HEADER);
copy cuisines from '/home/prafful/sem6/DBMS/Project/database/cuisines.csv' with (FORMAT csv, HEADER);


copy users from '/home/prafful/sem6/DBMS/Project/database/userdata.csv' with (FORMAT csv, HEADER);
