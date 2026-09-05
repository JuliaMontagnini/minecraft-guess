import { Heart } from "./Heart";

type LivesProps = {
  lives: number;
  maxLives?: number;
};

export function Lives({
  lives,
  maxLives = 5,
}: LivesProps) {
  return (
    <div
      className="flex items-center justify-center gap-2"
      aria-label={`${lives} de ${maxLives} vidas restantes`}
    >
      {Array.from({ length: maxLives }).map((_, index) => (
        <Heart
          key={index}
          filled={index < lives}
        />
      ))}
    </div>
  );
}