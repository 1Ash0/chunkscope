import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

export function getErrorMessage(error: any): string {
    if (!error) return 'An unknown error occurred';

    if (typeof error === 'string') return error;

    // Handle FastAPI/Pydantic validation errors (often a list of error objects)
    if (Array.isArray(error)) {
        return error.map(err => {
            if (typeof err === 'string') return err;
            if (err && typeof err === 'object' && err.msg) return err.msg;
            return JSON.stringify(err);
        }).join('. ');
    }

    // Handle objects with msg or message fields
    if (typeof error === 'object') {
        if (error.msg) return error.msg;
        if (error.message) return error.message;
        if (error.detail) return getErrorMessage(error.detail);
        try {
            return JSON.stringify(error);
        } catch {
            return 'An unparseable error occurred';
        }
    }

    return String(error);
}
