import { FaSpinner } from 'react-icons/fa';

export default function LoadingSpinner({ size = 'default', text = 'Loading...' }) {
  const sizeClasses = {
    small: 'text-xl',
    default: 'text-3xl',
    large: 'text-5xl',
  };

  return (
    <div className="flex flex-col items-center justify-center py-12">
      <FaSpinner className={`animate-spin text-primary-500 ${sizeClasses[size]} mb-4`} />
      <p className="text-gray-400">{text}</p>
    </div>
  );
}