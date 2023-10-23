import React from 'react';
import {
  Alert,
  AlertDescription,
} from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"

interface Props {
  message: string | null;
  clearAlert: () => void;
}

const AlertNotification: React.FC<Props> = ({ message, clearAlert }) => {
  if (!message) return null;
  setTimeout(clearAlert, 5000);

  return (
    <Alert className="dark Alert-notification fixed top-5 w-200 right-0 z-10 mr-12">
      <AlertCircle className="h-6 w-6 mt-1" />
      <AlertDescription className="mt-6">
        <b>Alert:</b> {message}
        <button onClick={clearAlert} className="ml-5 bg-red-500 text-white p-2"><b>Close</b></button>
      </AlertDescription>
    </Alert>
  );
};

export default AlertNotification;
