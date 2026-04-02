create table candidategroups
(
	id serial not null
		constraint id_unique
			primary key,
	edges integer not null,
	vehicles integer not null,
	alpha real not null,
	groupquantity integer not null,
	initializationt real not null,
	pairwiseincentivest real not null,
	initialgroupst real not null,
	persistgroupst real not null,
	sumsp real not null,
	formedgroups integer not null,
	datetime timestamp default now() not null,
	groupsetid integer
)
;

create unique index candidategroups_groupsetid_uindex
	on candidategroups (groupsetid)
;

create table forminggroupslp
(
	id serial not null
		constraint id_unique2
			primary key,
	edges integer not null,
	vehicles integer not null,
	objectivevalue real not null,
	lpt real not null,
	groups varchar(45) not null,
	platoonedvehicles varchar(45) not null,
	sumsp real not null,
	sumsps real not null,
	vehiclesingroups integer not null,
	vehiclesnotingroups integer not null,
	datetime timestamp not null
)
;

create table optimum
(
	id serial not null
		constraint id_unique3
			primary key,
	edges integer not null,
	vehicles integer not null,
	objectivevalue real not null,
	lpt real not null,
	datetime timestamp not null
)
;

create table candidategroupssd
(
	id serial not null
		constraint id_uniquesd
			primary key,
	edges integer not null,
	vehicles integer not null,
	datetime timestamp default now() not null,
	groupsetid integer
)
;

create unique index candidategroupssd_groupsetid_uindex
	on candidategroupssd (groupsetid)
;

create table groupset
(
	id serial not null
		constraint groupset_pkey
			primary key,
	groupsetid integer not null
		constraint groupset_groupsetid_fkey
			references candidategroups (groupsetid)
				on delete cascade,
	vehicles integer[] not null
)
;

create unique index groupset_id_uindex
	on groupset (id)
;

create table groupsetting
(
	groupset_id integer not null
		constraint groupsetting_pkey
			primary key
)
;

create table formingsd
(
	fsd_id integer not null
		constraint formingsd_pkey
			primary key,
	groupset_id integer not null
		constraint fk_sd_groupset_id
			references groupsetting
				on delete cascade
)
;

create table formingconvex
(
	fc_id integer not null
		constraint formingconvex_pkey
			primary key,
	groupset_id integer not null
		constraint fk_convex_groupset_id
			references groupsetting
				on delete cascade
)
;

create table groups
(
	g_id integer not null
		constraint groups_pkey
			primary key,
	groupset_id integer not null
		constraint fk_groups_id
			references groupsetting
				on delete cascade
)
;

