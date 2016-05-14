create table if not exists nodes (
	id  integer not null, 
	lat real not null, 
	lon real not null,
	user text not null,
	uid integer not null,
	version text not null,
	changeset integer not null,
	timestamp text not null,
	primary key(id)
);

create table if not exists nodes_tags (
	id integer not null,
	key text not null,
	value text not null,
	type text not null,
	primary key (id, key, type),
	foreign key(id) references nodes(id)
);

create table if not exists ways (
	id  integer not null, 
	user text not null,
	uid integer not null,
	version text not null, 
	changeset integer not null,
	timestamp text not null,
	primary key(id)	
);

create table if not exists ways_nodes (
	id integer not null,
	node_id integer not null,
	position integer not null,
	foreign key(id) references ways(id)
);

create table if not exists ways_tags (
	id integer not null,
	key text not null,
	value text not null,
	type text not null,
	primary key (id, key, type),
	foreign key(id) references ways(id)
);



	