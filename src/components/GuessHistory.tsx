import { GuessItem } from "./GuessItem";

type GuessHistoryProps = {
  guesses: string[];
};

export function GuessHistory({
  guesses,
}: GuessHistoryProps) {
  return (
    <section
      className="
        w-full
        max-w-md
        rounded-2xl
        bg-[#F2F5D6]
        p-6
        text-[#502D10]
      "
    >
      <h2 className="mb-5 text-center text-xl md:text-2xl">
        Palpites anteriores
      </h2>

      {guesses.length === 0 ? (
        <p className="text-center opacity-70">
          Nenhum palpite ainda.
        </p>
      ) : (
        <ul className="flex flex-col gap-4">
          {guesses.map((guess, index) => (
            <GuessItem
              key={`${guess}-${index}`}
              guess={guess}
            />
          ))}
        </ul>
      )}
    </section>
  );
}