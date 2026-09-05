import { CategoryCard } from "../components/CategoryCard";

import mobIcon from "../assets/mob.png";
import biomeIcon from "../assets/biome.png";
import itemIcon from "../assets/item.png";
import structureIcon from "../assets/structure.png";
import enchantmentIcon from "../assets/enchantment.png";
import randomIcon from "../assets/random.png";

import brownBackground from "../assets/fundo-quadriculado-marrom.png";
import greenBackground from "../assets/fundo-quadriculado-verde.png";
import { useNavigate } from "react-router-dom";

type Category = {
  id: string;
  name: string;
  icon: string;
};

const categories: Category[] = [
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
    function selectCategory(category: Category) {
        navigate(`/game/${category.id}`);
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
        <h1 className="text-center text-4xl md:text-6xl">
          MinecraftGuess
        </h1>
      </header>

      <div
        className="
          mx-auto
          flex
          w-full
          max-w-6xl
          flex-col
          gap-16
          px-6
          py-12
          md:px-10
          md:py-20
        "
      >
        <section>
          <h2
            className="
              mb-10
              text-center
              text-2xl
              md:text-4xl
            "
          >
            Selecione uma categoria e descubra a entidade secreta
          </h2>

          <div
            className="
              grid
              grid-cols-1
              gap-5

              sm:grid-cols-2

              lg:grid-cols-3
              lg:gap-8
            "
          >
            {categories.map((category) => (
              <CategoryCard
                key={category.id}
                name={category.name}
                icon={category.icon}
                onClick={() => selectCategory(category)}
              />
            ))}
          </div>
        </section>

        <section className="mx-auto w-full max-w-2xl">
          <h2 className="mb-5 text-center text-2xl">
            Como jogar?
          </h2>

          <div
            className="
              rounded-2xl
              bg-[#F2F5D6]
              p-8
              text-center
              text-[#502D10]
              md:text-xl
            "
          >
            <p>Descubra a entidade secreta!</p>

            <div className="my-5">
              <p>Você começa com 5 vidas.</p>
              <p>Pedir uma dica custa 1 coração.</p>
              <p>Um palpite errado custa 1 coração.</p>
            </div>

            <p>Acerte antes de perder todos!</p>
          </div>
        </section>
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