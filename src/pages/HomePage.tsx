import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { CategoryCard } from "../components/CategoryCard";

import {
  createGame,
  type Category,
} from "../services/gameApi";

import mobIcon from "../assets/mob.png";
import biomeIcon from "../assets/biome.png";
import itemIcon from "../assets/item.png";
import structureIcon from "../assets/structure.png";
import enchantmentIcon from "../assets/enchantment.png";
import randomIcon from "../assets/random.png";

import brownBackground from "../assets/fundo-quadriculado-marrom.png";
import greenBackground from "../assets/fundo-quadriculado-verde.png";


type CategoryCardData = {
  id: Category;
  name: string;
  icon: string;
};


const categories: CategoryCardData[] = [
  {
    id: "mobs",
    name: "Mobs",
    icon: mobIcon,
  },
  {
    id: "biomes",
    name: "Biomas",
    icon: biomeIcon,
  },
  {
    id: "items",
    name: "Itens",
    icon: itemIcon,
  },
  {
    id: "structures",
    name: "Estruturas",
    icon: structureIcon,
  },
  {
    id: "enchantments",
    name: "Encantamentos",
    icon: enchantmentIcon,
  },
  {
    id: "random",
    name: "Aleatório",
    icon: randomIcon,
  },
];


export function HomePage() {
  const navigate = useNavigate();

  const [startingGame, setStartingGame] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function selectCategory(
    category: Category,
  ) {
    if (startingGame) {
      return;
    }

    try {
      setStartingGame(true);
      setError(null);

      const game = await createGame(
        category,
      );

      navigate(
        `/game/${category}/${game.game_id}`,
      );
    } catch (error) {
      console.error(
        "Erro ao criar partida:",
        error,
      );

      setError(
        error instanceof Error
          ? error.message
          : "Não foi possível iniciar a partida.",
      );

      setStartingGame(false);
    }
  }


  return (
    <main
      className="
        min-h-screen
        text-[#F2F5D6]
      "
      style={{
        backgroundColor: "#8E5A2F",

        backgroundImage:
          `url(${brownBackground})`,

        backgroundRepeat: "repeat",
      }}
    >
      {/* HEADER */}
      <header
        className="
          flex
          min-h-32
          items-center
          justify-center
          px-6
          text-center
          md:min-h-44
        "
        style={{
          backgroundColor:
            "rgba(78, 165, 51, 0.62)",

          backgroundImage:
            `url(${greenBackground})`,

          backgroundSize: "cover",
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


      {/* CONTEÚDO PRINCIPAL */}
      <div
        className="
          mx-auto
          flex
          w-full
          max-w-6xl
          flex-col
          items-center
          px-6
          py-12
        "
      >
        {/* TÍTULO */}
        <section
          className="
            mb-10
            text-center
          "
        >
          <h2
            className="
              text-3xl
              md:text-4xl
            "
          >
            Escolha uma categoria
          </h2>

          <p
            className="
              mt-4
              text-lg
              md:text-xl
            "
          >
            Tente descobrir o segredo antes
            de perder todas as vidas!
          </p>
        </section>


        {/* ERRO DA API */}
        {error && (
          <div
            className="
              mb-8
              w-full
              max-w-2xl
              rounded-xl
              bg-[#F2F5D6]
              px-6
              py-4
              text-center
              text-[#9D1C1C]
            "
            role="alert"
          >
            <p>
              {error}
            </p>

            <p
              className="
                mt-2
                text-sm
                text-[#502D10]
              "
            >
              Verifique se o servidor da API
              está ligado e tente novamente.
            </p>
          </div>
        )}


        {/* CARREGAMENTO */}
        {startingGame && (
          <p
            className="
              mb-6
              rounded-xl
              bg-[#F2F5D6]
              px-5
              py-3
              text-center
              text-[#502D10]
            "
          >
            Criando partida...
          </p>
        )}


        {/* CATEGORIAS */}
        <section
          className="
            grid
            w-full
            grid-cols-1
            gap-6
            sm:grid-cols-2
            lg:grid-cols-3
          "
        >
          {categories.map(
            (category) => (
              <CategoryCard
                key={category.id}
                name={category.name}
                icon={category.icon}
                onClick={() =>
                  selectCategory(
                    category.id,
                  )
                }
              />
            ),
          )}
        </section>


        {/* COMO JOGAR */}
        <section
          className="
            mt-16
            w-full
            max-w-3xl
            rounded-2xl
            bg-[#F2F5D6]
            p-8
            text-[#502D10]
          "
        >
          <h2
            className="
              mb-6
              text-center
              text-3xl
            "
          >
            Como jogar?
          </h2>

          <div
            className="
              flex
              flex-col
              gap-5
              text-lg
            "
          >
            <p>
              Escolha uma categoria e tente
              adivinhar qual é o elemento
              secreto do Minecraft.
            </p>

            <p>
              Você começa cada partida com
              5 vidas.
            </p>

            <p>
              Cada palpite errado faz você
              perder uma vida.
            </p>

            <p>
              Pedir uma nova dica também
              custa uma vida.
            </p>

            <p>
              Acerte a resposta antes que
              suas vidas acabem!
            </p>
          </div>
        </section>
      </div>


      {/* FOOTER */}
      <footer
        className="
          px-6
          py-8
          text-center
        "
      >
        <a
          href="https://api.astroworldmc.com"
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