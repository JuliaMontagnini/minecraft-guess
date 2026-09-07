import {
  Heart,
  type HeartState,
} from "./Heart";


type LivesProps = {
  lives: number;
  maxLives?: number;
};


export function Lives({
  lives,
  maxLives = 10,
}: LivesProps) {
  const totalHearts =
    Math.ceil(maxLives / 2);

  function getHeartState(
    index: number,
  ): HeartState {
    const pointsForHeart =
      lives - index * 2;

    if (pointsForHeart >= 2) {
      return "full";
    }

    if (pointsForHeart === 1) {
      return "half";
    }

    return "empty";
  }


  return (
    <div
      className="
        flex
        items-center
        justify-center
        gap-2
      "
      aria-label={
        `${lives} de ${maxLives} pontos de vida restantes`
      }
    >
      {Array.from({
        length: totalHearts,
      }).map((_, index) => (
        <Heart
          key={index}
          state={
            getHeartState(index)
          }
        />
      ))}
    </div>
  );
}