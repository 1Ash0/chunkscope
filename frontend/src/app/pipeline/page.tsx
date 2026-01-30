import { PipelineBuilder } from '@/components/pipeline/pipeline-builder'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'

export default function PipelinePage() {
    return (
        <div className="h-screen w-screen flex flex-col bg-neutral-950 overflow-hidden">
            {/* Mini Header */}
            <header className="h-14 border-b border-white/10 flex items-center px-4 bg-black/40 backdrop-blur-md z-20 shrink-0">
                <Link href="/" className="p-2 -ml-2 rounded-full hover:bg-white/10 transition-colors text-neutral-400 hover:text-white mr-4">
                    <ArrowLeft className="w-5 h-5" />
                </Link>
                <h1 className="text-sm font-semibold text-white tracking-wide uppercase">Pipeline Editor</h1>
                <div className="ml-auto text-xs text-neutral-500 font-mono">
                    Draft Mode
                </div>
            </header>

            {/* Editor Canvas */}
            <div className="flex-1 relative">
                <PipelineBuilder />
            </div>
        </div>
    )
}
