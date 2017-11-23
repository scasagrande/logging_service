drop table if exists messages;
drop table if exists loglevels;

create table loglevels (
 id integer primary key,
 name text not null
);

insert into loglevels (id, name)
values  (0, 'info'),
        (1, 'warning'),
        (2, 'error');

create table messages (
  id integer primary key autoincrement,
  clientid integer not null,
  loglevel integer not null,
  message text not null,
  FOREIGN KEY(loglevel) REFERENCES loglevels(id)
);
