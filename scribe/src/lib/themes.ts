export type ThemeId =
  | 'default'
  | 'cobalt2'
  | 'dracula'
  | 'catppuccin-latte'
  | 'catppuccin-frappe'
  | 'catppuccin-macchiato'
  | 'catppuccin-mocha'
  | 'github-dark-high-contrast'
  | 'github-dark-dimmed'
  | 'github-light'
  | 'rose-pine-moon'
  | 'rose-pine-dawn';

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
  cobalt2: {
    id: 'cobalt2',
    label: 'Cobalt2',
    group: 'Cobalt2',
    themeColor: '#122738',
    colors: {
      bg: '#122738',
      surface: '#193549',
      surfaceAlt: '#234a5f',
      surfaceMuted: '#0d1f2d',
      border: '#0050a4',
      text: '#ffffff',
      textMuted: '#80fcff',
      textSubtle: '#0088ff',
      accentRgb: '255 198 0',
      accentHover: '#ffa500',
      accentContrast: '#122738',
      focusRgb: '128 252 255',
      dangerRgb: '255 98 140',
      warningRgb: '255 198 0',
      successRgb: '58 217 0',
    },
    categories: [
      '255 198 0',
      '251 148 255',
      '58 217 0',
      '128 252 255',
      '0 136 255',
      '255 98 140',
      '0 80 164',
      '255 255 255',
    ],
  },
  'github-dark-high-contrast': {
    id: 'github-dark-high-contrast',
    label: 'Dark High Contrast',
    group: 'GitHub',
    themeColor: '#010409',
    colors: {
      bg: '#010409',
      surface: '#0d1117',
      surfaceAlt: '#161b22',
      surfaceMuted: '#06090c',
      border: '#30363d',
      text: '#f0f3f6',
      textMuted: '#d9dee3',
      textSubtle: '#9ea7b3',
      accentRgb: '113 183 255',
      accentHover: '#539bf5',
      accentContrast: '#010409',
      focusRgb: '57 197 207',
      dangerRgb: '255 148 146',
      warningRgb: '240 183 47',
      successRgb: '38 205 77',
    },
    categories: [
      '113 183 255',
      '203 158 255',
      '38 205 77',
      '57 197 207',
      '240 183 47',
      '255 148 146',
      '145 203 255',
      '255 177 175',
    ],
  },
  'github-dark-dimmed': {
    id: 'github-dark-dimmed',
    label: 'Dark Dimmed',
    group: 'GitHub',
    themeColor: '#1c2128',
    colors: {
      bg: '#1c2128',
      surface: '#2d333b',
      surfaceAlt: '#373e47',
      surfaceMuted: '#161a1f',
      border: '#444c56',
      text: '#adbac7',
      textMuted: '#909dab',
      textSubtle: '#636e7b',
      accentRgb: '83 155 245',
      accentHover: '#4184e4',
      accentContrast: '#1c2128',
      focusRgb: '57 197 207',
      dangerRgb: '244 112 103',
      warningRgb: '198 144 38',
      successRgb: '87 171 90',
    },
    categories: [
      '83 155 245',
      '176 131 240',
      '87 171 90',
      '57 197 207',
      '218 170 63',
      '220 189 251',
      '108 182 255',
      '255 147 138',
    ],
  },
  'github-light': {
    id: 'github-light',
    label: 'Light Legacy',
    group: 'GitHub',
    themeColor: '#f6f8fa',
    colors: {
      bg: '#f6f8fa',
      surface: '#ffffff',
      surfaceAlt: '#f3f4f6',
      surfaceMuted: '#e5e7ea',
      border: '#d0d7de',
      text: '#586069',
      textMuted: '#6a737d',
      textSubtle: '#959da5',
      accentRgb: '3 102 214',
      accentHover: '#005cc5',
      accentContrast: '#ffffff',
      focusRgb: '27 124 131',
      dangerRgb: '215 58 73',
      warningRgb: '219 171 9',
      successRgb: '40 167 69',
    },
    categories: [
      '3 102 214',
      '90 50 163',
      '40 167 69',
      '27 124 131',
      '219 171 9',
      '203 36 49',
      '49 146 170',
      '176 0 32',
    ],
  },
  'rose-pine-moon': {
    id: 'rose-pine-moon',
    label: 'Moon',
    group: 'Rosé Pine',
    themeColor: '#2a273f',
    colors: {
      bg: '#2a273f',
      surface: '#393552',
      surfaceAlt: '#37344d',
      surfaceMuted: '#232136',
      border: '#44415a',
      text: '#e0def4',
      textMuted: '#908caa',
      textSubtle: '#6e6a86',
      accentRgb: '156 207 216',
      accentHover: '#7ab8c2',
      accentContrast: '#2a273f',
      focusRgb: '234 154 151',
      dangerRgb: '235 111 146',
      warningRgb: '246 193 119',
      successRgb: '62 143 176',
    },
    categories: [
      '156 207 216',
      '196 167 231',
      '62 143 176',
      '234 154 151',
      '246 193 119',
      '235 111 146',
      '144 140 170',
      '224 222 244',
    ],
  },
  'rose-pine-dawn': {
    id: 'rose-pine-dawn',
    label: 'Dawn',
    group: 'Rosé Pine',
    themeColor: '#fffaf3',
    colors: {
      bg: '#fffaf3',
      surface: '#f2e9e1',
      surfaceAlt: '#f3eeea',
      surfaceMuted: '#faf4ed',
      border: '#dfdad9',
      text: '#575279',
      textMuted: '#797593',
      textSubtle: '#9893a5',
      accentRgb: '86 148 159',
      accentHover: '#56949f',
      accentContrast: '#fffaf3',
      focusRgb: '215 130 126',
      dangerRgb: '180 99 122',
      warningRgb: '234 157 52',
      successRgb: '40 105 131',
    },
    categories: [
      '86 148 159',
      '144 122 169',
      '40 105 131',
      '215 130 126',
      '234 157 52',
      '180 99 122',
      '121 117 147',
      '87 82 121',
    ],
  },
};

export const themeList = Object.values(themes);
export const DEFAULT_THEME_ID: ThemeId = 'default';
export const DEFAULT_LIGHT_THEME_ID: ThemeId = 'rose-pine-dawn';
export const DEFAULT_DARK_THEME_ID: ThemeId = 'catppuccin-mocha';

export function getTheme(themeId: string | null | undefined): ThemeDefinition {
  if (!themeId) return themes.default;
  return themes[themeId as ThemeId] ?? themes.default;
}

export function getDefaultThemeForColorScheme(prefersDark: boolean): ThemeDefinition {
  return prefersDark ? themes[DEFAULT_DARK_THEME_ID] : themes[DEFAULT_LIGHT_THEME_ID];
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
