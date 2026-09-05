import { HintItem } from "./HintItem";

type HintListProps = {
  hints: string[];
};

export function HintList({
  hints,
}: HintListProps) {
  if (hints.length === 0) {
    return null;
  }

  return (
    <section
      className="
        flex
        w-full
        max-w-md
        flex-col
        gap-6
        rounded-2xl
        bg-[#63C947]
        p-6
        text-[#502D10]
      "
    >
      {hints.map((hint, index) => (
        <HintItem
          key={index}
          number={index + 1}
          text={hint}
        />
      ))}
    </section>
  );
}