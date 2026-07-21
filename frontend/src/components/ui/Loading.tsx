interface LoadingProps {
  message?: string;
}

export default function Loading({ message = "Cargando..." }: LoadingProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-primary/10 px-4">
      <div className="flex flex-col items-center space-y-4">
        
        {/* Spinner */}
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-focus/20 border-t-interactive"></div>
        
        {/* Text */}
        <p className="text-sm font-medium text-accent">
          {message}
        </p>
      </div>
    </div>
  );
}