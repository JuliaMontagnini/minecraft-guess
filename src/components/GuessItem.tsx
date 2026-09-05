import emptyHeart from "../assets/heart-empty.png";

type GuessItemProps = {
  guess: string;
};

export function GuessItem({ guess }: GuessItemProps) {
  return (
    <li className="flex items-center gap-3">
      <img
        src={emptyHeart}
        alt=""
        className="h-5 w-5 object-contain"
      />

      <span>{guess}</span>
    </li>
  );
}