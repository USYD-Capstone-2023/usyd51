import React from 'react';
import {
  Alert,
  AlertDescription,
} from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"

interface Props {
  message: string | null;
  clearError: () => void;
}

const ErrorNotification: React.FC<Props> = ({ message, clearError }) => {
  if (!message) return null;
  setTimeout(clearError, 5000);

  return (
    <Alert variant="destructive" className="error-notification fixed top-5 w-200 right-0 z-10 mr-12 bg-white">
      <AlertCircle className="h-6 w-6 mt-1" />
      <AlertDescription style={{ marginTop: 6}}>
        <b>ERROR:</b> {message}
        <button onClick={clearError} className="ml-5 bg-red-500 text-white p-2"><b>Close</b></button>
      </AlertDescription>
    </Alert>
  );
};

export default ErrorNotification;
