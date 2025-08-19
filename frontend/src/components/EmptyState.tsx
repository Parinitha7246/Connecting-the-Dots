export const EmptyState = ({ message, icon }: { message: string, icon: React.ReactNode }) => (
  <div className="h-full flex flex-col items-center justify-center text-center text-gray-500 p-4">
    <div className="text-4xl mb-3 opacity-50">{icon}</div>
    <p className="max-w-xs">{message}</p>
  </div>
);