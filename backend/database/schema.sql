CREATE DATABASE IF NOT EXISTS minecraft_guess
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE minecraft_guess;


-- =========================================================
-- ENTIDADE BASE
-- =========================================================

CREATE TABLE IF NOT EXISTS entities (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    external_id VARCHAR(191) NOT NULL,

    entity_type VARCHAR(30) NOT NULL,

    name VARCHAR(255) NOT NULL,

    category VARCHAR(100) NOT NULL,

    version_added VARCHAR(100) NOT NULL,

    notes TEXT NOT NULL,

    raw_payload JSON NOT NULL,

    collected_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT chk_entity_type
        CHECK (
            entity_type IN (
                'mob',
                'biome',
                'item',
                'structure',
                'enchantment'
            )
        ),

    CONSTRAINT uq_entity_external
        UNIQUE (entity_type, external_id)
);


-- =========================================================
-- MOBS
-- =========================================================

CREATE TABLE IF NOT EXISTS mobs (
    entity_id BIGINT UNSIGNED PRIMARY KEY,

    mob_type VARCHAR(100) NOT NULL,

    hp INT UNSIGNED NOT NULL,

    damage_easy INT UNSIGNED NOT NULL,
    damage_normal INT UNSIGNED NOT NULL,
    damage_hard INT UNSIGNED NOT NULL,

    xp_min INT UNSIGNED NOT NULL,
    xp_max INT UNSIGNED NOT NULL,

    spawn_conditions TEXT NOT NULL,

    behavior TEXT NOT NULL,

    tameable BOOLEAN NOT NULL,

    taming_method TEXT NULL,

    breedable BOOLEAN NOT NULL,

    breeding_item VARCHAR(255) NULL,

    CONSTRAINT fk_mobs_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_mob_xp
        CHECK (xp_min <= xp_max)
);


CREATE TABLE IF NOT EXISTS mob_drops (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    mob_entity_id BIGINT UNSIGNED NOT NULL,

    item_name VARCHAR(255) NOT NULL,

    count_min INT UNSIGNED NOT NULL,

    count_max INT UNSIGNED NOT NULL,

    chance_raw DECIMAL(10,4) NOT NULL,

    CONSTRAINT fk_mob_drops_entity
        FOREIGN KEY (mob_entity_id)
        REFERENCES mobs(entity_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_mob_drop_count
        CHECK (count_min <= count_max)
);


-- =========================================================
-- BIOMAS
-- =========================================================

CREATE TABLE IF NOT EXISTS biomes (
    entity_id BIGINT UNSIGNED PRIMARY KEY,

    dimension VARCHAR(100) NOT NULL,

    temperature DECIMAL(8,4) NOT NULL,

    precipitation VARCHAR(100) NOT NULL,

    rarity VARCHAR(100) NOT NULL,

    color_grass VARCHAR(20) NOT NULL,

    color_water VARCHAR(20) NOT NULL,

    color_foliage VARCHAR(20) NOT NULL,

    color_sky VARCHAR(20) NOT NULL,

    CONSTRAINT fk_biomes_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE
);


-- =========================================================
-- ITENS
-- =========================================================

CREATE TABLE IF NOT EXISTS items (
    entity_id BIGINT UNSIGNED PRIMARY KEY,

    stack_size INT UNSIGNED NOT NULL,

    durability INT UNSIGNED NULL,

    description TEXT NOT NULL,

    enchantable BOOLEAN NOT NULL,

    food_hunger INT UNSIGNED NULL,

    food_saturation DECIMAL(10,4) NULL,

    fuel_value INT UNSIGNED NULL,

    crafting_recipe JSON NULL,

    CONSTRAINT fk_items_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE
);


-- =========================================================
-- ESTRUTURAS
-- =========================================================

CREATE TABLE IF NOT EXISTS structures (
    entity_id BIGINT UNSIGNED PRIMARY KEY,

    dimension VARCHAR(100) NOT NULL,

    rarity VARCHAR(100) NOT NULL,

    y_min INT NOT NULL,

    y_max INT NOT NULL,

    how_to_find TEXT NOT NULL,

    CONSTRAINT fk_structures_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_structure_y
        CHECK (y_min <= y_max)
);


CREATE TABLE IF NOT EXISTS structure_loot (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    structure_entity_id BIGINT UNSIGNED NOT NULL,

    item_name VARCHAR(255) NOT NULL,

    count_min INT UNSIGNED NOT NULL,

    count_max INT UNSIGNED NOT NULL,

    chance_raw DECIMAL(10,4) NOT NULL,

    CONSTRAINT fk_structure_loot_entity
        FOREIGN KEY (structure_entity_id)
        REFERENCES structures(entity_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_structure_loot_count
        CHECK (count_min <= count_max)
);


-- =========================================================
-- ENCANTAMENTOS
-- =========================================================

CREATE TABLE IF NOT EXISTS enchantments (
    entity_id BIGINT UNSIGNED PRIMARY KEY,

    max_level INT UNSIGNED NOT NULL,

    description TEXT NOT NULL,

    weight INT UNSIGNED NOT NULL,

    treasure_only BOOLEAN NOT NULL,

    curse_of BOOLEAN NOT NULL,

    CONSTRAINT fk_enchantments_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE
);


-- =========================================================
-- ATRIBUTOS QUE SÃO LISTAS
-- =========================================================

CREATE TABLE IF NOT EXISTS entity_list_values (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    entity_id BIGINT UNSIGNED NOT NULL,

    attribute_name VARCHAR(100) NOT NULL,

    position_index INT UNSIGNED NOT NULL,

    value TEXT NOT NULL,

    CONSTRAINT fk_list_entity
        FOREIGN KEY (entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_list_position
        UNIQUE (
            entity_id,
            attribute_name,
            position_index
        )
);


CREATE INDEX idx_list_entity_attribute
    ON entity_list_values (
        entity_id,
        attribute_name
    );


-- =========================================================
-- AUDITORIA DAS COLETAS
-- =========================================================

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    endpoint VARCHAR(100) NOT NULL,

    started_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    finished_at TIMESTAMP NULL,

    records_received INT UNSIGNED NOT NULL
        DEFAULT 0,

    records_accepted INT UNSIGNED NOT NULL
        DEFAULT 0,

    records_rejected INT UNSIGNED NOT NULL
        DEFAULT 0,

    status VARCHAR(30) NOT NULL
        DEFAULT 'running',

    error_message TEXT NULL,

    CONSTRAINT chk_ingestion_status
        CHECK (
            status IN (
                'running',
                'success',
                'partial',
                'failed'
            )
        )
);


CREATE TABLE IF NOT EXISTS ingestion_errors (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    ingestion_run_id BIGINT UNSIGNED NOT NULL,

    external_id VARCHAR(191) NULL,

    record_name VARCHAR(255) NULL,

    error_type VARCHAR(100) NOT NULL,

    error_message TEXT NOT NULL,

    raw_data JSON NULL,

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_ingestion_error_run
        FOREIGN KEY (ingestion_run_id)
        REFERENCES ingestion_runs(id)
        ON DELETE CASCADE
);