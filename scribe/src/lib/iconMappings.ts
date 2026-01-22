/**
 * Emoji to Solar Icon mappings
 * Maps semantic names to Solar icon identifiers
 */

export const iconMap = {
  // Stats & Metrics
  'total-notes': 'library',
  'today-notes': 'document-add',
  'week-notes': 'calendar',
  'month-notes': 'calendar-month',

  // Sections
  'categories': 'tag',
  'recent-activity': 'bolt',
  'quick-actions': 'rocket',

  // Category Icons
  'category-projects': 'case',
  'category-people': 'users',
  'category-journal': 'notebook',
  'category-tech': 'settings',
  'category-reading': 'book-2',
  'category-wellness': 'health',
  'category-home': 'home-2',

  // File System
  'folder': 'folder',
  'folder-open': 'folder-open',
  'file': 'document',
  'file-text': 'file-text',

  // Actions
  'random': 'shuffle',
  'capture': 'pen-new-square',
  'browse': 'folder',
  'archive': 'archive-down-minimlistic',

  // Empty States
  'empty-folder': 'folder-open',
  'empty-timeline': 'calendar',
  'empty-archive': 'archive-down-minimlistic',

  // Settings
  'mobile-install': 'smartphone',
  'ios-share': 'upload',
  'android-menu': 'menu-dots-bold',

  // Navigation & UI
  'help': 'question-circle',
  'check': 'check-circle',
  'close': 'close-circle',
  'add': 'add-circle',
  'arrow-right': 'alt-arrow-right',
  'arrow-left': 'alt-arrow-left',

  // Fallback
  'default': 'document',
} as const;

export type IconName = keyof typeof iconMap;

/**
 * Get Solar icon name for semantic name
 */
export function getIcon(name: IconName | string): string {
  return iconMap[name as IconName] || iconMap.default;
}

/**
 * Category emoji to icon mapping
 */
export const categoryIcons: Record<string, string> = {
  projects: 'case',
  people: 'users',
  journal: 'notebook',
  tech: 'settings',
  reading: 'book-2',
  wellness: 'health',
  home: 'home-2',
};

/**
 * Get category icon name
 */
export function getCategoryIcon(category: string): string {
  return categoryIcons[category.toLowerCase()] || 'folder';
}
