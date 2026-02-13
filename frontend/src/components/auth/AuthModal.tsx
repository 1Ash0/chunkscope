"use client"

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { authApi } from '@/lib/api'
import { useToast } from '@/components/ui/use-toast'
import { Loader2, X } from 'lucide-react'

interface AuthModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: (user: any) => void;
}

export function AuthModal({ isOpen, onClose, onSuccess }: AuthModalProps) {
    const [loading, setLoading] = useState(false)
    const { toast } = useToast()

    // Form states
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [name, setName] = useState('')

    if (!isOpen) return null

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        try {
            const response = await authApi.login({ email, password })
            localStorage.setItem('token', response.tokens.access_token)
            toast({
                title: "Success",
                description: `Welcome back, ${response.user.name}!`,
            })
            onSuccess(response.user)
            onClose()
        } catch (error: any) {
            toast({
                title: "Login Failed",
                description: error.response?.data?.error || "Invalid credentials",
                variant: "destructive"
            })
        } finally {
            setLoading(false)
        }
    }

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        try {
            const response = await authApi.register({ email, password, name })
            localStorage.setItem('token', response.tokens.access_token)
            toast({
                title: "Account Created",
                description: `Welcome, ${name}! Your account has been created.`,
            })
            onSuccess(response.user)
            onClose()
        } catch (error: any) {
            toast({
                title: "Registration Failed",
                description: error.response?.data?.error || "Failed to create account",
                variant: "destructive"
            })
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="relative w-full max-w-md animate-in zoom-in-95 duration-200">
                <Button
                    variant="ghost"
                    size="icon"
                    className="absolute right-2 top-2 text-zinc-400 hover:text-white z-10"
                    onClick={onClose}
                >
                    <X className="h-4 w-4" />
                </Button>

                <Tabs defaultValue="login" className="w-full">
                    <TabsList className="grid w-full grid-cols-2 bg-zinc-900 mb-0">
                        <TabsTrigger value="login">Login</TabsTrigger>
                        <TabsTrigger value="register">Register</TabsTrigger>
                    </TabsList>

                    <Card className="bg-zinc-950 border-white/10 shadow-2xl">

                        <TabsContent value="login" className="mt-0">
                            <form onSubmit={handleLogin}>
                                <CardHeader className="pt-0">
                                    <CardTitle className="text-white">Sign In</CardTitle>
                                    <CardDescription className="text-zinc-500">
                                        Enter your credentials to access your pipelines.
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="email">Email</Label>
                                        <Input
                                            id="email"
                                            type="email"
                                            placeholder="name@example.com"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            required
                                            className="bg-zinc-900 border-white/5 text-white"
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
                                            className="bg-zinc-900 border-white/5 text-white"
                                        />
                                    </div>
                                </CardContent>
                                <CardFooter>
                                    <Button type="submit" className="w-full bg-white text-black hover:bg-zinc-200" disabled={loading}>
                                        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                        Sign In
                                    </Button>
                                </CardFooter>
                            </form>
                        </TabsContent>

                        <TabsContent value="register" className="mt-0">
                            <form onSubmit={handleRegister}>
                                <CardHeader className="pt-0">
                                    <CardTitle className="text-white">Create Account</CardTitle>
                                    <CardDescription className="text-zinc-500">
                                        Join ChunkScope to start building RAG pipelines.
                                    </CardDescription>
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
                                            className="bg-zinc-900 border-white/5 text-white"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="reg-email">Email</Label>
                                        <Input
                                            id="reg-email"
                                            type="email"
                                            placeholder="name@example.com"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            required
                                            className="bg-zinc-900 border-white/5 text-white"
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
                                            className="bg-zinc-900 border-white/5 text-white"
                                        />
                                    </div>
                                </CardContent>
                                <CardFooter>
                                    <Button type="submit" className="w-full bg-amber-500 text-black hover:bg-amber-600 font-semibold" disabled={loading}>
                                        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                        Get Started
                                    </Button>
                                </CardFooter>
                            </form>
                        </TabsContent>
                    </Card>
                </Tabs>
            </div>
        </div>
    )
}
