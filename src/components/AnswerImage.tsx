import {
  useEffect,
  useState,
} from "react";


interface AnswerImageProps {
  src: string | null;
  answer: string | null;
}


export function AnswerImage({
  src,
  answer,
}: AnswerImageProps) {
  const [
    failed,
    setFailed,
  ] = useState(false);


  useEffect(() => {
    setFailed(false);
  }, [src]);


  if (!src || failed) {
    return (
      <div
        className="
          mx-auto
          mt-6
          flex
          h-48
          w-48
          items-center
          justify-center
          rounded-xl
          border-2
          border-dashed
          border-[#8E5A2F]
          bg-[#E8E9C8]
          p-4
          text-center
          text-sm
          text-[#502D10]
        "
      >
        Imagem indisponível
      </div>
    );
  }


  return (
    <img
      src={src}
      alt={
        answer
          ? `Imagem de ${answer}`
          : "Imagem da resposta"
      }
      onError={() =>
        setFailed(true)
      }
      style={{
        imageRendering: "pixelated",
      }}
      className="
        mx-auto
        mt-6
        max-h-64
        max-w-full
        rounded-xl
        object-contain
      "
    />
  );
}
