

type StatCardProps = {
  label: string;
  value: number;
  color:"blue" | "purple" | "green" | "red" | "yellow" | "amber" | "pink" | "indigo" | "cyan" | "gray" | "muted";
  isSelected?: boolean;
  onClick?: () => void;
};

const colorClasses = {
  blue: {
    bg: "bg-blue-50 dark:bg-blue-900/20",
    hoverBg: "hover:bg-blue-100 dark:hover:bg-blue-900/30",
    selectedBg: "bg-blue-100 dark:bg-blue-900/40",
    ring: "ring-blue-600",
    text: "text-blue-600",
  },
  purple: {
    bg: "bg-purple-50 dark:bg-purple-900/20",
    hoverBg: "hover:bg-purple-100 dark:hover:bg-purple-900/30",
    selectedBg: "bg-purple-100 dark:bg-purple-900/40",
    ring: "ring-purple-600",
    text: "text-purple-600",
  },
  green: {
    bg: "bg-green-50 dark:bg-green-900/20",
    hoverBg: "hover:bg-green-100 dark:hover:bg-green-900/30",
    selectedBg: "bg-green-100 dark:bg-green-900/40",
    ring: "ring-green-600",
    text: "text-green-600",
  },
  red: {
    bg: "bg-red-50 dark:bg-red-900/20",
    hoverBg: "hover:bg-red-100 dark:hover:bg-red-900/30",
    selectedBg: "bg-red-100 dark:bg-red-900/40",
    ring: "ring-red-600",
    text: "text-red-600",
  },
  yellow: {
    bg: "bg-yellow-50 dark:bg-yellow-900/20",
    hoverBg: "hover:bg-yellow-100 dark:hover:bg-yellow-900/30",
    selectedBg: "bg-yellow-100 dark:bg-yellow-900/40",
    ring: "ring-yellow-600",
    text: "text-yellow-600",
  },
  amber: {
    bg: "bg-amber-50 dark:bg-amber-900/20",
    hoverBg: "hover:bg-amber-100 dark:hover:bg-amber-900/30",
    selectedBg: "bg-amber-100 dark:bg-amber-900/40",
    ring: "ring-amber-600",
    text: "text-amber-600",
  },
  pink: {
    bg: "bg-pink-50 dark:bg-pink-900/20",
    hoverBg: "hover:bg-pink-100 dark:hover:bg-pink-900/30",
    selectedBg: "bg-pink-100 dark:bg-pink-900/40",
    ring: "ring-pink-600",
    text: "text-pink-600",
  },
  indigo: {
    bg: "bg-indigo-50 dark:bg-indigo-900/20",
    hoverBg: "hover:bg-indigo-100 dark:hover:bg-indigo-900/30",
    selectedBg: "bg-indigo-100 dark:bg-indigo-900/40",
    ring: "ring-indigo-600",
    text: "text-indigo-600",
  },
  cyan: {
    bg: "bg-cyan-50 dark:bg-cyan-900/20",
    hoverBg: "hover:bg-cyan-100 dark:hover:bg-cyan-900/30",
    selectedBg: "bg-cyan-100 dark:bg-cyan-900/40",
    ring: "ring-cyan-600",
    text: "text-cyan-600",
  },
  gray: {
    bg: "bg-gray-50 dark:bg-gray-900/20",
    hoverBg: "hover:bg-gray-100 dark:hover:bg-gray-900/30",
    selectedBg: "bg-gray-100 dark:bg-gray-900/40",
    ring: "ring-gray-600",
    text: "text-gray-600",
  },
  muted: {
    bg: "bg-muted",
    hoverBg: "hover:bg-muted/80",
    selectedBg: "bg-muted",
    ring: "ring-gray-600",
    text: "text-foreground",
  },
};

const StatCard = ({ label, value, color, isSelected, onClick }: StatCardProps) => {
  const colors = colorClasses[color];
  const isClickable = !!onClick;

  const baseClasses = "text-center p-3 rounded-lg transition-all";
  const interactiveClasses = isClickable
    ? `cursor-pointer ${colors.hoverBg}`
    : "";
  const stateClasses = isSelected
    ? `${colors.selectedBg} ring-2 ${colors.ring}`
    : colors.bg;

  const Component = isClickable ? "button" : "div";

  return (
    <Component
      onClick={onClick}
      className={`${baseClasses} ${interactiveClasses} ${stateClasses}`}
      {...(isClickable && { type: "button" })}
    >
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className={`text-2xl font-bold ${colors.text}`}>{value}</p>
    </Component>
  );
};

export default StatCard;