CREATE TABLE IF NOT EXISTS entity_media (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    entity_id BIGINT UNSIGNED NOT NULL,

    source VARCHAR(50) NOT NULL,

    source_page_url TEXT NOT NULL,

    file_name VARCHAR(255) NULL,

    image_url TEXT NULL,

    license_note VARCHAR(255) NULL,

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_entity_media_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_entity_media_source
        UNIQUE (
            entity_id,
            source
        )
);
