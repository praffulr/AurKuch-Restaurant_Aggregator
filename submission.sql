create database group_30;
\c group_30;

-----------------REMOVE THIS IN FINAL SUBMISSION---------------------
create USER group_30 with password '776-302-579';
  GRANT ALL PRIVILEGES ON DATABASE group_30 TO group_30;
---------------------------------------------------------------------

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
,CONSTRAINT check_age CHECK ( (EXTRACT (YEAR FROM age(reg_time,dob))) >= 14 ));
create table cart_data(username text, item_id int, count int, PRIMARY KEY(username, item_id),
  CONSTRAINT item_in_list FOREIGN KEY(item_id) REFERENCES rest_dish_links(link_id),
  CONSTRAINT user_in_users FOREIGN KEY (username) REFERENCES users(username));

create table active_users( first_name text, last_name text, email_id text, gender text,location text, password text,
  username text, ph_no text, dob timestamp, reg_time timestamp, login_time timestamp, PRIMARY KEY (username),
  CONSTRAINT active_user_in_user FOREIGN KEY (username) REFERENCES users(username) ) ;
create table orders (order_time timestamp, username text, item_id integer, count integer, PRIMARY KEY(username, order_time, item_id));
create table order_ids (id SERIAL, order_time timestamp, username text, rest_id integer,
  PRIMARY KEY(order_time, username, rest_id)
  -- , CONSTRAINT in_orders FOREIGN KEY(order_time, username) REFERENCES orders(order_time, username)
 );

  copy locations from '/home/prafful/sem6/DBMS/Project/database/location.csv' with (FORMAT csv, HEADER);
  --Inserting from locations into cities
  INSERT INTO cities(city) ( SELECT distinct(listed_in_city) FROM locations );
  copy dishes from '/home/prafful/sem6/DBMS/Project/database/dishes.csv' with (FORMAT csv, HEADER);
  copy restaurants from '/home/prafful/sem6/DBMS/Project/database/restaurant.csv' with (FORMAT csv, HEADER, DELIMITER ',');
  copy rest_dish_links from '/home/prafful/sem6/DBMS/Project/database/restaurant_dish_links.csv' with (FORMAT csv, HEADER);
  copy rest_cuisine_links from '/home/prafful/sem6/DBMS/Project/database/restaurant_cuisine_links.csv' with (FORMAT csv, HEADER);
  copy cuisines from '/home/prafful/sem6/DBMS/Project/database/cuisines.csv' with (FORMAT csv, HEADER);
  copy users from '/home/prafful/sem6/DBMS/Project/database/userdata.csv' with (FORMAT csv, HEADER);

  copy orders from '/home/prafful/sem6/DBMS/Project/database/ordersdata.csv' with (FORMAT csv, HEADER);



  ---------------INDEXES----------------------------
  CREATE INDEX usernames ON users(username);
  CREATE INDEX rest_names ON restaurants(name);

  --helper function----------------------------
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

  --helper for finding rest_dish_link_id
  CREATE OR REPLACE FUNCTION link_id(rest_id_1 integer, dish_1 text) RETURNS INTEGER AS
  $$
    BEGIN
      RETURN
      (
        WITH
        temp_1 AS
        (
          Select dish_id as id
          FROM dishes
          where dishes.dish_liked = dish_1
        )
        select rest_dish_links.link_id
        FROM rest_dish_links INNER JOIN temp_1 ON temp_1.id = rest_dish_links.dish_id
        where rest_dish_links.rest_id = rest_id_1
      );
    END;
  $$ language plpgsql;

  --helper for finding rest_id from dish_link_id
  CREATE OR REPLACE FUNCTION get_rest_id(item_id integer) RETURNS INTEGER AS
  $$
    BEGIN
      RETURN
      (
        SELECT rest_id
        FROM rest_dish_links
        WHERE item_id = link_id
      );
    END;
  $$ language plpgsql;
  ---------------------------------------------------
  --trigger for updating location in user when updated in active_users table
  CREATE OR REPLACE FUNCTION change_loc() RETURNS TRIGGER AS
  $$
    BEGIN
      UPDATE users
      SET location = NEW.location
      where location = OLD.location;
      RETURN NULL;
    END;
  $$ language plpgsql;

  CREATE TRIGGER update_location
    AFTER UPDATE ON active_users
    FOR EACH ROW
    EXECUTE PROCEDURE change_loc();

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
        IF (search_mode = 1) THEN
          IF (sort_flag) THEN
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
        ELSIF (search_mode = 2) THEN
          IF (sort_flag) THEN
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
        ELSIF (search_mode = 3) THEN
          IF (sort_flag) THEN
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
        ELSIF (search_mode = 4) THEN
          IF (sort_flag) THEN
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

    --item_id is link_id in the rest_dish_links table
    CREATE OR REPLACE FUNCTION update_cart(username_1 text, item_id_1 integer, count_1 integer) returns VOID AS
    $$
      BEGIN
        IF (count_1 = 0) THEN
            DELETE
            FROM cart_data
            WHERE cart_data.username = username_1 and
            cart_data.item_id = item_id_1;
        ELSIF(item_in_cart(username_1, item_id_1)) THEN
          --update
            UPDATE cart_data
            SET count = count_1
            WHERE username = username_1 and item_id = item_id_1;
        ELSE
        --insert
            INSERT
            INTO cart_data
            VALUES(username_1, item_id_1, count_1);
        END IF;
      END;
    $$ language plpgsql;

    --updating user's location
    CREATE OR REPLACE FUNCTION update_user_loc(username_1 text, new_loc text) RETURNS VOID AS
    $$
      BEGIN
        UPDATE active_users
        SET location = new_loc
        WHERE username = username_1;
      END;
    $$ language plpgsql;


    --function for login
    CREATE OR REPLACE FUNCTION login(username_1 text, password_1 text) RETURNS VOID AS
    $$
      BEGIN
            INSERT INTO active_users
            (
            SELECT *, current_timestamp
            FROM users
            WHERE users.username = username_1 and users.password = password_1
            );
            IF (
               (
                 SELECT COUNT(t)
                 FROM
                 (
                   SELECT *, current_timestamp as t
                   FROM users
                   WHERE users.username = username_1 and users.password = password_1
                 ) as temp
               )
                = 0) THEN
               RAISE EXCEPTION 'INVALID CREDENTIALS';
            END IF;
      END;
    $$ language plpgsql;

    --function for logout
    CREATE OR REPLACE FUNCTION logout(username_1 text) RETURNS VOID AS
    $$
      BEGIN
        DELETE
        FROM active_users
        WHERE active_users.username = username_1;
      END;
    $$ language plpgsql;

    -- --TRIGGER FOR CART-ORDER
    CREATE OR REPLACE FUNCTION delete_in_cart_func() RETURNS TRIGGER AS
    $$
      BEGIN
        DELETE
        FROM cart_data
        WHERE (username=NEW.username and item_id=NEW.item_id and count=NEW.count);
        RETURN NULL;
      END;
    $$ language plpgsql;

    CREATE TRIGGER cart_order
    AFTER INSERT ON orders
    FOR EACH ROW
    EXECUTE PROCEDURE delete_in_cart_func();
    ---TRIGGER TO INSERT IN ORDER_IDS TABLE
    CREATE OR REPLACE FUNCTION put_in_orderids_func() RETURNS TRIGGER AS
    $$
      BEGIN
        INSERT INTO
        order_ids(order_time, username, rest_id) VALUES(NEW.order_time, NEW.username, get_rest_id(NEW.item_id));
        RETURN NULL;
      END;
    $$ language plpgsql;

    CREATE TRIGGER put_in_orderids
    AFTER INSERT ON orders
    FOR EACH ROW
    EXECUTE PROCEDURE put_in_orderids_func();

    --ORDER
    CREATE OR REPLACE FUNCTION ordering(username text, item_id integer, count integer) RETURNS VOID AS
    $$
      BEGIN
        INSERT INTO orders VALUES(current_timestamp, username, item_id, count);
      END;
    $$ language plpgsql;


    --to copy into order_ids
    CREATE VIEW item_rest AS
    (
      SELECT link_id as item_id, rest_id
      FROM rest_dish_links
    );
    INSERT INTO order_ids(order_time, username, rest_id)
    (
      SELECT orders.order_time, orders.username, item_rest.rest_id
      FROM (orders INNER JOIN item_rest ON item_rest.item_id = orders.item_id)
      GROUP BY orders.order_time, orders.username, item_rest.rest_id
    )
    ;
