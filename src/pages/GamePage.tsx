import {
  useEffect,
  useRef,
  useState,
} from "react";

import type {
  CSSProperties,
  KeyboardEvent,
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
  getEntitySuggestions,
  getGame,
  requestHint,
  submitGuess,
  type Category,
  type EntitySuggestion,
  type GameStatus,
} from "../services/gameApi";

import brownBackground from
  "../assets/fundo-quadriculado-marrom.png";

import greenBackground from
  "../assets/fundo-quadriculado-verde.png";


const pageBackgroundStyle:
  CSSProperties = {
    backgroundColor:
      "#8E5A2F",

    backgroundImage:
      `url(${brownBackground})`,

    backgroundRepeat:
      "repeat",

    backgroundSize:
      "auto",
  };


const MAX_LIVES = 10;

const MAX_HINTS = 5;

const MAX_SUGGESTIONS = 6;

const SUGGESTION_DELAY_MS = 150;

const MIN_SUGGESTION_LENGTH = 2;


const categoryLabels:
  Record<string, string> = {
    mobs: "Mobs",
    biomes: "Biomas",
    items: "Itens",
    structures: "Estruturas",
    enchantments: "Encantamentos",
    random: "Aleatório",
  };


const validCategories:
  Category[] = [
    "mobs",
    "biomes",
    "items",
    "structures",
    "enchantments",
    "random",
  ];


function GameBanner() {
  return (
    <header
      className="
        flex
        min-h-28
        items-center
        justify-center
        px-6
        text-[#F2F5D6]
        md:min-h-40
      "
      style={{
        backgroundColor:
          "rgba(78, 165, 51, 0.62)",

        backgroundImage:
          `url(${greenBackground})`,

        backgroundSize:
          "cover",

        backgroundPosition:
          "center",
      }}
    >
      <h1
        className="
          text-center
          text-4xl
          md:text-6xl
        "
      >
        MinecraftGuess
      </h1>
    </header>
  );
}


export function GamePage() {
  const {
    category = "random",
    gameId,
  } = useParams();


  const navigate =
    useNavigate();


  const suggestionContainerRef =
    useRef<HTMLDivElement | null>(
      null,
    );


  const [
    answer,
    setAnswer,
  ] = useState("");


  const [
    lives,
    setLives,
  ] = useState(
    MAX_LIVES,
  );


  const [
    guesses,
    setGuesses,
  ] = useState<string[]>(
    [],
  );


  const [
    hints,
    setHints,
  ] = useState<string[]>(
    [],
  );


  const [
    gameStatus,
    setGameStatus,
  ] = useState<GameStatus>(
    "playing",
  );


  const [
    secretAnswer,
    setSecretAnswer,
  ] = useState<
    string | null
  >(null);


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    initializing,
    setInitializing,
  ] = useState(true);


  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);


  // =====================================================
  // ESTADOS DO AUTOCOMPLETE
  // =====================================================

  const [
    suggestions,
    setSuggestions,
  ] = useState<
    EntitySuggestion[]
  >([]);


  const [
    suggestionOpen,
    setSuggestionOpen,
  ] = useState(false);


  const [
    suggestionLoading,
    setSuggestionLoading,
  ] = useState(false);


  const [
    selectedSuggestionIndex,
    setSelectedSuggestionIndex,
  ] = useState(-1);


  const [
    inputFocused,
    setInputFocused,
  ] = useState(false);


  const [
    suppressSuggestions,
    setSuppressSuggestions,
  ] = useState(false);


  const suggestionCategory:
    Category =
      validCategories.includes(
        category as Category,
      )
        ? category as Category
        : "random";


  // =====================================================
  // RECUPERAR PARTIDA
  // =====================================================

  useEffect(() => {
    if (!gameId) {
      setInitializing(
        false,
      );

      return;
    }


    let cancelled = false;


    setInitializing(true);

    setError(null);


    async function restoreGame() {
      try {
        const game =
          await getGame(
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


        setAnswer("");

        setSuggestions([]);

        setSuggestionOpen(false);

        setSelectedSuggestionIndex(
          -1,
        );

        setSuppressSuggestions(
          false,
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
          setInitializing(
            false,
          );
        }
      }
    }


    restoreGame();


    return () => {
      cancelled = true;
    };
  }, [gameId]);


  // =====================================================
  // BUSCAR SUGESTÕES
  // =====================================================

  useEffect(() => {
    const cleanQuery =
      answer.trim();


    if (
      !inputFocused
      || suppressSuggestions
      || loading
      || gameStatus !== "playing"
      || cleanQuery.length
        < MIN_SUGGESTION_LENGTH
    ) {
      setSuggestions([]);

      setSuggestionOpen(false);

      setSuggestionLoading(false);

      setSelectedSuggestionIndex(
        -1,
      );

      return;
    }


    const controller =
      new AbortController();


    const timeout =
      window.setTimeout(
        async () => {
          try {
            setSuggestionLoading(
              true,
            );


            const result =
              await getEntitySuggestions(
                cleanQuery,
                suggestionCategory,
                MAX_SUGGESTIONS,
                controller.signal,
              );


            if (
              controller.signal.aborted
            ) {
              return;
            }


            setSuggestions(
              result,
            );

            setSelectedSuggestionIndex(
              -1,
            );

            setSuggestionOpen(
              true,
            );
          } catch (error) {
            if (
              error instanceof DOMException
              && error.name
                === "AbortError"
            ) {
              return;
            }


            setSuggestions([]);

            setSuggestionOpen(
              false,
            );
          } finally {
            if (
              !controller.signal.aborted
            ) {
              setSuggestionLoading(
                false,
              );
            }
          }
        },
        SUGGESTION_DELAY_MS,
      );


    return () => {
      window.clearTimeout(
        timeout,
      );

      controller.abort();
    };
  }, [
    answer,
    gameStatus,
    inputFocused,
    loading,
    suggestionCategory,
    suppressSuggestions,
  ]);


  // =====================================================
  // FECHAR POPUP AO CLICAR FORA
  // =====================================================

  useEffect(() => {
    function handleMouseDown(
      event: MouseEvent,
    ) {
      const container =
        suggestionContainerRef.current;


      if (
        container
        && !container.contains(
          event.target as Node,
        )
      ) {
        setSuggestionOpen(
          false,
        );

        setSelectedSuggestionIndex(
          -1,
        );
      }
    }


    document.addEventListener(
      "mousedown",
      handleMouseDown,
    );


    return () => {
      document.removeEventListener(
        "mousedown",
        handleMouseDown,
      );
    };
  }, []);


  // =====================================================
  // ALTERAR CAMPO DE PALPITE
  // =====================================================

  function handleAnswerChange(
    value: string,
  ) {
    setAnswer(
      value,
    );

    setSuppressSuggestions(
      false,
    );

    setSelectedSuggestionIndex(
      -1,
    );


    if (
      value.trim().length
      < MIN_SUGGESTION_LENGTH
    ) {
      setSuggestions([]);

      setSuggestionOpen(
        false,
      );
    }
  }


  // =====================================================
  // ESCOLHER UMA SUGESTÃO
  // =====================================================

  function selectSuggestion(
    suggestion:
      EntitySuggestion,
  ) {
    setAnswer(
      suggestion.name,
    );


    setSuggestions([]);


    setSuggestionOpen(
      false,
    );


    setSelectedSuggestionIndex(
      -1,
    );


    // Impede que a busca abra novamente
    // apenas porque o campo foi preenchido
    // programaticamente.
    setSuppressSuggestions(
      true,
    );
  }


  // =====================================================
  // TECLADO DO AUTOCOMPLETE
  // =====================================================

  function handleInputKeyDown(
    event:
      KeyboardEvent<HTMLInputElement>,
  ) {
    if (
      event.key === "Escape"
      && suggestionOpen
    ) {
      event.preventDefault();

      setSuggestionOpen(
        false,
      );

      setSelectedSuggestionIndex(
        -1,
      );

      return;
    }


    if (
      !suggestionOpen
      || suggestions.length === 0
    ) {
      return;
    }


    if (
      event.key === "ArrowDown"
    ) {
      event.preventDefault();


      setSelectedSuggestionIndex(
        (current) => {
          if (
            current
            >= suggestions.length - 1
          ) {
            return 0;
          }

          return current + 1;
        },
      );

      return;
    }


    if (
      event.key === "ArrowUp"
    ) {
      event.preventDefault();


      setSelectedSuggestionIndex(
        (current) => {
          if (
            current <= 0
          ) {
            return (
              suggestions.length - 1
            );
          }

          return current - 1;
        },
      );

      return;
    }


    if (
      event.key === "Enter"
      && selectedSuggestionIndex
        >= 0
    ) {
      const selected =
        suggestions[
          selectedSuggestionIndex
        ];


      if (selected) {
        event.preventDefault();

        selectSuggestion(
          selected,
        );
      }
    }
  }


  // =====================================================
  // PEDIR NOVA DICA
  // =====================================================

  async function handleNewHint() {
    if (
      !gameId
      || loading
      || gameStatus !== "playing"
      || hints.length
        >= MAX_HINTS
    ) {
      return;
    }


    try {
      setLoading(true);

      setError(null);


      setSuggestionOpen(
        false,
      );


      const result =
        await requestHint(
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


  // =====================================================
  // ENVIAR PALPITE
  // =====================================================

  async function handleGuess(
    event:
      SyntheticEvent<
        HTMLFormElement
      >,
  ) {
    event.preventDefault();


    if (
      !gameId
      || loading
      || gameStatus
        !== "playing"
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


      setSuggestions([]);

      setSuggestionOpen(
        false,
      );

      setSelectedSuggestionIndex(
        -1,
      );


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

      setSuppressSuggestions(
        false,
      );
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


  // =====================================================
  // JOGAR NOVAMENTE
  // =====================================================

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


  // =====================================================
  // CARREGAMENTO
  // =====================================================

  if (initializing) {
    return (
      <main
        className="
          flex
          min-h-screen
          flex-col
          text-[#F2F5D6]
        "
        style={
          pageBackgroundStyle
        }
      >
        <GameBanner />


        <div
          className="
            flex
            flex-1
            items-center
            justify-center
            p-6
          "
        >
          <p
            className="
              rounded-xl
              bg-[#F2F5D6]
              px-8
              py-5
              text-center
              text-xl
              text-[#502D10]
              shadow
            "
          >
            Carregando partida...
          </p>
        </div>
      </main>
    );
  }


  // =====================================================
  // PARTIDA INVÁLIDA
  // =====================================================

  if (!gameId) {
    return (
      <main
        className="
          flex
          min-h-screen
          flex-col
          text-[#F2F5D6]
        "
        style={
          pageBackgroundStyle
        }
      >
        <GameBanner />


        <div
          className="
            flex
            flex-1
            items-center
            justify-center
            p-6
          "
        >
          <div
            className="
              rounded-2xl
              bg-[#F2F5D6]
              p-8
              text-center
              text-[#502D10]
              shadow
            "
          >
            <p
              className="
                text-2xl
              "
            >
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
                bg-[#63C947]
                px-6
                py-3
                text-[#502D10]
                shadow
              "
            >
              Voltar ao Menu
            </button>
          </div>
        </div>
      </main>
    );
  }


  // =====================================================
  // VITÓRIA
  // =====================================================

  if (
    gameStatus === "won"
  ) {
    return (
      <main
        className="
          flex
          min-h-screen
          flex-col
          text-[#F2F5D6]
        "
        style={
          pageBackgroundStyle
        }
      >
        <GameBanner />


        <div
          className="
            flex
            flex-1
            items-center
            justify-center
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
              shadow
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


            <p
              className="
                mt-4
              "
            >
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
                disabled={
                  loading
                }
                className="
                  rounded-xl
                  bg-[#63C947]
                  px-5
                  py-3
                  shadow
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
                disabled={
                  loading
                }
                className="
                  rounded-xl
                  bg-[#63C947]
                  px-5
                  py-3
                  shadow
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
        </div>
      </main>
    );
  }


  // =====================================================
  // DERROTA
  // =====================================================

  if (
    gameStatus === "lost"
  ) {
    return (
      <main
        className="
          flex
          min-h-screen
          flex-col
          text-[#F2F5D6]
        "
        style={
          pageBackgroundStyle
        }
      >
        <GameBanner />


        <div
          className="
            flex
            flex-1
            items-center
            justify-center
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
              shadow
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


            <p
              className="
                mt-6
              "
            >
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


            <p
              className="
                mt-4
              "
            >
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
                disabled={
                  loading
                }
                className="
                  rounded-xl
                  bg-[#63C947]
                  px-5
                  py-3
                  shadow
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
                disabled={
                  loading
                }
                className="
                  rounded-xl
                  bg-[#63C947]
                  px-5
                  py-3
                  shadow
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
        </div>
      </main>
    );
  }


  // =====================================================
  // PAINEL DO AUTOCOMPLETE
  // =====================================================

  const showSuggestionPanel =
    inputFocused
    && !suppressSuggestions
    && answer.trim().length
      >= MIN_SUGGESTION_LENGTH
    && (
      suggestionLoading
      || suggestionOpen
    );


  // =====================================================
  // PARTIDA EM ANDAMENTO
  // =====================================================

  return (
    <main
      className="
        min-h-screen
        text-[#F2F5D6]
      "
      style={
        pageBackgroundStyle
      }
    >
      <GameBanner />


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
            <div
              ref={
                suggestionContainerRef
              }
              className="
                relative
                w-full
                max-w-md
              "
            >
              <input
                type="text"

                value={
                  answer
                }

                onChange={
                  (event) =>
                    handleAnswerChange(
                      event.target.value,
                    )
                }

                onKeyDown={
                  handleInputKeyDown
                }

                onFocus={() => {
                  setInputFocused(
                    true,
                  );


                  if (
                    !suppressSuggestions
                    && suggestions.length
                      > 0
                  ) {
                    setSuggestionOpen(
                      true,
                    );
                  }
                }}

                onBlur={() => {
                  setInputFocused(
                    false,
                  );
                }}

                disabled={
                  loading
                }

                placeholder=
                  "Insira seu palpite..."

                autoComplete="off"

                role="combobox"

                aria-autocomplete=
                  "list"

                aria-expanded={
                  showSuggestionPanel
                }

                aria-controls=
                  "guess-suggestions"

                className="
                  w-full
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


              {showSuggestionPanel && (
                <div
                  id="guess-suggestions"

                  role="listbox"

                  className="
                    absolute
                    left-0
                    right-0
                    top-full
                    z-30
                    mt-2
                    overflow-hidden
                    rounded-xl
                    border-2
                    border-[#502D10]/20
                    bg-[#F2F5D6]
                    text-[#502D10]
                    shadow-xl
                  "
                >
                  {suggestionLoading ? (
                    <div
                      className="
                        px-5
                        py-4
                        text-center
                        text-sm
                        opacity-70
                      "
                    >
                      Buscando sugestões...
                    </div>
                  ) : suggestions.length
                      === 0 ? (
                    <div
                      className="
                        px-5
                        py-4
                        text-center
                        text-sm
                        opacity-70
                      "
                    >
                      Nenhuma sugestão encontrada.
                    </div>
                  ) : (
                    suggestions.map(
                      (
                        suggestion,
                        index,
                      ) => {
                        const selected =
                          index
                          === selectedSuggestionIndex;


                        return (
                          <button
                            key={
                              `${suggestion.category}-${suggestion.name}`
                            }

                            type="button"

                            role="option"

                            aria-selected={
                              selected
                            }

                            // Evita que o input
                            // perca o foco antes
                            // do clique ser tratado.
                            onMouseDown={
                              (event) =>
                                event.preventDefault()
                            }

                            onMouseEnter={() =>
                              setSelectedSuggestionIndex(
                                index,
                              )
                            }

                            onClick={() =>
                              selectSuggestion(
                                suggestion,
                              )
                            }

                            className={`
                              flex
                              w-full
                              items-center
                              justify-between
                              gap-4
                              border-b
                              border-[#502D10]/10
                              px-5
                              py-3
                              text-left
                              last:border-b-0
                              ${
                                selected
                                  ? "bg-[#63C947]"
                                  : "hover:bg-[#E4E8C4]"
                              }
                            `}
                          >
                            <span>
                              {suggestion.name}
                            </span>


                            {
                              suggestionCategory
                                === "random"
                              && (
                                <span
                                  className="
                                    shrink-0
                                    rounded-md
                                    bg-[#502D10]/10
                                    px-2
                                    py-1
                                    text-xs
                                  "
                                >
                                  {
                                    categoryLabels[
                                      suggestion.category
                                    ]
                                    ?? suggestion.category
                                  }
                                </span>
                              )
                            }
                          </button>
                        );
                      },
                    )
                  )}
                </div>
              )}
            </div>


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

                disabled={
                  loading
                  || hints.length
                    >= MAX_HINTS
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
                {loading
                  ? "Aguarde..."
                  : hints.length
                      >= MAX_HINTS
                    ? "Todas as dicas usadas"
                    : "Nova dica"}
              </button>


              <button
                type="submit"

                disabled={
                  loading
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
                Enviar palpite
              </button>


              <button
                type="button"

                onClick={() =>
                  navigate("/")
                }

                disabled={
                  loading
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
                Voltar ao Menu
              </button>
            </div>
          </form>
        </section>


        <GuessHistory
          guesses={guesses}
        />


        <p
          className="
            text-center
            text-lg
          "
        >
          Dicas:{" "}
          {hints.length}/{MAX_HINTS}
        </p>


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