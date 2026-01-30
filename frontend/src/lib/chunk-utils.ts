export interface Rect {
    x: number;
    y: number;
    width: number;
    height: number;
}

export interface Point {
    x: number;
    y: number;
}

/**
 * Generates N perceptually distinct colors using the Golden Ratio method.
 * Returns colors in HSL format for CSS usage.
 */
export function generateDistinctColors(count: number, saturation = 70, lightness = 50): string[] {
    const colors: string[] = [];
    const goldenRatio = 0.618033988749895;
    let hue = 0; // consistent start for reproducibility

    for (let i = 0; i < count; i++) {
        hue = (hue + goldenRatio) % 1;
        const h = Math.floor(hue * 360);
        colors.push(`hsl(${h}, ${saturation}%, ${lightness}%)`);
    }

    return colors;
}

/**
 * Checks if a point is inside a rectangle.
 */
export function isPointInRect(point: Point, rect: Rect): boolean {
    return (
        point.x >= rect.x &&
        point.x <= rect.x + rect.width &&
        point.y >= rect.y &&
        point.y <= rect.y + rect.height
    );
}

/**
 * Converts screen coordinates (mouse event) to PDF coordinates (points).
 */
export function screenToPdfCoordinates(
    screenX: number,
    screenY: number,
    scale: number,
    canvasRect: DOMRect
): Point {
    return {
        x: (screenX - canvasRect.left) / scale,
        y: (screenY - canvasRect.top) / scale,
    };
}
