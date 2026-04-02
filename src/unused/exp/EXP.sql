create table candidategroups
(
	id serial not null
		constraint id_unique
			primary key,
	alpha real not null,
	groupquantity integer not null,
	initializationt real not null,
	pairwiseincentivest real not null,
	initialgroupst real not null,
	persistgroupst real not null,
	sumsp real not null,
	formedgroups integer not null,
	testid integer
)
;

create table forminggroupslp
(
	id serial not null
		constraint id_unique2
			primary key,
	objectivevalue real not null,
	lpt real not null,
	testid integer not null,
	sumsp real not null,
	sumsps real not null,
	vehiclesingroups integer not null,
	vehiclesnotingroups integer not null
)
;

create table optimum
(
	id serial not null
		constraint id_unique3
			primary key,
	objectivevalue real not null,
	lpt real not null,
	testid integer not null
)
;

create table candidategroupssd
(
	id serial not null
		constraint id_uniquesd
			primary key,
	testid integer not null,
	sigma real,
	inittime real,
	sdtime real,
	grouptime real,
	formedgroups integer,
	sumsp real
)
;

create table test
(
	testid serial not null
		constraint groupsetting_pkey
			primary key,
	edges integer not null,
	vehicles integer not null,
	datetime timestamp default now() not null,
	dbuser varchar(60) not null,
	machine varchar(60) not null
)
;

alter table candidategroups
	add constraint candidategroups_test_testid_fk
		foreign key (testid) references test
			on delete cascade
;

alter table forminggroupslp
	add constraint forminggroupslp_test_testid_fk
		foreign key (testid) references test
			on delete cascade
;

alter table optimum
	add constraint optimum_test_testid_fk
		foreign key (testid) references test
			on delete cascade
;

alter table candidategroupssd
	add constraint candidategroupssd_test_testid_fk
		foreign key (testid) references test
			on delete cascade
;

create table groups
(
	id serial not null
		constraint groups_pkey
			primary key,
	testid integer not null
		constraint groups_test_testid_fk
			references test
				on delete cascade,
	vehicles integer[],
	saving real,
	platooned boolean default false not null
)
;

CREATE VIEW cgview AS SELECT t1.edges,
    t1.vehicles,
    (((avg(t2.initializationt) + avg(t2.pairwiseincentivest)) + avg(t2.initialgroupst)) + avg(t2.persistgroupst)) AS sum
   FROM (test t1
     JOIN candidategroups t2 ON ((t1.testid = t2.testid)))
  GROUP BY t1.edges, t1.vehicles
  ORDER BY t1.edges, t1.vehicles
;

CREATE VIEW glpview AS SELECT t1.edges,
    t1.vehicles,
    avg(t2.lpt) AS sum
   FROM (test t1
     JOIN forminggroupslp t2 ON ((t1.testid = t2.testid)))
  GROUP BY t1.edges, t1.vehicles
  ORDER BY t1.edges, t1.vehicles
;

CREATE VIEW optviewjoin AS SELECT t1.edges,
    t1.vehicles,
    t2.objectivevalue
   FROM (test t1
     JOIN optimum t2 ON ((t1.testid = t2.testid)))
  ORDER BY t1.edges, t1.vehicles
;

CREATE VIEW cgviewjoin AS SELECT t1.edges,
    t1.vehicles,
    t2.sumsp
   FROM (test t1
     JOIN candidategroups t2 ON ((t1.testid = t2.testid)))
  ORDER BY t1.edges, t1.vehicles
;

CREATE VIEW glpviewjoin AS SELECT t1.edges,
    t1.vehicles,
    t2.objectivevalue,
    t2.sumsp,
    t2.sumsps
   FROM (test t1
     JOIN forminggroupslp t2 ON ((t1.testid = t2.testid)))
  ORDER BY t1.edges, t1.vehicles
;

CREATE VIEW savings AS SELECT DISTINCT t1.vehicles,
    t1.edges,
    t2.groupquantity,
    t2.sumsp AS shortestpath,
    ((t2.sumsp - t1.groupshortest) + t1.sumsps) AS groupsaving,
    t3.objectivevalue AS optimal,
    ((((t2.sumsp - t1.groupshortest) + t1.sumsps) - t3.objectivevalue) / (t3.objectivevalue / (100)::double precision)) AS savingdifference
   FROM ((( SELECT test.testid,
            test.vehicles,
            test.edges,
            forminggroupslp.sumsp AS groupshortest,
            forminggroupslp.sumsps
           FROM (test
             JOIN forminggroupslp ON ((test.testid = forminggroupslp.testid)))) t1
     JOIN ( SELECT test.vehicles,
            test.edges,
            candidategroups.sumsp,
            candidategroups.groupquantity
           FROM (test
             JOIN candidategroups ON ((test.testid = candidategroups.testid)))) t2 USING (vehicles, edges))
     JOIN ( SELECT test.vehicles,
            test.edges,
            optimum.objectivevalue
           FROM (test
             JOIN optimum ON ((test.testid = optimum.testid)))) t3 USING (vehicles, edges))
;

CREATE VIEW example AS SELECT te.testid,
    op.objectivevalue,
    op.lpt
   FROM (test te
     JOIN optimum op ON ((te.testid = op.id)));
;

