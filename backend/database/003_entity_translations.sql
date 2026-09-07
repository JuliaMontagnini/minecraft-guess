USE minecraft_guess;


CREATE TABLE IF NOT EXISTS entity_translations (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    entity_id BIGINT UNSIGNED NOT NULL,

    locale VARCHAR(20) NOT NULL,

    translated_name VARCHAR(255) NOT NULL,

    source VARCHAR(100) NOT NULL,

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_entity_translation
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_entity_translation
        UNIQUE (
            entity_id,
            locale
        )
);