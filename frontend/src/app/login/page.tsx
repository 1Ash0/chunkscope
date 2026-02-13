"use client"

import { useState } from "react"
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

export default function LoginPage() {
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

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsSubmitting(true)
        try {
            await login({ email, password })
            toast({
                title: "Welcome back!",
                description: "You have successfully signed in.",
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
                description: "Your account has been created successfully.",
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
            {/* Background Effects */}
            <div className="absolute inset-0 z-0">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl animate-pulse" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
            </div>

            <div className="z-10 w-full max-w-md space-y-8">
                <div className="text-center space-y-2">
                    <Link href="/" className="inline-flex items-center text-sm text-zinc-400 hover:text-white transition-colors mb-4">
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Back to Home
                    </Link>
                    <h1 className="text-3xl font-bold tracking-tight">ChunkScope</h1>
                    <p className="text-zinc-400">Sign in to access your RAG pipelines.</p>
                </div>

                <Card className="bg-zinc-950/50 border-white/10 backdrop-blur-xl shadow-2xl">
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
                                            className="bg-black/50 border-white/10 focus:border-amber-500/50 focus:ring-amber-500/20"
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
                                            className="bg-black/50 border-white/10 focus:border-amber-500/50 focus:ring-amber-500/20"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            required
                                        />
                                    </div>
                                </CardContent>
                                <CardFooter>
                                    <Button type="submit" className="w-full bg-white text-black hover:bg-zinc-200" disabled={isSubmitting}>
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
                                            className="bg-black/50 border-white/10 focus:border-amber-500/50 focus:ring-amber-500/20"
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
                                            className="bg-black/50 border-white/10 focus:border-amber-500/50 focus:ring-amber-500/20"
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
                                            className="bg-black/50 border-white/10 focus:border-amber-500/50 focus:ring-amber-500/20"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            required
                                        />
                                    </div>
                                </CardContent>
                                <CardFooter>
                                    <Button type="submit" className="w-full bg-amber-500 text-black hover:bg-amber-600" disabled={isSubmitting}>
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
