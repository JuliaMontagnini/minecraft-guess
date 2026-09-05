import { FormEvent, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { GuessHistory } from "../components/GuessHistory";
import { HintList } from "../components/HintList";
import { Lives } from "../components/Lives";

import brownBackground from "../assets/fundo-quadriculado-marrom.png";
import greenBackground from "../assets/fundo-quadriculado-verde.png";

const MAX_LIVES = 5;

/*
  Dados temporários.

  Mais tarde isto será substituído
  pelos dados recebidos da nossa API AWS.
*/
const mockGame = {
  secret: "Plains",

  hints: [
    "Sou encontrado no Overworld.",
    "Tenho terreno predominantemente plano.",
    "Aldeias podem ser encontradas em mim.",
    "Sou um dos biomas mais conhecidos do Minecraft.",
  ],
};

const categoryLabels: Record<string, string> = {
  mobs: "Mobs",
  biomes: "Biomas",
  items: "Itens",
  structures: "Estruturas",
  enchantments: "Encantamentos",
  random: "Aleatório",
};

export function GamePage() {
  const { category = "random" } = useParams();

  const navigate = useNavigate();

  const [answer, setAnswer] = useState("");
  const [lives, setLives] = useState(MAX_LIVES);

  const [guesses, setGuesses] = useState<string[]>([]);

  const [visibleHintCount, setVisibleHintCount] =
    useState(0);

  const [gameStatus, setGameStatus] =
    useState<"playing" | "won" | "lost">("playing");

  const visibleHints = mockGame.hints.slice(
    0,
    visibleHintCount,
  );

  function loseLife() {
    setLives((currentLives) => {
      const newLives = currentLives - 1;

      if (newLives <= 0) {
        setGameStatus("lost");
        return 0;
      }

      return newLives;
    });
  }

  function handleNewHint() {
    if (
      gameStatus !== "playing" ||
      lives <= 0 ||
      visibleHintCount >= mockGame.hints.length
    ) {
      return;
    }

    setVisibleHintCount((count) => count + 1);

    loseLife();
  }

  function handleGuess(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const cleanAnswer = answer.trim();

    if (!cleanAnswer || gameStatus !== "playing") {
      return;
    }

    const isCorrect =
      cleanAnswer.localeCompare(
        mockGame.secret,
        undefined,
        {
          sensitivity: "accent",
        },
      ) === 0;

    if (isCorrect) {
      setGameStatus("won");
      return;
    }

    setGuesses((current) => [
      ...current,
      cleanAnswer,
    ]);

    setAnswer("");

    loseLife();
  }

  if (gameStatus === "won") {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#8E5A2F] p-6">
        <div className="w-full max-w-lg rounded-2xl bg-[#F2F5D6] p-8 text-center text-[#502D10]">
          <h1 className="mb-5 text-3xl">
            Parabéns! Você acertou!
          </h1>

          <Lives lives={lives} />

          <p className="mt-6 text-2xl">
            {mockGame.secret}
          </p>

          <p className="mt-4">
            {visibleHintCount} dica(s) • {guesses.length} palpite(s) errado(s)
          </p>

          <div className="mt-8 flex justify-center gap-4">
            <button
              type="button"
              onClick={() => navigate("/")}
              className="rounded-lg bg-[#F2F5D6] px-5 py-3 shadow"
            >
              Menu
            </button>

            <button
              type="button"
              onClick={() => window.location.reload()}
              className="rounded-lg bg-[#F2F5D6] px-5 py-3 shadow"
            >
              Jogar novamente
            </button>
          </div>
        </div>
      </main>
    );
  }

  if (gameStatus === "lost") {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#8E5A2F] p-6">
        <div className="w-full max-w-lg rounded-2xl bg-[#F2F5D6] p-8 text-center text-[#502D10]">
          <h1 className="mb-5 text-3xl">
            Game Over
          </h1>

          <Lives lives={0} />

          <p className="mt-6">
            A resposta era:
          </p>

          <p className="mt-2 text-2xl">
            {mockGame.secret}
          </p>

          <p className="mt-4">
            {visibleHintCount} dica(s) • {guesses.length} palpite(s) errado(s)
          </p>

          <div className="mt-8 flex justify-center gap-4">
            <button
              type="button"
              onClick={() => navigate("/")}
              className="rounded-lg bg-[#F2F5D6] px-5 py-3 shadow"
            >
              Menu
            </button>

            <button
              type="button"
              onClick={() => window.location.reload()}
              className="rounded-lg bg-[#F2F5D6] px-5 py-3 shadow"
            >
              Jogar novamente
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main
      className="min-h-screen text-[#F2F5D6]"
      style={{
        backgroundColor: "#8E5A2F",
        backgroundImage: `url(${brownBackground})`,
        backgroundRepeat: "repeat",
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
          backgroundColor: "rgba(78, 165, 51, 0.62)",
          backgroundImage: `url(${greenBackground})`,
          backgroundSize: "cover",
        }}
      >
        <h1 className="text-4xl md:text-6xl">
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
        <section className="flex w-full flex-col items-center gap-6">
          <p className="text-center text-xl md:text-2xl">
            Categoria:{" "}
            {categoryLabels[category] ?? category}
          </p>

          <form
            onSubmit={handleGuess}
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
              onChange={(event) =>
                setAnswer(event.target.value)
              }
              placeholder="Insira seu palpite..."
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
              "
            />

            <Lives lives={lives} />

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
                onClick={handleNewHint}
                disabled={
                  visibleHintCount >=
                  mockGame.hints.length
                }
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
                Nova dica
              </button>

              <button
                type="submit"
                className="
                  rounded-xl
                  bg-[#F2F5D6]
                  px-6
                  py-3
                  text-[#502D10]
                  shadow
                "
              >
                Enviar palpite
              </button>

              <button
                type="button"
                onClick={() => navigate("/")}
                className="
                  rounded-xl
                  bg-[#F2F5D6]
                  px-6
                  py-3
                  text-[#502D10]
                  shadow
                "
              >
                Voltar ao Menu
              </button>
            </div>
          </form>
        </section>

        <GuessHistory guesses={guesses} />

        <HintList hints={visibleHints} />
      </div>

      <footer className="p-8 text-center">
        <a
          href="https://api.astroworldmc.com"
          target="_blank"
          rel="noopener noreferrer"
          className="underline"
        >
          Powered by Astroworld API
        </a>
      </footer>
    </main>
  );
}