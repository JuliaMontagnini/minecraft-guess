import fullHeart from "../assets/heart-full.png";
import halfHeart from "../assets/heart-half.png";
import emptyHeart from "../assets/heart-empty.png";


export type HeartState =
  | "full"
  | "half"
  | "empty";


type HeartProps = {
  state: HeartState;
};


export function Heart({
  state,
}: HeartProps) {
  const heartImage = {
    full: fullHeart,
    half: halfHeart,
    empty: emptyHeart,
  }[state];

  const heartLabel = {
    full: "Coração cheio",
    half: "Meio coração",
    empty: "Coração vazio",
  }[state];


  return (
    <img
      src={heartImage}
      alt={heartLabel}
      className="
        h-8
        w-8
        object-contain
        md:h-10
        md:w-10
      "
    />
  );
}