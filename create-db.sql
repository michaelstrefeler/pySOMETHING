#------------------------------------------------------------
#        Script MySQL.
#------------------------------------------------------------

DROP DATABASE IF EXISTS pysomething;
CREATE DATABASE pysomething;
USE pysomething;

#------------------------------------------------------------
# t_user
#------------------------------------------------------------

CREATE TABLE t_user(
        idUser    int (11) Auto_increment  NOT NULL ,
        use_name  Varchar (100) NOT NULL ,
        use_email Varchar (255) NOT NULL ,
        password  Varchar (100) NOT NULL ,
        PRIMARY KEY (idUser )
)ENGINE=InnoDB;


#------------------------------------------------------------
# t_list
#------------------------------------------------------------

CREATE TABLE t_list(
        idList    int (11) Auto_increment  NOT NULL ,
        lis_title Varchar (100) NOT NULL ,
        lis_author VARCHAR(255) NOT NULL,
        PRIMARY KEY (idList )
)ENGINE=InnoDB;


#------------------------------------------------------------
# t_item
#------------------------------------------------------------

CREATE TABLE t_item(
        idItem          int (11) Auto_increment  NOT NULL ,
        ite_description Varchar (100) NOT NULL ,
        ite_is_done     Bool NOT NULL DEFAULT '0',
        for_list        int(5) NOT NULL,
        PRIMARY KEY (idItem )
)ENGINE=InnoDB;


#------------------------------------------------------------
# t_calendar
#------------------------------------------------------------

CREATE TABLE t_calendar(
        idCalendar int (11) Auto_increment  NOT NULL ,
        cal_title  Varchar (100) NOT NULL ,
        PRIMARY KEY (idCalendar )
)ENGINE=InnoDB;


#------------------------------------------------------------
# t_event
#------------------------------------------------------------

CREATE TABLE t_event(
        idEvent         int (11) Auto_increment  NOT NULL ,
        eve_title       Varchar (150) NOT NULL ,
        eve_description Text NOT NULL ,
        eve_location    Text ,
        eve_start_time  Datetime NOT NULL ,
        eve_end_time    Datetime ,
        PRIMARY KEY (idEvent )
)ENGINE=InnoDB;


#------------------------------------------------------------
# cal_events
#------------------------------------------------------------

CREATE TABLE cal_events(
        idCalendar Int NOT NULL ,
        idEvent    Int NOT NULL ,
        PRIMARY KEY (idCalendar ,idEvent )
)ENGINE=InnoDB;


#------------------------------------------------------------
# uses
#------------------------------------------------------------

CREATE TABLE uses(
        idUser     Int NOT NULL ,
        idCalendar Int NOT NULL ,
        PRIMARY KEY (idUser ,idCalendar )
)ENGINE=InnoDB;

ALTER TABLE cal_events ADD CONSTRAINT FK_cal_events_idCalendar FOREIGN KEY (idCalendar) REFERENCES t_calendar(idCalendar);
ALTER TABLE cal_events ADD CONSTRAINT FK_cal_events_idEvent FOREIGN KEY (idEvent) REFERENCES t_event(idEvent);
ALTER TABLE uses ADD CONSTRAINT FK_uses_idUser FOREIGN KEY (idUser) REFERENCES t_user(idUser);
ALTER TABLE uses ADD CONSTRAINT FK_uses_idCalendar FOREIGN KEY (idCalendar) REFERENCES t_calendar(idCalendar);
