--------------
--- Tables ---
--------------
CREATE TABLE Experiments (
  id SERIAL PRIMARY KEY NOT NULL,
  db_user VARCHAR(64) NOT NULL,
  started_at TIMESTAMP NOT NULL,
  finished_at TIMESTAMP NULL
);

CREATE TABLE Tests (
  id SERIAL PRIMARY KEY NOT NULL,
  experiment_id INT NOT NULL,
  vehicle_set_id INT NOT NULL,
  number_of_edges INT NOT NULL,
  number_of_vehicles INT NOT NULL,
  number_of_groups INT NOT NULL,
  enable_grouping BOOLEAN,
  identify_group_by VARCHAR(64),
  distribution VARCHAR(64) NOT NULL,
  database VARCHAR(64) NOT NULL,
  longest_shortest_path REAL NOT NULL,
  shortest_path_total REAL NOT NULL,
  machine VARCHAR(64) NOT NULL,
  db_user VARCHAR(64) NOT NULL,
  FOREIGN KEY (experiment_id) REFERENCES Experiments(id) ON DELETE CASCADE
);

CREATE TABLE Times (
  id SERIAL PRIMARY KEY NOT NULL,
  test_id INT NOT NULL,
  init_considered_set REAL,
  init_total REAL,
  creating_incentives REAL,
  creating_groups REAL,
  storing_routes REAL,
  calc_group_savings REAL,
  determine_disjunct_groups REAL,
  storing_incentives REAL,
  storing_groups REAL,
  routing REAL,
  FOREIGN KEY (test_id) REFERENCES Tests(id) ON DELETE CASCADE
);

-- CREATE TABLE Groups_Properties (
--   id SERIAL PRIMARY KEY NOT NULL,
--   test_id INT NOT NULL,
--   algorithm VARCHAR(64),
--   parameter INT[],
--   FOREIGN KEY (test_id) REFERENCES Tests(id) ON DELETE CASCADE
-- );

CREATE TABLE Group_Sets (
  id SERIAL PRIMARY KEY NOT NULL,
  test_id INT NOT NULL,
  calculated_number_of_groups INT NOT NULL,
  vehicles_in_groups INT NOT NULL,
  vehicles_not_in_groups INT NOT NULL,
  successfull_groups INT NOT NULL,
  unsuccessfull_groups INT NOT NULL,
  group_savings REAL NOT NULL,
  parameter JSONB,
  FOREIGN KEY (test_id) REFERENCES Tests(id) ON DELETE CASCADE
);

CREATE TABLE Groups (
  id SERIAL PRIMARY KEY NOT NULL,
  test_id INT NOT NULL,
  group_set_id INT NOT NULL,
  groups_shortest_path_sum REAL NOT NULL,
  group_incentives INT[] NOT NULL,
  vehicles INT[] NOT NULL,
  parameter JSONB,
  FOREIGN KEY (test_id) REFERENCES Tests(id) ON DELETE CASCADE,
  FOREIGN KEY (group_set_id) REFERENCES Group_Sets(id) ON DELETE CASCADE
);

CREATE TABLE Routing (
  id SERIAL PRIMARY KEY NOT NULL,
  test_id INT NOT NULL,
  group_id INT NULL,
  savings REAL NOT NULL,
  algorithm VARCHAR(64) NOT NULL,
  shortest_path REAL NOT NULL,
  parameter JSONB,
  FOREIGN KEY (test_id) REFERENCES Tests(id) ON DELETE CASCADE,
  FOREIGN KEY (group_id) REFERENCES Groups(id) ON DELETE CASCADE
);

CREATE TABLE Slicing (
  id SERIAL PRIMARY KEY NOT NULL,
  test_id INT NOT NULL,
  method VARCHAR(64) NOT NULL,
  slices INT NOT NULL,
  vehicles INT[] NOT NULL,
  parameter JSONB,
  FOREIGN KEY (test_id) REFERENCES Tests(id) ON DELETE CASCADE
);

CREATE TABLE Incentives (
  id SERIAL PRIMARY KEY NOT NULL,
  test_id INT NOT NULL,
  incentives REAL[] NOT NULL,
  vehicles INT[] NOT NULL,
  criteria JSONB NOT NULL,
  FOREIGN KEY (test_id) REFERENCES Tests(id) ON DELETE CASCADE
);

CREATE TABLE Vehicles (
  id SERIAL PRIMARY KEY NOT NULL,
  test_id INT NOT NULL,
  vehicle_id INT NOT NULL,
  incentive_id INT[] NULL,
  shortest_path INT[] NOT NULL,
  platoon_path INT[] NOT NULL,
  shortest_path_value REAL NOT NULL,
  platoon_path_value REAL NOT NULL,
  FOREIGN KEY (test_id) REFERENCES Tests(id) ON DELETE CASCADE
);

-------------
--- Views ---
-------------
CREATE VIEW Gradient_Incentive AS
  SELECT experiment_id, t.id as test_id, incentives.id as incentive_id,
    incentives.incentives[1] as incentive_1, incentives.incentives[2] as incentive_2,
    incentives.incentives[3] as incentive_3, incentives.incentives[4] as incentive_4,
    savings, shortest_path,
    criteria->'start_end_points'->0->0 as start_veh1_lat, criteria->'start_end_points'->0->1 as start_veh1_lon,
    criteria->'start_end_points'->0->2 as start_veh2_lat, criteria->'start_end_points'->0->3 as start_veh2_lon,
    criteria->'start_end_points'->1->0 as end_veh1_lat, criteria->'start_end_points'->1->1 as end_veh1_lon,
    criteria->'start_end_points'->1->2 as end_veh2_lat, criteria->'start_end_points'->1->3 as end_veh2_lon
  FROM incentives
  JOIN tests t on incentives.test_id = t.id
  JOIN groups g ON incentives.vehicles <@ g.vehicles AND array_length(g.vehicles, 1) = 2
  JOIN routing r ON g.id = r.group_id
  WHERE criteria?'start_end_points';

CREATE VIEW Incentives_Savings AS
  SELECT experiment_id, tests.id as test_id, i.id as incentive_id, i.incentives, savings, shortest_path
  FROM tests
  JOIN incentives i on tests.id = i.test_id
  JOIN groups g ON i.vehicles <@ g.vehicles AND array_length(g.vehicles, 1) = 2
  JOIN routing r ON g.id = r.group_id