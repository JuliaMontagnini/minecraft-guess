import {
  useEffect,
  useState,
} from "react";

import type {
  SyntheticEvent,
} from "react";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  GuessHistory,
} from "../components/GuessHistory";

import {
  HintList,
} from "../components/HintList";

import {
  Lives,
} from "../components/Lives";

import {
  createGame,
  getGame,
  requestHint,
  submitGuess,
  type Category,
  type GameStatus,
} from "../services/gameApi";

import brownBackground from
  "../assets/fundo-quadriculado-marrom.png";

import greenBackground from
  "../assets/fundo-quadriculado-verde.png";


const MAX_LIVES = 5;


const categoryLabels:
  Record<string, string> = {
    mobs: "Mobs",
    biomes: "Biomas",
    items: "Itens",
    structures: "Estruturas",
    enchantments: "Encantamentos",
    random: "Aleatório",
  };


const validCategories: Category[] = [
  "mobs",
  "biomes",
  "items",
  "structures",
  "enchantments",
  "random",
];


export function GamePage() {
  const {
    category = "random",
    gameId,
  } = useParams();

  const navigate = useNavigate();


  const [answer, setAnswer] =
    useState("");

  const [lives, setLives] =
    useState(MAX_LIVES);

  const [guesses, setGuesses] =
    useState<string[]>([]);

  const [hints, setHints] =
    useState<string[]>([]);

  const [gameStatus, setGameStatus] =
    useState<GameStatus>("playing");

  const [
    secretAnswer,
    setSecretAnswer,
  ] =
    useState<string | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [
    initializing,
    setInitializing,
  ] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {
    if (!gameId) {
      setInitializing(false);
      return;
    }

    let cancelled = false;


    async function restoreGame() {
      try {
        const game = await getGame(
          gameId as string,
        );

        if (cancelled) {
          return;
        }

        setLives(
          game.lives,
        );

        setGameStatus(
          game.status,
        );

        setSecretAnswer(
          game.answer,
        );

        setGuesses(
          game.guesses
            .filter(
              (guess) =>
                !guess.correct,
            )
            .map(
              (guess) =>
                guess.guess,
            ),
        );

        setHints(
          game.hints.map(
            (hint) =>
              hint.hint,
          ),
        );

        setError(null);
      } catch (error) {
        if (cancelled) {
          return;
        }

        setError(
          error instanceof Error
            ? error.message
            : (
              "Não foi possível "
              + "recuperar a partida."
            ),
        );
      } finally {
        if (!cancelled) {
          setInitializing(false);
        }
      }
    }


    restoreGame();


    return () => {
      cancelled = true;
    };
  }, [gameId]);


  async function handleNewHint() {
    if (
      !gameId
      || loading
      || gameStatus !== "playing"
    ) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const result = await requestHint(
        gameId,
      );

      setHints(
        (current) => [
          ...current,
          result.hint,
        ],
      );

      setLives(
        result.lives,
      );

      setGameStatus(
        result.status,
      );

      if (result.answer) {
        setSecretAnswer(
          result.answer,
        );
      }
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : (
            "Não foi possível "
            + "obter a dica."
          ),
      );
    } finally {
      setLoading(false);
    }
  }


  async function handleGuess(
    event:
      SyntheticEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (
      !gameId
      || loading
      || gameStatus !== "playing"
    ) {
      return;
    }

    const cleanAnswer =
      answer.trim();

    if (!cleanAnswer) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const result =
        await submitGuess(
          gameId,
          cleanAnswer,
        );

      setLives(
        result.lives,
      );

      setGameStatus(
        result.status,
      );

      if (!result.correct) {
        setGuesses(
          (current) => [
            ...current,
            cleanAnswer,
          ],
        );
      }

      if (result.answer) {
        setSecretAnswer(
          result.answer,
        );
      }

      setAnswer("");
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : (
            "Não foi possível "
            + "enviar o palpite."
          ),
      );
    } finally {
      setLoading(false);
    }
  }


  async function handlePlayAgain() {
    if (loading) {
      return;
    }

    if (
      !validCategories.includes(
        category as Category,
      )
    ) {
      navigate("/");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const newGame =
        await createGame(
          category as Category,
        );

      navigate(
        `/game/${category}/${newGame.game_id}`,
      );
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : (
            "Não foi possível "
            + "iniciar outra partida."
          ),
      );
    } finally {
      setLoading(false);
    }
  }


  if (initializing) {
    return (
      <main
        className="
          flex
          min-h-screen
          items-center
          justify-center
          bg-[#8E5A2F]
          p-6
          text-[#F2F5D6]
        "
      >
        <p className="text-2xl">
          Carregando partida...
        </p>
      </main>
    );
  }


  if (!gameId) {
    return (
      <main
        className="
          flex
          min-h-screen
          items-center
          justify-center
          bg-[#8E5A2F]
          p-6
          text-[#F2F5D6]
        "
      >
        <div className="text-center">
          <p className="text-2xl">
            Partida inválida.
          </p>

          <button
            type="button"
            onClick={() =>
              navigate("/")
            }
            className="
              mt-6
              rounded-xl
              bg-[#F2F5D6]
              px-6
              py-3
              text-[#502D10]
            "
          >
            Voltar ao Menu
          </button>
        </div>
      </main>
    );
  }


  if (gameStatus === "won") {
    return (
      <main
        className="
          flex
          min-h-screen
          items-center
          justify-center
          bg-[#8E5A2F]
          p-6
        "
      >
        <div
          className="
            w-full
            max-w-lg
            rounded-2xl
            bg-[#F2F5D6]
            p-8
            text-center
            text-[#502D10]
          "
        >
          <h1
            className="
              mb-5
              text-3xl
            "
          >
            Parabéns! Você acertou!
          </h1>

          <Lives
            lives={lives}
          />

          <p
            className="
              mt-6
              text-2xl
            "
          >
            {secretAnswer}
          </p>

          <p className="mt-4">
            {hints.length} dica(s)
            {" • "}
            {guesses.length}
            {" "}
            palpite(s) errado(s)
          </p>


          {error && (
            <p
              className="
                mt-5
                rounded-lg
                bg-red-100
                px-4
                py-3
                text-red-700
              "
            >
              {error}
            </p>
          )}


          <div
            className="
              mt-8
              flex
              flex-wrap
              justify-center
              gap-4
            "
          >
            <button
              type="button"
              onClick={() =>
                navigate("/")
              }
              disabled={loading}
              className="
                rounded-lg
                bg-[#63C947]
                px-5
                py-3
                disabled:cursor-not-allowed
                disabled:opacity-50
              "
            >
              Menu
            </button>


            <button
              type="button"
              onClick={
                handlePlayAgain
              }
              disabled={loading}
              className="
                rounded-lg
                bg-[#63C947]
                px-5
                py-3
                disabled:cursor-not-allowed
                disabled:opacity-50
              "
            >
              {loading
                ? "Criando partida..."
                : "Jogar novamente"}
            </button>
          </div>
        </div>
      </main>
    );
  }


  if (gameStatus === "lost") {
    return (
      <main
        className="
          flex
          min-h-screen
          items-center
          justify-center
          bg-[#8E5A2F]
          p-6
        "
      >
        <div
          className="
            w-full
            max-w-lg
            rounded-2xl
            bg-[#F2F5D6]
            p-8
            text-center
            text-[#502D10]
          "
        >
          <h1
            className="
              mb-5
              text-3xl
            "
          >
            Game Over
          </h1>

          <Lives
            lives={0}
          />

          <p className="mt-6">
            A resposta era:
          </p>

          <p
            className="
              mt-2
              text-2xl
            "
          >
            {secretAnswer}
          </p>

          <p className="mt-4">
            {hints.length} dica(s)
            {" • "}
            {guesses.length}
            {" "}
            palpite(s) errado(s)
          </p>


          {error && (
            <p
              className="
                mt-5
                rounded-lg
                bg-red-100
                px-4
                py-3
                text-red-700
              "
            >
              {error}
            </p>
          )}


          <div
            className="
              mt-8
              flex
              flex-wrap
              justify-center
              gap-4
            "
          >
            <button
              type="button"
              onClick={() =>
                navigate("/")
              }
              disabled={loading}
              className="
                rounded-lg
                bg-[#63C947]
                px-5
                py-3
                disabled:cursor-not-allowed
                disabled:opacity-50
              "
            >
              Menu
            </button>


            <button
              type="button"
              onClick={
                handlePlayAgain
              }
              disabled={loading}
              className="
                rounded-lg
                bg-[#63C947]
                px-5
                py-3
                disabled:cursor-not-allowed
                disabled:opacity-50
              "
            >
              {loading
                ? "Criando partida..."
                : "Jogar novamente"}
            </button>
          </div>
        </div>
      </main>
    );
  }


  return (
    <main
      className="
        min-h-screen
        text-[#F2F5D6]
      "
      style={{
        backgroundColor:
          "#8E5A2F",

        backgroundImage:
          `url(${brownBackground})`,

        backgroundRepeat:
          "repeat",
      }}
    >
      <header
        className="
          flex
          min-h-28
          items-center
          justify-center
          px-6
          md:min-h-40
        "
        style={{
          backgroundColor:
            "rgba(78, 165, 51, 0.62)",

          backgroundImage:
            `url(${greenBackground})`,

          backgroundSize:
            "cover",
        }}
      >
        <h1
          className="
            text-4xl
            md:text-6xl
          "
        >
          MinecraftGuess
        </h1>
      </header>


      <div
        className="
          mx-auto
          flex
          w-full
          max-w-xl
          flex-col
          items-center
          gap-10
          px-6
          py-12
        "
      >
        <section
          className="
            flex
            w-full
            flex-col
            items-center
            gap-6
          "
        >
          <p
            className="
              text-center
              text-xl
              md:text-2xl
            "
          >
            Categoria:{" "}
            {
              categoryLabels[
                category
              ]
              ?? category
            }
          </p>


          <form
            onSubmit={
              handleGuess
            }
            className="
              flex
              w-full
              flex-col
              items-center
              gap-6
            "
          >
            <input
              type="text"
              value={answer}
              onChange={
                (event) =>
                  setAnswer(
                    event.target.value,
                  )
              }
              disabled={loading}
              placeholder=
                "Insira seu palpite..."
              className="
                w-full
                max-w-md
                rounded-xl
                bg-[#F2F5D6]
                px-6
                py-4
                text-center
                text-lg
                text-[#502D10]
                outline-none
                placeholder:text-[#502D10]/50
                focus:ring-4
                focus:ring-[#63C947]
                disabled:opacity-60
              "
            />


            <Lives
              lives={lives}
            />


            {error && (
              <p
                className="
                  rounded-lg
                  bg-[#F2F5D6]
                  px-4
                  py-3
                  text-center
                  text-red-700
                "
              >
                {error}
              </p>
            )}


            <div
              className="
                flex
                w-full
                flex-col
                justify-center
                gap-4
                sm:flex-row
              "
            >
              <button
                type="button"
                onClick={
                  handleNewHint
                }
                disabled={loading}
                className="
                  rounded-xl
                  bg-[#F2F5D6]
                  px-6
                  py-3
                  text-[#502D10]
                  shadow
                  disabled:cursor-not-allowed
                  disabled:opacity-50
                "
              >
                {loading
                  ? "Aguarde..."
                  : "Nova dica"}
              </button>


              <button
                type="submit"
                disabled={loading}
                className="
                  rounded-xl
                  bg-[#F2F5D6]
                  px-6
                  py-3
                  text-[#502D10]
                  shadow
                  disabled:cursor-not-allowed
                  disabled:opacity-50
                "
              >
                Enviar palpite
              </button>


              <button
                type="button"
                onClick={() =>
                  navigate("/")
                }
                disabled={loading}
                className="
                  rounded-xl
                  bg-[#F2F5D6]
                  px-6
                  py-3
                  text-[#502D10]
                  shadow
                  disabled:cursor-not-allowed
                  disabled:opacity-50
                "
              >
                Voltar ao Menu
              </button>
            </div>
          </form>
        </section>


        <GuessHistory
          guesses={guesses}
        />


        <HintList
          hints={hints}
        />
      </div>


      <footer
        className="
          p-8
          text-center
        "
      >
        <a
          href=
            "https://api.astroworldmc.com"
          target="_blank"
          rel="noopener noreferrer"
          className="
            underline
            underline-offset-4
          "
        >
          Powered by Astroworld API
        </a>
      </footer>
    </main>
  );
}