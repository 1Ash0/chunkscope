'use client'

import React, { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
    children: ReactNode
}

interface State {
    hasError: boolean
    error: Error | null
}

export class GlobalErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null
    }

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error }
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo)
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex flex-col items-center justify-center bg-black text-white p-6 text-center">
                    <h1 className="text-4xl font-bold mb-4 text-amber-500">Something went wrong</h1>
                    <p className="text-zinc-400 mb-8 max-w-md">
                        The application crashed during runtime. This might be due to a WebGL issue or a hydration mismatch.
                    </p>
                    <pre className="bg-zinc-900 border border-white/10 p-4 rounded-lg text-left text-xs overflow-auto max-w-full mb-8 font-mono text-red-400">
                        {this.state.error?.toString()}
                    </pre>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-6 py-2 bg-white text-black font-bold rounded-full hover:bg-zinc-200 transition-colors"
                    >
                        Reload Page
                    </button>
                </div>
            )
        }

        return this.props.children
    }
}
