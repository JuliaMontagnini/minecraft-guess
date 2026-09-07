USE minecraft_guess;


CREATE TABLE IF NOT EXISTS games (
    id CHAR(36) PRIMARY KEY,

    secret_entity_id BIGINT UNSIGNED NOT NULL,

    requested_category VARCHAR(30) NOT NULL,

    lives_remaining TINYINT UNSIGNED NOT NULL
        DEFAULT 10,

    status VARCHAR(20) NOT NULL
        DEFAULT 'playing',

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    finished_at TIMESTAMP NULL,

    CONSTRAINT fk_games_secret
        FOREIGN KEY (secret_entity_id)
        REFERENCES entities(id),

    CONSTRAINT chk_game_status
        CHECK (
            status IN (
                'playing',
                'won',
                'lost'
            )
        ),

    CONSTRAINT chk_game_lives
        CHECK (
            lives_remaining <= 10
        )
);


CREATE TABLE IF NOT EXISTS game_guesses (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    game_id CHAR(36) NOT NULL,

    guess_text VARCHAR(255) NOT NULL,

    correct BOOLEAN NOT NULL,

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_game_guesses_game
        FOREIGN KEY (game_id)
        REFERENCES games(id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS game_hints (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    game_id CHAR(36) NOT NULL,

    hint_number INT UNSIGNED NOT NULL,

    hint_text TEXT NOT NULL,

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_game_hints_game
        FOREIGN KEY (game_id)
        REFERENCES games(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_game_hint
        UNIQUE (
            game_id,
            hint_number
        )
);