'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { analyzerApi, presetsApi } from '@/lib/api';
import {
    Upload,
    FileText,
    CheckCircle,
    AlertCircle,
    Loader2,
    ArrowRight,
    Sparkles
} from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { getErrorMessage } from '@/lib/utils';

interface AnalysisResult {
    document_id: string | null;
    document_type: string;
    structure: {
        has_headings: boolean;
        has_tables: boolean;
        has_code_blocks: boolean;
        hierarchy_depth: number;
        avg_paragraph_length: number;
    };
    density: {
        avg_sentence_length: number;
        vocabulary_richness: number;
        technical_term_density: number;
    };
    recommended_config: {
        chunking_method: string;
        chunk_size: number;
        overlap: number;
        embedding_model: string;
        retrieval_k: number;
        reranking: boolean;
    };
    confidence_score: number;
    reasoning: string;
}

export default function AnalyzePage() {
    const [file, setFile] = useState<File | null>(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [creating, setCreating] = useState(false);
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const router = useRouter();
    const { toast } = useToast();

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            if (selectedFile.type !== 'application/pdf') {
                setError('Please select a PDF file');
                setFile(null);
                return;
            }
            if (selectedFile.size > 10 * 1024 * 1024) {
                setError('File size must be less than 10MB');
                setFile(null);
                return;
            }
            setFile(selectedFile);
            setError(null);
        }
    };

    const handleAnalyze = async () => {
        if (!file) return;

        setAnalyzing(true);
        setError(null);

        try {
            const data = await analyzerApi.analyzeDocument(file);
            setResult(data);
            toast({
                title: 'Analysis Complete',
                description: 'We have generated a recommended configuration for your document.',
            });
        } catch (err: any) {
            console.error('Analysis failed:', err);
            setError(getErrorMessage(err.response?.data?.detail || err.message || 'Failed to analyze document. Please try again.'));
        } finally {
            setAnalyzing(false);
        }
    };

    const handleApplyRecommendation = async () => {
        if (!result) return;

        setCreating(true);
        try {
            // Create a new pipeline using the recommended configuration
            const response = await analyzerApi.applyPresetFromAnalysis({
                document_id: result.document_id || undefined,
                config: result.recommended_config
            });

            toast({
                title: 'Pipeline Created',
                description: 'Your RAG pipeline has been successfully configured.',
            });

            // Redirect to visualizer with the new pipeline ID
            router.push(`/visualizer?pipeline_id=${response.pipeline_id}`);
        } catch (err: any) {
            console.error('Failed to create pipeline:', err);
            toast({
                variant: 'destructive',
                title: 'Error',
                description: getErrorMessage(err.response?.data?.detail || err.message || 'Failed to create pipeline.'),
            });
        } finally {
            setCreating(false);
        }
    };

    return (
        <AuthGuard>
            <div className="min-h-screen bg-black text-white py-12 px-4">
                <div className="max-w-4xl mx-auto">
                    <div className="text-center mb-12">
                        <h1 className="text-4xl font-bold mb-4">Document Analysis</h1>
                        <p className="text-zinc-400 text-lg">
                            Upload your PDF and let AI recommend the best RAG configuration.
                        </p>
                    </div>

                    {!result ? (
                        <div className="bg-zinc-900/50 border border-white/10 rounded-3xl p-12 text-center">
                            <div className="max-w-md mx-auto">
                                <div className="mb-8 relative group">
                                    <div className="absolute inset-0 bg-amber-500/20 blur-3xl rounded-full scale-0 group-hover:scale-100 transition-transform duration-500" />
                                    <div className="relative w-20 h-20 bg-amber-500/10 rounded-2xl flex items-center justify-center mx-auto border border-amber-500/20 group-hover:border-amber-500/50 transition-colors">
                                        <Upload className="h-10 w-10 text-amber-500" />
                                    </div>
                                </div>

                                <h2 className="text-2xl font-semibold mb-2">Upload Document</h2>
                                <p className="text-zinc-500 mb-8">PDF files up to 10MB are supported.</p>

                                <div className="space-y-4">
                                    <input
                                        type="file"
                                        accept=".pdf,application/pdf"
                                        onChange={handleFileChange}
                                        className="hidden"
                                        id="file-upload"
                                    />
                                    <label
                                        htmlFor="file-upload"
                                        className="inline-flex h-12 px-8 rounded-full border border-white/20 hover:border-amber-500 transition-colors items-center gap-2 cursor-pointer"
                                    >
                                        <FileText className="h-4 w-4" />
                                        {file ? file.name : 'Choose PDF File'}
                                    </label>

                                    {error && (
                                        <div className="flex items-center gap-2 text-red-500 justify-center text-sm mt-4">
                                            <AlertCircle className="h-4 w-4" />
                                            {error}
                                        </div>
                                    )}

                                    <button
                                        onClick={handleAnalyze}
                                        disabled={!file || analyzing}
                                        className="w-full mt-6 h-12 rounded-full bg-white text-black font-bold hover:bg-zinc-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                                    >
                                        {analyzing ? (
                                            <>
                                                <Loader2 className="h-4 w-4 animate-spin" />
                                                Analyzing Content...
                                            </>
                                        ) : (
                                            'Analyze PDF'
                                        )}
                                    </button>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            {/* Analysis Summary */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="bg-zinc-900/50 border border-white/10 rounded-2xl p-6">
                                    <h3 className="text-zinc-400 text-sm uppercase tracking-wider mb-4">Document Type</h3>
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-amber-500/10 rounded-xl">
                                            <FileText className="h-6 w-6 text-amber-500" />
                                        </div>
                                        <div>
                                            <p className="text-xl font-semibold">{result.document_type}</p>
                                            <p className="text-zinc-500 text-sm font-mono">Confidence: {(result.confidence_score * 100).toFixed(0)}%</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="bg-zinc-900/50 border border-white/10 rounded-2xl p-6">
                                    <h3 className="text-zinc-400 text-sm uppercase tracking-wider mb-4">Structure Analysis</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="flex items-center gap-2 text-sm">
                                            {result.structure.has_headings ? <CheckCircle className="h-4 w-4 text-green-500" /> : <AlertCircle className="h-4 w-4 text-zinc-600" />}
                                            High-level Sections
                                        </div>
                                        <div className="flex items-center gap-2 text-sm">
                                            {result.structure.has_tables ? <CheckCircle className="h-4 w-4 text-green-500" /> : <AlertCircle className="h-4 w-4 text-zinc-600" />}
                                            Tabular Data
                                        </div>
                                        <div className="flex items-center gap-2 text-sm">
                                            {result.structure.has_code_blocks ? <CheckCircle className="h-4 w-4 text-green-500" /> : <AlertCircle className="h-4 w-4 text-zinc-600" />}
                                            Code Content
                                        </div>
                                        <div className="text-zinc-500 text-xs">
                                            Avg Para: {result.structure.avg_paragraph_length} chars
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Recommendations */}
                            <div className="bg-zinc-900/80 border border-white/10 rounded-3xl p-8 relative overflow-hidden">
                                <div className="absolute top-0 right-0 p-8 opacity-10">
                                    <Sparkles className="h-32 w-32" />
                                </div>

                                <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                                    <Sparkles className="h-6 w-6 text-amber-500" />
                                    Recommended Configuration
                                </h2>

                                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                                    <div>
                                        <p className="text-zinc-500 text-xs uppercase mb-1">Method</p>
                                        <p className="font-semibold">{result.recommended_config.chunking_method}</p>
                                    </div>
                                    <div>
                                        <p className="text-zinc-500 text-xs uppercase mb-1">Size</p>
                                        <p className="font-semibold">{result.recommended_config.chunk_size} tokens</p>
                                    </div>
                                    <div>
                                        <p className="text-zinc-500 text-xs uppercase mb-1">Overlap</p>
                                        <p className="font-semibold">{result.recommended_config.overlap} tokens</p>
                                    </div>
                                    <div>
                                        <p className="text-zinc-500 text-xs uppercase mb-1">Retrieval</p>
                                        <p className="font-semibold">k={result.recommended_config.retrieval_k}</p>
                                    </div>
                                </div>

                                <div className="p-4 bg-white/5 rounded-xl border border-white/10 mb-8">
                                    <p className="text-sm text-zinc-400 leading-relaxed italic">
                                        &ldquo;{result.reasoning}&rdquo;
                                    </p>
                                </div>

                                <div className="flex gap-4">
                                    <button
                                        onClick={handleApplyRecommendation}
                                        disabled={creating}
                                        className="flex-1 h-12 rounded-full bg-amber-500 text-black font-bold hover:bg-amber-600 transition-all flex items-center justify-center gap-2"
                                    >
                                        {creating ? (
                                            <>
                                                <Loader2 className="h-4 w-4 animate-spin" />
                                                Setting up Workspace...
                                            </>
                                        ) : (
                                            <>
                                                Use This Configuration
                                                <ArrowRight className="h-4 w-4" />
                                            </>
                                        )}
                                    </button>
                                    <button
                                        onClick={() => setResult(null)}
                                        className="px-8 h-12 rounded-full border border-white/10 hover:bg-white/5 transition-colors"
                                    >
                                        Try Another
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </AuthGuard>
    );
}
