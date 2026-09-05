type CategoryCardProps = {
  name: string;
  icon: string;
  onClick: () => void;
};

export function CategoryCard({
  name,
  icon,
  onClick,
}: CategoryCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="
        flex
        w-full
        items-center
        justify-center
        gap-4
        rounded-xl
        bg-[#F2F5D6]
        px-6
        py-5
        text-[#502D10]
        shadow-md
        transition-transform
        duration-150

        hover:scale-[1.02]
        active:scale-[0.98]

        focus-visible:outline
        focus-visible:outline-4
        focus-visible:outline-offset-4
        focus-visible:outline-[#F2F5D6]
      "
    >
      <img
        src={icon}
        alt=""
        className="
          h-12
          w-12
          object-contain
          md:h-16
          md:w-16
        "
      />

      <span className="text-2xl md:text-3xl">
        {name}
      </span>
    </button>
  );
}