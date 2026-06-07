create table users (
  id bigint generated always as identity primary key,
  username text not null unique,
  email text not null unique,
  password_hash text not null,
  role text not null,
  created_at timestamp default current_timestamp
)


create table games (
  id bigint generated always as identity primary key,
  name text not null unique
)

create table tournaments (
  id bigint generated always as identity primary key,
  game_id bigint not null,
  name text not null,
  description text,
  start_date date,
  end_date date,
  status text not null,
  max_teams integer,
  created_by bigint,

  foreign key (game_id) references games(id),
  foreign key (created_by) references users(id)
)

create table teams (
  id bigint generated always as identity primary key,
  name text not null,
  captain_id bigint,
  created_at timestamp default current_timestamp,

  foreign key (captain_id) references users(id)
)

create table team_members (
  id bigint generated always as identity primary key,
  team_id bigint not null,
  user_id bigint not null,
  joined_at timestamp default current_timestamp,

  foreign key (team_id) references teams(id),
  foreign key (user_id) references users(id)
)

create table tournament_registrations (
  id bigint generated always as identity primary key,
  tournament_id bigint not null,
  team_id bigint not null,
  registration_date timestamp default current_timestamp,
  status text not null,

  foreign key (tournament_id) references tournaments(id) on delete cascade,
  foreign key (team_id) references teams(id) on delete cascade
)

create table matches(
  id bigint generated always as identity primary key,
  tournament_id bigint not null,
  team1_id bigint not null,
  team2_id bigint not null,
  match_date timestamp,
  status text not null,
  round_name text,

  foreign key (tournament_id) references tournaments(id),
  foreign key (team1_id) references teams(id),
  foreign key (team2_id) references teams(id)
)

create table match_results (
  id bigint generated always as identity primary key,
  match_id bigint not null,
  winner_team_id bigint,
  score_team1 integer not null,
  score_team2 integer not null,

  foreign key (match_id) references matches(id) on delete cascade,
  foreign key (winner_team_id) references teams(id)
)