USE sbha;

CREATE TABLE bot (
   bot_id CHAR(255),
   bot_name VARCHAR(50) NOT NULL,
   bot_dob DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
   bot_mnemonic VARCHAR(255) NOT NULL, -- a verif
   bot_role VARCHAR(255),
   PRIMARY KEY(bot_id),
   UNIQUE(bot_key)
);