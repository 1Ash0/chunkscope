"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import Link from "next/link"
import { useAuthStore } from "@/stores/useAuthStore"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useToast } from "@/components/ui/use-toast"
import { Loader2, ArrowLeft } from "lucide-react"

import { Suspense } from "react"

import { ShaderAnimation } from "@/components/ui/spiral-shader"

function LoginContent() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const { toast } = useToast()
    const { login, register, isLoading } = useAuthStore()

    // Check if we specifically want to start on register tab
    const defaultTab = searchParams.get("tab") === "register" ? "register" : "login"

    // Form states
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [name, setName] = useState("")
    const [isSubmitting, setIsSubmitting] = useState(false)
    const { isAuthenticated: storeIsAuth } = useAuthStore()

    // Auto-redirect if already logged in
    useState(() => {
        if (typeof window !== 'undefined') {
            const token = localStorage.getItem('token');
            if (token && storeIsAuth) {
                router.push("/dashboard");
            }
        }
    });

    useEffect(() => {
        if (storeIsAuth) {
            const from = searchParams.get("from") || "/dashboard"
            router.push(from)
        }
    }, [storeIsAuth, router, searchParams])

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsSubmitting(true)
        try {
            await login({ email, password })
            toast({
                title: "Welcome back!",
                description: "Access granted to the Workspace.",
            })
            router.push("/dashboard")
        } catch (error: any) {
            toast({
                title: "Login Failed",
                description: error.response?.data?.error || "Invalid credentials",
                variant: "destructive",
            })
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsSubmitting(true)
        try {
            await register({ email, password, name })
            toast({
                title: "Account Created",
                description: "Your session has been initialized.",
            })
            router.push("/dashboard")
        } catch (error: any) {
            toast({
                title: "Registration Failed",
                description: error.response?.data?.error || "Could not create account",
                variant: "destructive",
            })
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-4 relative overflow-hidden">
            {/* Spiral Shader Background */}
            <div className="absolute inset-0 z-0">
                <ShaderAnimation />
                <div className="absolute inset-0 bg-black/40 backdrop-blur-[2px]" />
            </div>

            <div className="z-10 w-full max-w-md space-y-8 animate-fade-in-up">
                <div className="text-center space-y-4">
                    <Link href="/" className="inline-flex items-center text-xs font-bold uppercase tracking-widest text-zinc-500 hover:text-white transition-colors mb-4 bg-white/5 px-4 py-2 rounded-full border border-white/5">
                        <ArrowLeft className="mr-2 h-3 w-3" />
                        Return to Origin
                    </Link>
                    <h1 className="text-5xl font-black tracking-tighter bg-gradient-to-b from-white to-zinc-500 bg-clip-text text-transparent">ChunkScope</h1>
                    <p className="text-zinc-500 font-medium">Authentication Protocol Required</p>
                </div>

                <Card className="bg-glass border-white/5 shadow-2xl rounded-[2.5rem] overflow-hidden">
                    <Tabs defaultValue={defaultTab} className="w-full">
                        <TabsList className="grid w-full grid-cols-2 bg-zinc-900/50 p-1 mb-2">
                            <TabsTrigger value="login" className="data-[state=active]:bg-zinc-800">Login</TabsTrigger>
                            <TabsTrigger value="register" className="data-[state=active]:bg-zinc-800">Register</TabsTrigger>
                        </TabsList>

                        <TabsContent value="login">
                            <form onSubmit={handleLogin}>
                                <CardHeader>
                                    <CardTitle>Welcome back</CardTitle>
                                    <CardDescription>Enter your credentials to continue.</CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="email">Email</Label>
                                        <Input
                                            id="email"
                                            type="email"
                                            placeholder="m@example.com"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            required
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="password">Password</Label>
                                        <Input
                                            id="password"
                                            type="password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            required
                                        />
                                    </div>
                                </CardContent>
                                <CardFooter>
                                    <Button type="submit" className="w-full bg-gold text-black hover:bg-gold/90 font-bold" disabled={isSubmitting}>
                                        {isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                                        Sign In
                                    </Button>
                                </CardFooter>
                            </form>
                        </TabsContent>

                        <TabsContent value="register">
                            <form onSubmit={handleRegister}>
                                <CardHeader>
                                    <CardTitle>Create an account</CardTitle>
                                    <CardDescription>Start visualizing your embeddings today.</CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="reg-name">Full Name</Label>
                                        <Input
                                            id="reg-name"
                                            placeholder="John Doe"
                                            value={name}
                                            onChange={(e) => setName(e.target.value)}
                                            required
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="reg-email">Email</Label>
                                        <Input
                                            id="reg-email"
                                            type="email"
                                            placeholder="m@example.com"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            required
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="reg-password">Password</Label>
                                        <Input
                                            id="reg-password"
                                            type="password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            required
                                        />
                                    </div>
                                </CardContent>
                                <CardFooter>
                                    <Button type="submit" className="w-full bg-gold text-black hover:bg-gold/90 font-bold" disabled={isSubmitting}>
                                        {isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                                        Create Account
                                    </Button>
                                </CardFooter>
                            </form>
                        </TabsContent>
                    </Tabs>
                </Card>
            </div>
        </div>
    )
}

export default function LoginPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-black flex items-center justify-center"><Loader2 className="animate-spin text-white" /></div>}>
            <LoginContent />
        </Suspense>
    )
}
