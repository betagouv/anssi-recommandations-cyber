ALTER TABLE interactions ADD COLUMN id_conversation TEXT;

ALTER TABLE interactions
    ADD CONSTRAINT clef_interaction_conversation
    FOREIGN KEY (id_conversation)
    REFERENCES conversations (id);

INSERT INTO conversations (id)
SELECT id_interaction FROM interactions;

UPDATE interactions
SET id_conversation = id_interaction;
