import React from 'react';

interface Props {
  message: string | null;
  clearError: () => void;
}

const ErrorNotification: React.FC<Props> = ({ message, clearError }) => {
  if (!message) return null;
  setTimeout(clearError, 5000);

  return (
    <div className="error-notification">
      {message}
      <button onClick={clearError}>Close</button>
    </div>
  );
};

export default ErrorNotification;
