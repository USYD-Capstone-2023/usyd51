import * as React from "react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const Login = (props: any) => {
    return (
        <div 
            className="h-screen flex items-center justify-center"
            style={{ 
                background: 'rgba(0, 0, 0, 0)',
                position: 'relative',
                overflow: 'hidden'
            }}
        >
            <div 
                className="breathing-graph"
                style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    animation: 'breathe 4s infinite alternate',
                }}
            >
                {/* Adjusted SVG for better visibility */}
                <svg xmlns="http://www.w3.org/2000/svg" width="1500" height="100vh" viewBox="0 0 1500 750">
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
            <Card className="w-[400px] h-[400px] z-10">
                <CardHeader>
                    <CardTitle>LOGIN</CardTitle>
                </CardHeader>
                <CardContent>
                    <form>
                        <div className="grid w-full items-center gap-4">
                            <div className="flex flex-col space-y-1.5">
                                <Label htmlFor="name">Username</Label>
                                <Input id="name" placeholder="Username" />
                            </div>
                            <div className="flex flex-col space-y-1.5">
                                <Label htmlFor="name">Password</Label>
                                <Input id="password" placeholder="Password" />
                            </div>
                            <div className="flex flex-col space-y-1.5"></div>
                        </div>
                    </form>
                </CardContent>
                <CardFooter className="flex justify-between">
                    <Button variant="outline"><Link to={"./dashboard"}> Sign Up </Link></Button>
                    <Button><Link to={"./dashboard"}> Login </Link></Button>
                </CardFooter>
            </Card>

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
    )
};

export default Login;
