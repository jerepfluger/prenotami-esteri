create schema base_schema;

create table if not exists base_schema.base_table(
    id int auto_increment primary key
);

-- auto-generated definition
create table appointment
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
