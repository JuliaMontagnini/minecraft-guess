USE minecraft_guess;


ALTER TABLE games
    DROP CHECK chk_game_lives;


ALTER TABLE games
    MODIFY lives_remaining
        TINYINT UNSIGNED
        NOT NULL
        DEFAULT 10;


ALTER TABLE games
    ADD CONSTRAINT chk_game_lives
        CHECK (
            lives_remaining <= 10
        );