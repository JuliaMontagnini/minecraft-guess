type HintItemProps = {
  number: number;
  text: string;
};

export function HintItem({
  number,
  text,
}: HintItemProps) {
  return (
    <div className="text-center">
      <h3 className="font-semibold">
        Dica #{number}
      </h3>

      <p className="mt-1">
        {text}
      </p>
    </div>
  );
}