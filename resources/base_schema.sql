create schema prenotami_esteri;

create table if not exists prenotami_esteri.base_table(
    id int auto_increment primary key
);

-- auto-generated definition
create table prenotami_esteri.appointment if not exists
(
    id                     int auto_increment
        primary key,
    timestamp              timestamp   null,
    last_updated           timestamp   null,
    username               varchar(30) null,
    password               varchar(20) null,
    appointment_type       varchar(15) null,
    address                varchar(50) null,
    have_kids              varchar(2)  null,
    marital_status         varchar(15) null,
    is_passport_expired    varchar(2)  null,
    amount_minor_kids      int         null,
    passport_expiry_date   varchar(10) null,
    travel_reason          varchar(15) null,
    height                 int         null,
    zip_code               varchar(6)  null,
    other_citizenship      varchar(15) null,
    multiple_appointment   tinyint(1)  null,
    additional_people_data text        null,
    scheduled_appointment  tinyint(1)  null
);

create table prenotami_esteri.login_credentials if not exists
(
    id int auto_increment primary key,
    username varchar(30),
    password varchar(20)
);


create table prenotami_esteri.multiple_passport_appointment if not exists
(
    id int auto_increment primary key,
    created_at timestamp,
    last_updated_at timestamp,
    login_credentials_id int,
    address varchar(50),
    have_kids varchar(2),
    marital_status varchar(15),
    own_expired_passport varchar(2),
    minor_kids_amount int,
    additional_notes text
    scheduled tinyint(1),
    foreign key (login_credentials_id) references prenotami_esteri.login_credentials(id)
);

create table prenotami_esteri.multiple_passport_additional_people_data if not exists
(
    id int auto_increment primary key,
    multiple_passport_appointment_id int,
    last_name varchar(30),
    first_name varchar(30),
    date_of_birth varchar(10),
    relationship varchar(15),
    have_kids varchar(2),
    marital_status varchar(15),
    address varchar(50)
    foreign key (multiple_passport_appointment_id) references prenotami_esteri.multiple_passport_appointment(id)
);
