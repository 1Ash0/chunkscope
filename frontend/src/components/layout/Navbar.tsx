"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowRight, Github, User, LogOut } from "lucide-react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/useAuthStore";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export function Navbar() {
    const pathname = usePathname();
    const { user, isAuthenticated, logout } = useAuthStore();
    const router = useRouter();

    const handleLogout = () => {
        logout();
        router.push('/');
    };

    const isActive = (path: string) => pathname === path;

    return (
        <header className="w-full h-20 border-b border-white/5 bg-zinc-950/20 backdrop-blur-2xl sticky top-0 z-50">
            <div className="container mx-auto px-6 h-full flex items-center justify-between">
                <Link href="/" className="flex items-center gap-2 font-black tracking-tighter text-white hover:opacity-80 transition-opacity">
                    <span className="text-2xl">Chunk<span className="text-amber-500">Scope</span></span>
                </Link>

                <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-zinc-400">
                    <Link
                        href="/presets"
                        className={cn("hover:text-white transition-colors", isActive('/presets') && "text-white font-semibold")}
                    >
                        Templates
                    </Link>
                    <Link
                        href="/pipeline"
                        className={cn("hover:text-white transition-colors", isActive('/pipeline') && "text-white font-semibold")}
                    >
                        Builder
                    </Link>
                    <Link
                        href="/visualizer"
                        className={cn("hover:text-white transition-colors", isActive('/visualizer') && "text-white font-semibold")}
                    >
                        Visualizer
                    </Link>
                </nav>

                <div className="flex items-center gap-4">
                    {isAuthenticated && user ? (
                        <div className="flex items-center gap-3">
                            <div className="hidden sm:flex flex-col items-end">
                                <span className="text-xs font-medium text-white">{user.name}</span>
                                <Button
                                    variant="ghost"
                                    onClick={handleLogout}
                                    className="h-auto p-0 text-[10px] text-zinc-500 hover:text-red-400 flex items-center gap-1 transition-colors hover:bg-transparent"
                                >
                                    <LogOut className="h-2 w-2" />
                                    Logout
                                </Button>
                            </div>
                            <div className="h-8 w-8 rounded-full bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-500">
                                <User className="h-4 w-4" />
                            </div>
                        </div>
                    ) : (
                        <Link href="/login">
                            <Button
                                className="bg-white text-black hover:bg-zinc-200 h-9 px-4 rounded-full text-xs font-bold"
                            >
                                Sign In
                            </Button>
                        </Link>
                    )}

                    <Link href="https://github.com/1Ash0/chunkscope" className="text-zinc-400 hover:text-white transition-colors">
                        <Github className="h-5 w-5" />
                    </Link>
                </div>
            </div>
        </header>
    );
}
