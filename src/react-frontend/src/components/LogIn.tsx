import * as React from "react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import CryptoJS from "crypto-js";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { databaseUrl } from "@/servers";
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert"
import { AlertCircle, FileWarning, Terminal } from "lucide-react"

const Login = (props: any) => {
  const [isErrorVisible, setIsErrorVisible] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState('');
  const isPasswordMatch = password === confirmPassword;
  const navigate = useNavigate();

  const switchToSignUp = () => {
    setIsSignUp(true);
    setIsErrorVisible(false);
    clearFields();
  };

  const switchToLogin = () => {
    setIsSignUp(false);
    setIsErrorVisible(false);
    clearFields();
  };

  const clearFields = () => {
    setUsername("");
    setPassword("");
    setConfirmPassword("");
  };

  const login = () => {
    var salt = "";
    // Retrieve salt associated with entered user
    fetch(databaseUrl + "users/" + username + "/salt")
    .then((res) => {
        if (!res.ok) {
            return res.json().then((errorData) => {
                throw new Error(errorData.message);
            });
        }
        return res.json();
    })
    .then((data) => {
        if (data["status"] === 200) {
            salt = data["content"]["salt"];
            const credentials = {
                username: username,
                password: CryptoJS.SHA256(password + salt).toString(),
            };
            const options = {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json",
                },
                body: JSON.stringify(credentials),
            };
            return fetch(databaseUrl + "login", options);
        } else {
            throw new Error(data["message"]);
        }
    })
    .then((res) => {
        if (!res.ok) {
            return res.json().then((errorData) => {
                throw new Error(errorData.message);
            });
        }
        return res.json();
    })
    .then((data) => {
        if (data["status"] === 200) {
            localStorage.setItem("Auth-Token", data["content"]["Auth-Token"]);
            navigate("/dashboard");
        } else {
            throw new Error(data["message"]);
        }
    })
    .catch((error) => {
        console.error('Fetch error:', error.message);
        setIsErrorVisible(true);
        setErrorMessage(error.message);
    });
  };

  const signUp = () => {
    let salt = CryptoJS.lib.WordArray.random(256 / 8).toString();
    const credentials = {
      username: username,
      password: CryptoJS.SHA256(password + salt).toString(),
      email: "not_implemented",
      salt: salt,
    };
    const options = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(credentials),
    };
    fetch(databaseUrl + "signup", options)
      .then((res) => {
        if (!res.ok) {  // Check if the request was successful
          return res.json().then((errorData) => {
            setIsErrorVisible(true);
            setErrorMessage(errorData.message);
          });
        }
        return res.json();  // Return the JSON data if the request was successful
      })
      .then((data) => {
        if (data["status"] === 200) {
          login();
        } else {
          setIsErrorVisible(true);
          setErrorMessage(data["message"]);
        }
      })
      .catch((error) => {
        setIsErrorVisible(true);
        setErrorMessage(error.message);
      });

  };

  const handleSubmit = (e: React.SyntheticEvent) => {
    e.preventDefault();

    if (isSignUp) {
      signUp();
    } else {
      login();
    }
  };

  return (
    <div
      className="h-screen flex items-center justify-center"
      style={{
        background: "rgba(0, 0, 0, 0)",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div
        className="breathing-graph"
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          animation: "breathe 4s infinite alternate",
        }}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="1500"
          height="100vh"
          viewBox="0 0 1500 750"
        >
          <line x1="300.0" y1="300.0" x2="600.0" y2="300.0" stroke="black" />
          <line x1="600.0" y1="300.0" x2="900.0" y2="300.0" stroke="black" />
          <line x1="900.0" y1="300.0" x2="1200.0" y2="300.0" stroke="black" />
          <line x1="300.0" y1="300.0" x2="450.0" y2="450.0" stroke="black" />
          <line x1="600.0" y1="300.0" x2="750.0" y2="450.0" stroke="black" />
          <line x1="900.0" y1="300.0" x2="900.0" y2="150.0" stroke="black" />
          <line x1="900.0" y1="150.0" x2="600.0" y2="150.0" stroke="black" />
          <line x1="600.0" y1="150.0" x2="450.0" y2="450.0" stroke="black" />
          <line x1="300.0" y1="300.0" x2="300.0" y2="150.0" stroke="black" />
          <line x1="600.0" y1="300.0" x2="1200.0" y2="150.0" stroke="black" />
          <line x1="1200.0" y1="300.0" x2="750.0" y2="450.0" stroke="black" />
          <line x1="900.0" y1="300.0" x2="450.0" y2="450.0" stroke="black" />
          <circle cx="300.0" cy="300.0" r="25" fill="#F00" />
          <circle cx="600.0" cy="300.0" r="25" fill="#0F0" />
          <circle cx="900.0" cy="300.0" r="25" fill="#00F" />
          <circle cx="1200.0" cy="300.0" r="25" fill="#FF0" />
          <circle cx="450.0" cy="450.0" r="25" fill="#0FF" />
          <circle cx="750.0" cy="450.0" r="25" fill="#F0F" />
          <circle cx="600.0" cy="150.0" r="25" fill="#F80" />
          <circle cx="900.0" cy="150.0" r="25" fill="#8F0" />
          <circle cx="300.0" cy="150.0" r="25" fill="#F8F" />
          <circle cx="1200.0" cy="150.0" r="25" fill="#88F" />
        </svg>
      </div>
      {!isSignUp ? (
        <Card className="w-[400px] h-[400px] z-10">
          <CardHeader>
            <CardTitle>LOGIN</CardTitle>
          </CardHeader>
          <form onSubmit={(e) => handleSubmit(e)}>
            <CardContent>
              <div className="grid w-full items-center gap-4">
                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="name">Username</Label>
                  <Input
                    id="name"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                  />
                </div>
                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    placeholder="Password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
            <CardFooter style={{ flexDirection: 'column' }}>
              <div className="flex justify-between">
                <Button type="button" variant="outline" onClick={switchToSignUp}>
                  Sign Up
                </Button>
                <Button type="submit" value="Login" variant="outline">
                  login
                </Button>
              </div>
              <div id="error-UserOrPass" style={{ marginTop: 40, display: isErrorVisible ? 'block' : 'none' }}>
                <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription style={{ marginTop: 6}}>
                  <b>ERROR:</b> {errorMessage}
                </AlertDescription>
                </Alert>
              </div>
            </CardFooter>
          </form>
        </Card>
      ) : (
        <Card className="w-[400px] h-[400px] z-10">
          <CardHeader>
            <CardTitle>SIGN UP</CardTitle>
          </CardHeader>
          <form onSubmit={(e) => handleSubmit(e)}>
            <CardContent>
              <div className="grid w-full items-center gap-4">
                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="name">Username</Label>
                  <Input
                    id="name"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                  />
                </div>
                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="confirmPassword">Confirm Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="Confirm Password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  />
                </div>
              </div>
              {!isPasswordMatch && (
                <p className="text-red-500">Passwords do not match!</p>
              )}
            </CardContent>
            <CardFooter style={{ flexDirection: 'column' }}>
              <div className="flex justify-between">
                <Button type="button" variant="outline" onClick={switchToLogin}>
                  Back
                </Button>
                <Button type="submit" disabled={!isPasswordMatch}>
                  Create
                </Button>
              </div>
              <div id="error-UserOrPass" style={{ marginTop: 4, display: isErrorVisible ? 'block' : 'none' }}>
                <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription style={{ marginTop: 6}}>
                  <b>ERROR:</b> {errorMessage}
                </AlertDescription>
                </Alert>
              </div>
            </CardFooter>
          </form>
        </Card>
      )}
      {/* Inline keyframes CSS */}
      <style>{`
                @keyframes breathe {
                    0% {
                        transform: translate(-50%, -50%) scaleY(1);
                    }
                    100% {
                        transform: translate(-50%, -50%) scaleY(1.1);
                    }
                }
            `}</style>
    </div>
  );
};

export default Login;
