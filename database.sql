create database project;
\c project;

create table locations(location_id int, location text, listed_in_city text);
create table dishes(dish_id int, dish_liked text);
create table restaurants (restaurant_id int,
   url text, address text , name text, online_order text, book_table text,
   rate_5 float, votes int, phone text, rest_type text,
   approx_cost_for_two int);
create table rest_dish_links(link_id int, rest_id int, dish_id int);
create table rest_cuisine_links(link_id int, rest_id int, cuisine_id int);

copy locations from '/home/lalithsrinivas/DBMS/Project/location.csv' with (FORMAT csv, HEADER);
copy dishes from '/home/lalithsrinivas/DBMS/Project/dishes.csv' with (FORMAT csv, HEADER);
copy restaurants from '/home/lalithsrinivas/DBMS/Project/restaurant.csv' with (FORMAT csv, HEADER);
copy rest_dish_links from '/home/lalithsrinivas/DBMS/Project/restaurant_dish_links.csv' with (FORMAT csv, HEADER);
copy rest_cuisine_links from '/home/lalithsrinivas/DBMS/Project/restaurant_cuisine_links.csv' with (FORMAT csv, HEADER);
