export type ThemeId =
  | 'default'
  | 'dracula'
  | 'catppuccin-latte'
  | 'catppuccin-frappe'
  | 'catppuccin-macchiato'
  | 'catppuccin-mocha';

export type ThemeDefinition = {
  id: ThemeId;
  label: string;
  group: string;
  themeColor: string;
  colors: {
    bg: string;
    surface: string;
    surfaceAlt: string;
    surfaceMuted: string;
    border: string;
    text: string;
    textMuted: string;
    textSubtle: string;
    accentRgb: string;
    accentHover: string;
    accentContrast: string;
    focusRgb: string;
    dangerRgb: string;
    warningRgb: string;
    successRgb: string;
  };
  categories: string[];
};

export const themes: Record<ThemeId, ThemeDefinition> = {
  default: {
    id: 'default',
    label: 'Midnight',
    group: 'Default',
    themeColor: '#0b1120',
    colors: {
      bg: '#0b1120',
      surface: '#111827',
      surfaceAlt: '#1f2937',
      surfaceMuted: '#0f172a',
      border: '#1f2937',
      text: '#f3f4f6',
      textMuted: '#9ca3af',
      textSubtle: '#6b7280',
      accentRgb: '59 130 246',
      accentHover: '#2563eb',
      accentContrast: '#f8fafc',
      focusRgb: '56 189 248',
      dangerRgb: '248 113 113',
      warningRgb: '251 191 36',
      successRgb: '52 211 153',
    },
    categories: [
      '96 165 250',
      '167 139 250',
      '74 222 128',
      '34 211 238',
      '251 191 36',
      '244 114 182',
      '251 146 60',
      '94 234 212',
    ],
  },
  dracula: {
    id: 'dracula',
    label: 'Dracula',
    group: 'Dracula',
    themeColor: '#282a36',
    colors: {
      bg: '#282a36',
      surface: '#2f3242',
      surfaceAlt: '#3b3f52',
      surfaceMuted: '#1f222d',
      border: '#44475a',
      text: '#f8f8f2',
      textMuted: '#c0c3d8',
      textSubtle: '#6272a4',
      accentRgb: '189 147 249',
      accentHover: '#a679f6',
      accentContrast: '#1b1c24',
      focusRgb: '139 233 253',
      dangerRgb: '255 85 85',
      warningRgb: '241 250 140',
      successRgb: '80 250 123',
    },
    categories: [
      '139 233 253',
      '255 121 198',
      '80 250 123',
      '189 147 249',
      '255 184 108',
      '241 250 140',
      '255 85 85',
      '98 114 164',
    ],
  },
  'catppuccin-latte': {
    id: 'catppuccin-latte',
    label: 'Latte',
    group: 'Catppuccin',
    themeColor: '#eff1f5',
    colors: {
      bg: '#eff1f5',
      surface: '#e6e9ef',
      surfaceAlt: '#dce0e8',
      surfaceMuted: '#ccd0da',
      border: '#bcc0cc',
      text: '#4c4f69',
      textMuted: '#5c5f77',
      textSubtle: '#8c8fa1',
      accentRgb: '30 102 245',
      accentHover: '#1a5ad7',
      accentContrast: '#f8fafc',
      focusRgb: '32 159 181',
      dangerRgb: '210 15 57',
      warningRgb: '223 142 29',
      successRgb: '64 160 43',
    },
    categories: [
      '30 102 245',
      '136 57 239',
      '64 160 43',
      '32 159 181',
      '223 142 29',
      '234 118 203',
      '254 100 11',
      '114 135 253',
    ],
  },
  'catppuccin-frappe': {
    id: 'catppuccin-frappe',
    label: 'Frappe',
    group: 'Catppuccin',
    themeColor: '#303446',
    colors: {
      bg: '#303446',
      surface: '#414559',
      surfaceAlt: '#51576d',
      surfaceMuted: '#292c3c',
      border: '#626880',
      text: '#c6d0f5',
      textMuted: '#b5bfe2',
      textSubtle: '#737994',
      accentRgb: '140 170 238',
      accentHover: '#85c1dc',
      accentContrast: '#1e1e2e',
      focusRgb: '129 200 190',
      dangerRgb: '231 130 132',
      warningRgb: '229 200 144',
      successRgb: '166 209 137',
    },
    categories: [
      '140 170 238',
      '202 158 230',
      '166 209 137',
      '129 200 190',
      '229 200 144',
      '244 184 228',
      '239 159 118',
      '153 209 219',
    ],
  },
  'catppuccin-macchiato': {
    id: 'catppuccin-macchiato',
    label: 'Macchiato',
    group: 'Catppuccin',
    themeColor: '#24273a',
    colors: {
      bg: '#24273a',
      surface: '#363a4f',
      surfaceAlt: '#494d64',
      surfaceMuted: '#1f2234',
      border: '#5b6078',
      text: '#cad3f5',
      textMuted: '#b8c0e0',
      textSubtle: '#6e738d',
      accentRgb: '138 173 244',
      accentHover: '#7dc4e4',
      accentContrast: '#1d1f2b',
      focusRgb: '125 196 228',
      dangerRgb: '237 135 150',
      warningRgb: '245 169 127',
      successRgb: '166 218 149',
    },
    categories: [
      '138 173 244',
      '198 160 246',
      '166 218 149',
      '139 213 202',
      '238 212 159',
      '245 189 230',
      '245 169 127',
      '183 189 248',
    ],
  },
  'catppuccin-mocha': {
    id: 'catppuccin-mocha',
    label: 'Mocha',
    group: 'Catppuccin',
    themeColor: '#1e1e2e',
    colors: {
      bg: '#1e1e2e',
      surface: '#313244',
      surfaceAlt: '#45475a',
      surfaceMuted: '#181825',
      border: '#585b70',
      text: '#cdd6f4',
      textMuted: '#bac2de',
      textSubtle: '#6c7086',
      accentRgb: '137 180 250',
      accentHover: '#74c7ec',
      accentContrast: '#1e1e2e',
      focusRgb: '116 199 236',
      dangerRgb: '243 139 168',
      warningRgb: '250 179 135',
      successRgb: '166 227 161',
    },
    categories: [
      '137 180 250',
      '203 166 247',
      '166 227 161',
      '148 226 213',
      '249 226 175',
      '245 194 231',
      '250 179 135',
      '116 199 236',
    ],
  },
};

export const themeList = Object.values(themes);
export const DEFAULT_THEME_ID: ThemeId = 'default';

export function getTheme(themeId: string | null | undefined): ThemeDefinition {
  if (!themeId) return themes.default;
  return themes[themeId as ThemeId] ?? themes.default;
}

export function themeToCssVars(theme: ThemeDefinition): string {
  const vars: Record<string, string> = {
    '--color-bg': theme.colors.bg,
    '--color-surface': theme.colors.surface,
    '--color-surface-alt': theme.colors.surfaceAlt,
    '--color-surface-muted': theme.colors.surfaceMuted,
    '--color-border': theme.colors.border,
    '--color-text': theme.colors.text,
    '--color-text-muted': theme.colors.textMuted,
    '--color-text-subtle': theme.colors.textSubtle,
    '--accent-rgb': theme.colors.accentRgb,
    '--accent-hover': theme.colors.accentHover,
    '--accent-contrast': theme.colors.accentContrast,
    '--focus-rgb': theme.colors.focusRgb,
    '--danger-rgb': theme.colors.dangerRgb,
    '--warning-rgb': theme.colors.warningRgb,
    '--success-rgb': theme.colors.successRgb,
  };

  theme.categories.forEach((color, index) => {
    vars[`--category-${index + 1}-rgb`] = color;
  });

  return Object.entries(vars)
    .map(([key, value]) => `${key}: ${value};`)
    .join(' ');
}
