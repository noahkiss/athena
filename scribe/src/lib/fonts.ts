/**
 * Font System - 3-category font management
 *
 * Fonts are organized into three categories:
 * - Headers: Display fonts for headings (h1-h6)
 * - Body: Readable fonts for body text
 * - Mono: Monospace fonts for code/editor
 */

export type FontCategory = 'header' | 'body' | 'mono';

export type HeaderFontId = 'inter' | 'roboto-flex' | 'rubik' | 'atkinson-hyperlegible' | 'eb-garamond' | 'fraunces';
export type BodyFontId = 'inter' | 'atkinson-hyperlegible' | 'source-sans-3' | 'noto-sans' | 'literata' | 'ibm-plex-sans';
export type MonoFontId = 'fira-code' | 'jetbrains-mono' | 'source-code-pro' | 'ibm-plex-mono' | 'cascadia-code' | 'system-mono';

export type FontId = HeaderFontId | BodyFontId | MonoFontId;

export interface FontDefinition {
  id: string;
  category: FontCategory;
  label: string;
  description: string;
  family: string;
  variable?: boolean; // True if font uses variable font technology
  fallback: string;
}

/* ============================================================================
   HEADER FONTS
   ============================================================================ */

export const headerFonts: Record<HeaderFontId, FontDefinition> = {
  'inter': {
    id: 'inter',
    category: 'header',
    label: 'Inter',
    description: 'Clean, modern sans-serif with excellent readability',
    family: '"Inter Variable", Inter',
    variable: true,
    fallback: 'sans-serif',
  },
  'roboto-flex': {
    id: 'roboto-flex',
    category: 'header',
    label: 'Roboto Flex',
    description: 'Google\'s flexible, geometric sans-serif',
    family: '"Roboto Flex", Roboto',
    variable: true,
    fallback: 'sans-serif',
  },
  'rubik': {
    id: 'rubik',
    category: 'header',
    label: 'Rubik',
    description: 'Rounded, friendly sans-serif with personality',
    family: 'Rubik',
    variable: false,
    fallback: 'sans-serif',
  },
  'atkinson-hyperlegible': {
    id: 'atkinson-hyperlegible',
    category: 'header',
    label: 'Atkinson Hyperlegible',
    description: 'Designed for maximum legibility and accessibility',
    family: '"Atkinson Hyperlegible"',
    variable: false,
    fallback: 'sans-serif',
  },
  'eb-garamond': {
    id: 'eb-garamond',
    category: 'header',
    label: 'EB Garamond',
    description: 'Classic serif for elegant, traditional look',
    family: '"EB Garamond"',
    variable: false,
    fallback: 'serif',
  },
  'fraunces': {
    id: 'fraunces',
    category: 'header',
    label: 'Fraunces',
    description: 'Expressive display font with character',
    family: '"Fraunces Variable", Fraunces',
    variable: true,
    fallback: 'serif',
  },
};

/* ============================================================================
   BODY FONTS
   ============================================================================ */

export const bodyFonts: Record<BodyFontId, FontDefinition> = {
  'inter': {
    id: 'inter',
    category: 'body',
    label: 'Inter',
    description: 'Clean, modern sans-serif with excellent readability',
    family: '"Inter Variable", Inter',
    variable: true,
    fallback: 'sans-serif',
  },
  'atkinson-hyperlegible': {
    id: 'atkinson-hyperlegible',
    category: 'body',
    label: 'Atkinson Hyperlegible',
    description: 'Designed for maximum legibility and accessibility',
    family: '"Atkinson Hyperlegible"',
    variable: false,
    fallback: 'sans-serif',
  },
  'source-sans-3': {
    id: 'source-sans-3',
    category: 'body',
    label: 'Source Sans 3',
    description: 'Adobe\'s versatile, readable sans-serif',
    family: '"Source Sans 3"',
    variable: false,
    fallback: 'sans-serif',
  },
  'noto-sans': {
    id: 'noto-sans',
    category: 'body',
    label: 'Noto Sans',
    description: 'Google\'s universal, harmonious sans-serif',
    family: '"Noto Sans Variable", "Noto Sans"',
    variable: true,
    fallback: 'sans-serif',
  },
  'literata': {
    id: 'literata',
    category: 'body',
    label: 'Literata',
    description: 'Serif optimized for extended reading',
    family: 'Literata',
    variable: false,
    fallback: 'serif',
  },
  'ibm-plex-sans': {
    id: 'ibm-plex-sans',
    category: 'body',
    label: 'IBM Plex Sans',
    description: 'IBM\'s corporate sans-serif with warmth',
    family: '"IBM Plex Sans"',
    variable: false,
    fallback: 'sans-serif',
  },
};

/* ============================================================================
   MONOSPACE FONTS
   ============================================================================ */

export const monoFonts: Record<MonoFontId, FontDefinition> = {
  'fira-code': {
    id: 'fira-code',
    category: 'mono',
    label: 'Fira Code',
    description: 'Popular coding font with programming ligatures',
    family: '"Fira Code Variable", "Fira Code"',
    variable: true,
    fallback: 'monospace',
  },
  'jetbrains-mono': {
    id: 'jetbrains-mono',
    category: 'mono',
    label: 'JetBrains Mono',
    description: 'Optimized for developers, great for long sessions',
    family: '"JetBrains Mono"',
    variable: false,
    fallback: 'monospace',
  },
  'source-code-pro': {
    id: 'source-code-pro',
    category: 'mono',
    label: 'Source Code Pro',
    description: 'Adobe\'s clean, professional monospace',
    family: '"Source Code Pro Variable", "Source Code Pro"',
    variable: true,
    fallback: 'monospace',
  },
  'ibm-plex-mono': {
    id: 'ibm-plex-mono',
    category: 'mono',
    label: 'IBM Plex Mono',
    description: 'IBM\'s monospace with character',
    family: '"IBM Plex Mono"',
    variable: false,
    fallback: 'monospace',
  },
  'cascadia-code': {
    id: 'cascadia-code',
    category: 'mono',
    label: 'Cascadia Code',
    description: 'Microsoft\'s modern coding font',
    family: '"Cascadia Code"',
    variable: false,
    fallback: 'monospace',
  },
  'system-mono': {
    id: 'system-mono',
    category: 'mono',
    label: 'System Mono',
    description: 'Native system monospace fonts',
    family: 'ui-monospace, "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace',
    variable: false,
    fallback: 'monospace',
  },
};

/* ============================================================================
   EXPORTS & HELPERS
   ============================================================================ */

export const headerFontList = Object.values(headerFonts);
export const bodyFontList = Object.values(bodyFonts);
export const monoFontList = Object.values(monoFonts);

export const DEFAULT_HEADER_FONT: HeaderFontId = 'inter';
export const DEFAULT_BODY_FONT: BodyFontId = 'inter';
export const DEFAULT_MONO_FONT: MonoFontId = 'fira-code';

export function getHeaderFont(fontId: string | null | undefined): FontDefinition {
  if (!fontId) return headerFonts[DEFAULT_HEADER_FONT];
  return headerFonts[fontId as HeaderFontId] ?? headerFonts[DEFAULT_HEADER_FONT];
}

export function getBodyFont(fontId: string | null | undefined): FontDefinition {
  if (!fontId) return bodyFonts[DEFAULT_BODY_FONT];
  return bodyFonts[fontId as BodyFontId] ?? bodyFonts[DEFAULT_BODY_FONT];
}

export function getMonoFont(fontId: string | null | undefined): FontDefinition {
  if (!fontId) return monoFonts[DEFAULT_MONO_FONT];
  return monoFonts[fontId as MonoFontId] ?? monoFonts[DEFAULT_MONO_FONT];
}

/**
 * Get the full CSS font-family value with fallback
 */
export function getFontFamily(font: FontDefinition): string {
  return `${font.family}, ${font.fallback}`;
}
