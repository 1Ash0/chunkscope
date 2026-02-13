"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useAuthStore } from "@/stores/useAuthStore"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight, Database, GitBranch, Search, LogOut, Loader2 } from "lucide-react"

import { AuthGuard } from "@/components/auth/AuthGuard"

export default function DashboardPage() {
    const { user, logout } = useAuthStore()
    const router = useRouter()

    const handleLogout = () => {
        logout()
        router.push("/")
    }

    return (
        <AuthGuard>
            <div className="min-h-screen bg-black text-white">
                <header className="border-b border-white/10 bg-zinc-950/50 backdrop-blur-md sticky top-0 z-50">
                    <div className="container mx-auto px-6 h-16 flex items-center justify-between">
                        <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
                            <span className="text-amber-500">ChunkScope</span> Dashboard
                        </div>
                        <div className="flex items-center gap-4">
                            <span className="text-sm text-zinc-400">Welcome, {user?.name}</span>
                            <Button variant="ghost" size="sm" onClick={handleLogout} className="text-zinc-400 hover:text-white">
                                <LogOut className="h-4 w-4 mr-2" />
                                Sign Out
                            </Button>
                        </div>
                    </div>
                </header>

                <main className="container mx-auto px-6 py-12">
                    <h1 className="text-3xl font-bold mb-8">Your Workspace</h1>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <DashboardCard
                            title="Pipeline Builder"
                            description="Construct and configure your RAG pipeline with our visual node editor."
                            icon={<GitBranch className="h-8 w-8 text-amber-500" />}
                            href="/pipeline"
                            action="Open Builder"
                        />
                        <DashboardCard
                            title="Visualizer"
                            description="Explore your vector space in 3D and debug semantic relationships."
                            icon={<Search className="h-8 w-8 text-blue-500" />}
                            href="/visualizer"
                            action="Launch Visualizer"
                        />
                        <DashboardCard
                            title="Document Analysis"
                            description="Analyze your documents to find the optimal chunking strategy."
                            icon={<Database className="h-8 w-8 text-green-500" />}
                            href="/analyze"
                            action="Start Analysis"
                        />
                    </div>

                    <div className="mt-12 p-8 rounded-2xl border border-white/10 bg-zinc-900/30">
                        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
                        <p className="text-zinc-500 text-sm">No recent activity found. Start by creating a pipeline.</p>
                    </div>
                </main>
            </div>
        </AuthGuard>
    )
}

function DashboardCard({ title, description, icon, href, action }: any) {
    return (
        <Card className="bg-zinc-900/50 border-white/10 hover:border-amber-500/30 transition-colors group">
            <CardHeader>
                <div className="mb-4">{icon}</div>
                <CardTitle className="text-xl text-white group-hover:text-amber-500 transition-colors">{title}</CardTitle>
                <CardDescription className="text-zinc-400">{description}</CardDescription>
            </CardHeader>
            <CardContent>
                <Link href={href}>
                    <Button className="w-full bg-white text-black hover:bg-zinc-200 group-hover:bg-amber-500 group-hover:text-black transition-all">
                        {action} <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </Link>
            </CardContent>
        </Card>
    )
}
