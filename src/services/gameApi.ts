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


export interface GameCreateResponse {
  game_id: string;
  category: string;
  lives: number;
  max_lives: number;
  status: GameStatus;
}


export interface GuessResponse {
  game_id: string;
  correct: boolean;
  lives: number;
  status: GameStatus;
  answer: string | null;
}


export interface HintResponse {
  game_id: string;
  hint_number: number;
  hint: string;
  lives: number;
  status: GameStatus;
  answer: string | null;
}


export interface GameGuessHistoryItem {
  guess: string;
  correct: boolean;
}


export interface GameHintHistoryItem {
  hint_number: number;
  hint: string;
}


export interface GameStateResponse {
  game_id: string;
  category: string;
  lives: number;
  max_lives: number;
  status: GameStatus;
  answer: string | null;

  guesses:
    GameGuessHistoryItem[];

  hints:
    GameHintHistoryItem[];
}


export interface EntitySuggestion {
  name: string;
  category: Category;
}


interface SuggestionResponse {
  suggestions:
    EntitySuggestion[];
}


const API_URL = (
  import.meta.env.VITE_API_URL
  ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");


async function requestJson<T>(
  url: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    url,
    options,
  );


  if (!response.ok) {
    let message =
      `Erro HTTP ${response.status}`;


    try {
      const data = await response.json();

      if (
        typeof data?.detail
        === "string"
      ) {
        message = data.detail;
      }
    } catch {
      // Mantém a mensagem HTTP
      // caso o corpo não seja JSON.
    }


    throw new Error(
      message,
    );
  }


  return (
    await response.json()
  ) as T;
}


export async function createGame(
  category: Category,
): Promise<GameCreateResponse> {
  return requestJson<
    GameCreateResponse
  >(
    `${API_URL}/games`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({
        category,
      }),
    },
  );
}


export async function getGame(
  gameId: string,
): Promise<GameStateResponse> {
  return requestJson<
    GameStateResponse
  >(
    `${API_URL}/games/${gameId}`,
  );
}


export async function submitGuess(
  gameId: string,
  guess: string,
): Promise<GuessResponse> {
  return requestJson<
    GuessResponse
  >(
    `${API_URL}/games/${gameId}/guess`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({
        guess,
      }),
    },
  );
}


export async function requestHint(
  gameId: string,
): Promise<HintResponse> {
  return requestJson<
    HintResponse
  >(
    `${API_URL}/games/${gameId}/hint`,
    {
      method: "POST",
    },
  );
}


export async function getEntitySuggestions(
  query: string,
  category: Category,
  limit = 6,
  signal?: AbortSignal,
): Promise<EntitySuggestion[]> {
  const parameters =
    new URLSearchParams({
      q: query,
      category,
      limit: String(limit),
    });


  const result =
    await requestJson<
      SuggestionResponse
    >(
      `${API_URL}/entities/suggestions?${parameters.toString()}`,
      {
        signal,
      },
    );


  return result.suggestions;
}