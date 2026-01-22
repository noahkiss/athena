export type FontId = 'system' | 'serif' | 'mono' | 'humanist';

export type FontDefinition = {
  id: FontId;
  label: string;
  description: string;
  family: string; // CSS font-family value
};

export const fonts: Record<FontId, FontDefinition> = {
  system: {
    id: 'system',
    label: 'System',
    description: 'Native system fonts (San Francisco, Segoe UI, Roboto)',
    family:
      '-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  },
  serif: {
    id: 'serif',
    label: 'Serif',
    description: 'Classic serif for focused reading',
    family:
      'ui-serif, "New York", "Iowan Old Style", "Apple Garamond", Baskerville, "Times New Roman", "Droid Serif", "Times", serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"',
  },
  mono: {
    id: 'mono',
    label: 'Mono',
    description: 'Monospace for technical minds',
    family:
      'ui-monospace, "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", "Courier New", Courier, monospace',
  },
  humanist: {
    id: 'humanist',
    label: 'Humanist',
    description: 'Warm, approachable sans-serif',
    family:
      '"Inter Var", Inter, "Source Sans Pro", "Noto Sans", "Open Sans", system-ui, -apple-system, sans-serif',
  },
};

export const fontList = Object.values(fonts);
export const DEFAULT_FONT_ID: FontId = 'system';

export function getFont(fontId: string | null | undefined): FontDefinition {
  if (!fontId) return fonts.system;
  return fonts[fontId as FontId] ?? fonts.system;
}
