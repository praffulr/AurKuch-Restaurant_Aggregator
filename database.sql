create database project;
\c project;

CREATE or REPLACE FUNCTION calculate_age(a timestamp, b timestamp) RETURNS float AS $$
  ( ( SELECT EXTRACT (YEAR FROM (SELECT age(a, b)) ) ));
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION return_query() RETURNS VOID AS
$$

-- create database temp;
--   drop database temp;
create VIEW x as select * from users;

$$ language sql;

create table locations(location_id int, location text, listed_in_city text, PRIMARY KEY(location, listed_in_city));
create table cities(city text, CONSTRAINT city_uniq UNIQUE(city));
create table dishes(dish_id int, dish_liked text, PRIMARY KEY(dish_liked));
create table restaurants (restaurant_id int, address text , name text, online_order text, book_table text,
   rate_5 float, votes int, phone text, location text, rest_type text, approx_cost_for_two int, PRIMARY KEY (address, name));
create table rest_dish_links(link_id int, rest_id int, dish_id int, price float, PRIMARY KEY(link_id));
create table rest_cuisine_links(link_id int, rest_id int, cuisine_id int, PRIMARY KEY(link_id));
create table cuisines(cuisine_id int, cuisine text, PRIMARY KEY(cuisine));
create table users(first_name text, last_name text, email_id text, gender text,location text, password text,username text, ph_no text,
  dob timestamp, reg_time timestamp, PRIMARY KEY(username),CONSTRAINT loc_in_city FOREIGN KEY(location) REFERENCES cities(city)
,CONSTRAINT check_age CHECK ( (EXTRACT (YEAR FROM age(reg_time,dob))) >= 18 ));
create table cart_data(username text, item_id int, count int, PRIMARY KEY(username, item_id),
  CONSTRAINT item_in_list FOREIGN KEY(item_id) REFERENCES rest_dish_links(link_id));


  -----------------REMOVE THIS IN FINAL SUBMISSION---------------------
  create USER admin with password 'admin';
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA PUBLIC TO admin;
  ---------------------------------------------------------------------

-- CREATE FUNCTION cond_loc_in_locs(location text, locations) RETURNS BOOLEAN AS $$
--   SELECT ( $1 IN ($2.listed_in_city) );
-- $$ LANGUAGE SQL;
--
-- CREATE FUNCTION loc_in_locs() RETURNS TRIGGER AS $$
-- BEGIN
--   IF (SELECT cond_loc_in_locs(NEW.location, locations.listed_in_city)) THEN
--     INSERT INTO users(first_name, last_name, email_id, gender,
--       location, password, username, ph_no, dob, reg_time)
--       VALUES (new.first_name, new.last_name, new.email_id, new.gender, new.location, new.password
--         , new.username, new.ph_no, new.dob, current_timestamp);
--   END IF;
--   RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;
--
-- CREATE TRIGGER loc_in_locations
--   BEFORE INSERT ON users
--   FOR EACH ROW
--   --WHEN (users.location IN locations.listed_in_city)
--   EXECUTE PROCEDURE loc_in_locs();



-- CREATE FUNCTION insert_entry() RETURNS TRIGGER AS
-- $$
--   BEGIN
--     IF (calculate_age(NEW.reg_time, NEW.dob) < 18) THEN
--       DELETE VALUES(NEW) FROM users;
--       RAISE EXCEPTION 'User is not an adult';
--     END IF;
--     RETURN NULL;
--   END;
-- $$ LANGUAGE plpgsql;
--
-- CREATE TRIGGER user_age
--   AFTER INSERT ON users
--   FOR EACH ROW
--   --WHEN (calculate_age(NEW.reg_time, NEW.dob) >= 18)
--   EXECUTE PROCEDURE insert_entry();

-- CREATE RULE user_age

copy locations from '/home/prafful/sem6/DBMS/Project/database/location.csv' with (FORMAT csv, HEADER);
--Inserting from locations into cities
INSERT INTO cities(city) ( SELECT distinct(listed_in_city) FROM locations );
copy dishes from '/home/prafful/sem6/DBMS/Project/database/dishes.csv' with (FORMAT csv, HEADER);
copy restaurants from '/home/prafful/sem6/DBMS/Project/database/restaurant.csv' with (FORMAT csv, HEADER, DELIMITER ',');
copy rest_dish_links from '/home/prafful/sem6/DBMS/Project/database/restaurant_dish_links.csv' with (FORMAT csv, HEADER);
copy rest_cuisine_links from '/home/prafful/sem6/DBMS/Project/database/restaurant_cuisine_links.csv' with (FORMAT csv, HEADER);
copy cuisines from '/home/prafful/sem6/DBMS/Project/database/cuisines.csv' with (FORMAT csv, HEADER);
copy users from '/home/prafful/sem6/DBMS/Project/database/userdata.csv' with (FORMAT csv, HEADER);




-- CREATE OR REPLACE FUNCTION login(username text, password text)


--Show 'lim' number of results searched by keyword 'searchby' in mode 'search_mode' sorted in 'sort_mode' - inc/dec given by 'flag'
--search_mode:
--1 -> restaurant
--2 -> dish_name
--3 -> Cuisine_name
--4 -> Location
------------------------
--Sort_flag:
-- true -> DESC
-- false -> Asce
CREATE OR REPLACE FUNCTION search_rests(search_mode integer, searchby text, sortby text, sort_flag BOOLEAN, lim integer) returns
  TABLE(Name text, rest_type text, rating_5 float, address text, phone_number text) AS
  $$
  BEGIN
    IF (SELECT (search_mode == 1)) THEN
      IF (SELECT sort_flag) THEN
        RETURN QUERY
        (
          SELECT restaurants.Name, restaurants.rest_type, restaurants.rate_5, restaurants.address, restaurants.phone
          FROM restaurants
          WHERE Name = searchby
          ORDER BY sortby DESC
          LIMIT lim
        );
      ELSE
        RETURN QUERY
        (
          SELECT restaurants.Name, restaurants.rest_type, restaurants.rate_5, restaurants.address, restaurants.phone
          FROM restaurants
          WHERE Name = searchby
          ORDER BY sortby
          LIMIT lim
        );
      END IF;
    ELSIF (SELECT (search_mode == 2)) THEN
      IF (SELECT sort_flag) THEN
        RETURN QUERY
        (
          WITH
          temp_2 AS (
            SELECT *
            FROM dishes
            WHERE dishes.dish_liked = searchby
          ),
          temp_1 AS (
            SELECT *
            FROM rest_dish_links INNER JOIN temp_2 ON rest_dish_links.dish_id = temp_2.dish_id
          )
          SELECT restaurants.Name, restaurants.rest_type, restaurants.rate_5, restaurants.address, restaurants.phone
          FROM restaurants INNER JOIN temp_1 ON restaurants.restaurant_id = temp_1.rest_id
          ORDER BY sortby DESC
          LIMIT lim
        );
      ELSE
        RETURN QUERY
        (
          WITH
          temp_2 AS (
            SELECT *
            FROM dishes
            WHERE dishes.dish_liked = searchby
          ),
          temp_1 AS (
            SELECT *
            FROM rest_dish_links INNER JOIN temp_2 ON rest_dish_links.dish_id = temp_2.dish_id
          )
          SELECT restaurants.Name, restaurants.rest_type, restaurants.rate_5, restaurants.address, restaurants.phone
          FROM restaurants INNER JOIN temp_1 ON restaurants.restaurant_id = temp_1.rest_id
          ORDER BY sortby
          LIMIT lim
        );
      END IF;
    ELSIF (SELECT (search_mode == 3)) THEN
      IF (SELECT sort_flag) THEN
        RETURN QUERY
        (
          WITH
          temp_2 AS (
            SELECT *
            FROM cuisines
            WHERE cuisines.cuisine = searchby
          ),
          temp_1 AS (
            SELECT *
            FROM rest_cuisine_links INNER JOIN temp_2 ON rest_cuisine_links.cuisine_id = temp_2.cuisine_id
          )
          SELECT restaurants.Name, restaurants.rest_type, restaurants.rate_5, restaurants.address, restaurants.phone
          FROM restaurants INNER JOIN temp_1 ON restaurants.restaurant_id = temp_1.rest_id
          ORDER BY sortby DESC
          LIMIT lim
        );
      ELSE
        RETURN QUERY
        (
          WITH
          temp_2 AS (
            SELECT *
            FROM cuisines
            WHERE cuisines.cuisine = searchby
          ),
          temp_1 AS (
            SELECT *
            FROM rest_cuisine_links INNER JOIN temp_2 ON rest_cuisine_links.cuisine_id = temp_2.cuisine_id
          )
          SELECT restaurants.Name, restaurants.rest_type, restaurants.rate_5, restaurants.address, restaurants.phone
          FROM restaurants INNER JOIN temp_1 ON restaurants.restaurant_id = temp_1.rest_id
          ORDER BY sortby
          LIMIT lim
        );
      END IF;
    ELSIF (SELECT (search_mode == 4)) THEN
      IF (SELECT sort_flag) THEN
        RETURN QUERY
        (
          SELECT restaurants.Name, restaurants.rest_type, restaurants.rate_5, restaurants.address, restaurants.phone
          FROM restaurants
          WHERE location = searchby
          ORDER BY sortby DESC
          LIMIT lim
        );
      ELSE
        RETURN QUERY
        (
          SELECT restaurants.Name, restaurants.rest_type, restaurants.rate_5, restaurants.address, restaurants.phone
          FROM restaurants
          WHERE location = searchby
          ORDER BY sortby DESC
          LIMIT lim
        );
      END IF;
    END IF;
  END;
  $$ language plpgsql;


CREATE OR REPLACE FUNCTION item_in_cart(username text, item_id integer) RETURNS BOOLEAN AS
$$
    SELECT
    (
      (
        SELECT username = ANY (SELECT username from cart_data)
      )
      AND
      (
        SELECT item_id = ANY (SELECT item_id from cart_data)
      )
    );
$$ language SQL;

--item_id is link_id in the rest_dish_links table
CREATE OR REPLACE FUNCTION update_cart(username text, item_id integer, count integer) returns VOID AS
$$
  BEGIN
    IF(item_in_cart(username, item_id)) THEN
      --update
        UPDATE cart_data
        SET cart_data.count = count
        WHERE cart_data.username = username and cart_data.item_id = item_id;
    ELSE
    --insert
        INSERT
        INTO cart_data
        VALUES(username, item_id, count);
    END IF;
  END;
$$ language plpgsql;
