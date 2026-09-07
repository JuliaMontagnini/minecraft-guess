const API_URL =
  import.meta.env.VITE_API_URL
  ?? "http://127.0.0.1:8000";

export type Category =
  | "mobs"
  | "biomes"
  | "items"
  | "structures"
  | "enchantments"
  | "random";

export type GameStatus =
  | "playing"
  | "won"
  | "lost";

export type GameCreateResponse = {
  game_id: string;
  category: string;
  lives: number;
  max_lives: number;
  status: GameStatus;
};

export type GuessResponse = {
  game_id: string;
  correct: boolean;
  lives: number;
  status: GameStatus;
  answer: string | null;
};

export type HintResponse = {
  game_id: string;
  hint_number: number;
  hint: string;
  lives: number;
  status: GameStatus;
  answer: string | null;
};


async function handleResponse<T>(
  response: Response,
): Promise<T> {
  if (!response.ok) {
    let message =
      "Ocorreu um erro ao comunicar com o servidor.";

    try {
      const data = await response.json();

      if (data.detail) {
        message = data.detail;
      }
    } catch {
      // Mantém a mensagem padrão.
    }

    throw new Error(message);
  }

  return response.json();
}


export async function createGame(
  category: Category,
): Promise<GameCreateResponse> {
  const response = await fetch(
    `${API_URL}/games`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        category,
      }),
    },
  );

  return handleResponse<GameCreateResponse>(
    response,
  );
}


export async function submitGuess(
  gameId: string,
  guess: string,
): Promise<GuessResponse> {
  const response = await fetch(
    `${API_URL}/games/${gameId}/guess`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        guess,
      }),
    },
  );

  return handleResponse<GuessResponse>(
    response,
  );
}


export async function requestHint(
  gameId: string,
): Promise<HintResponse> {
  const response = await fetch(
    `${API_URL}/games/${gameId}/hint`,
    {
      method: "POST",
    },
  );

  return handleResponse<HintResponse>(
    response,
  );
}

export type GameGuessHistoryItem = {
  guess: string;
  correct: boolean;
};

export type GameHintHistoryItem = {
  hint_number: number;
  hint: string;
};

export type GameStateResponse = {
  game_id: string;
  category: string;
  lives: number;
  max_lives: number;
  status: GameStatus;
  answer: string | null;
  guesses: GameGuessHistoryItem[];
  hints: GameHintHistoryItem[];
};

export async function getGame(
  gameId: string,
): Promise<GameStateResponse> {
  const response = await fetch(
    `${API_URL}/games/${gameId}`,
  );

  return handleResponse<GameStateResponse>(
    response,
  );
}