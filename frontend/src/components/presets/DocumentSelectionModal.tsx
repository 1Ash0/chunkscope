"use client"

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { documentsApi } from '@/lib/api'
import { Loader2, X, Upload, FileText } from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'

interface DocumentSelectionModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: (documentId: string) => void;
    onUseDemo: () => void;
    presetName: string;
}

export function DocumentSelectionModal({ isOpen, onClose, onSuccess, onUseDemo, presetName }: DocumentSelectionModalProps) {
    const [loading, setLoading] = useState(false)
    const [file, setFile] = useState<File | null>(null)
    const { toast } = useToast()

    if (!isOpen) return null

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0])
        }
    }

    const handleUpload = async () => {
        if (!file) return
        setLoading(true)
        try {
            const response = await documentsApi.uploadDocument(file)
            toast({
                title: "Document Uploaded",
                description: "Your document is ready for processing.",
            })
            onSuccess(response.id)
        } catch (error: any) {
            console.error("Upload error:", error)
            toast({
                title: "Upload Failed",
                description: typeof error.response?.data?.detail === 'string'
                    ? error.response.data.detail
                    : JSON.stringify(error.response?.data?.detail || "Failed to upload document"),
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

                <Card className="bg-zinc-950 border-white/10 shadow-2xl">
                    <CardHeader>
                        <CardTitle className="text-white">Select Document</CardTitle>
                        <CardDescription className="text-zinc-500">
                            Choose a document to analyse with the <strong>{presetName}</strong> pipeline.
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-6">
                        {/* Option 1: Upload */}
                        <div className="space-y-4 rounded-lg bg-zinc-900/50 p-4 border border-white/5">
                            <div className="flex items-center gap-2 mb-2">
                                <div className="p-2 rounded-full bg-amber-500/10 text-amber-500">
                                    <Upload className="h-4 w-4" />
                                </div>
                                <Label className="text-sm font-medium text-white">Upload Custom Document</Label>
                            </div>

                            <div className="space-y-2">
                                <Input
                                    type="file"
                                    accept=".pdf,.txt,.md"
                                    onChange={handleFileChange}
                                    className="bg-zinc-900 border-white/10 text-zinc-300 file:text-zinc-300 file:bg-zinc-800 file:border-0 file:rounded-md file:mr-4 hover:file:bg-zinc-700 cursor-pointer"
                                />
                                <p className="text-xs text-zinc-500">Supports PDF, TXT, MD (max 100MB)</p>
                            </div>

                            <Button
                                onClick={handleUpload}
                                disabled={!file || loading}
                                className="w-full bg-amber-500 text-black hover:bg-amber-600 font-medium"
                            >
                                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Upload & Create Pipeline
                            </Button>
                        </div>

                        <div className="relative">
                            <div className="absolute inset-0 flex items-center">
                                <span className="w-full border-t border-white/10" />
                            </div>
                            <div className="relative flex justify-center text-xs uppercase">
                                <span className="bg-zinc-950 px-2 text-zinc-500">Or continue with</span>
                            </div>
                        </div>

                        {/* Option 2: Demo Doc */}
                        <Button
                            variant="outline"
                            onClick={onUseDemo}
                            disabled={loading}
                            className="w-full justify-between h-auto py-4 bg-transparent border-white/10 hover:bg-zinc-900 text-zinc-300 hover:text-white Group"
                        >
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-full bg-zinc-800 text-zinc-400 group-hover:text-white">
                                    <FileText className="h-4 w-4" />
                                </div>
                                <div className="text-left">
                                    <div className="font-medium">Use Demo Document</div>
                                    <div className="text-xs text-zinc-500">Standard PDF for testing</div>
                                </div>
                            </div>
                            <span className="text-xs text-amber-500 group-hover:underline">Select &rarr;</span>
                        </Button>

                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
