-- Restaurants table
CREATE TABLE restaurants (
  id serial PRIMARY KEY,
  user_id text NOT NULL,
  restaurant_name text NOT NULL UNIQUE,
  suburb text,
  city text,
  favourite_menu_item text,
  price_pp int,
  rating_out_of_five int
);

-- Users table
CREATE TABLE users (
  id serial PRIMARY KEY,
  username text NOT NULL UNIQUE,
  password_hash text NOT NULL
);
