import fullHeart from "../assets/heart-full.png";
import emptyHeart from "../assets/heart-empty.png";

type HeartProps = {
  filled: boolean;
};

export function Heart({ filled }: HeartProps) {
  return (
    <img
      src={filled ? fullHeart : emptyHeart}
      alt={filled ? "Vida disponível" : "Vida perdida"}
      className="h-8 w-8 object-contain md:h-10 md:w-10"
    />
  );
}