/**
 * Emoji to Solar Icon mappings
 * Maps semantic names to Solar icon identifiers
 */

export const iconMap = {
  // Stats & Metrics
  'total-notes': 'library-linear',
  'today-notes': 'document-add-linear',
  'week-notes': 'calendar-linear',
  'month-notes': 'calendar-minimalistic-linear',

  // Sections
  'categories': 'tag-linear',
  'recent-activity': 'bolt-linear',
  'quick-actions': 'rocket-linear',

  // Category Icons
  'category-projects': 'case-linear',
  'category-people': 'users-group-rounded-linear',
  'category-journal': 'notebook-linear',
  'category-tech': 'settings-linear',
  'category-reading': 'book-2-linear',
  'category-wellness': 'health-linear',
  'category-home': 'home-2-linear',

  // File System
  'folder': 'folder-linear',
  'folder-open': 'folder-open-linear',
  'file': 'document-linear',
  'file-text': 'file-text-linear',

  // Actions
  'random': 'shuffle-linear',
  'capture': 'pen-new-square-linear',
  'browse': 'folder-linear',
  'archive': 'archive-down-minimlistic-linear',

  // Empty States
  'empty-folder': 'folder-open-linear',
  'empty-timeline': 'calendar-linear',
  'empty-archive': 'archive-down-minimlistic-linear',

  // Settings
  'mobile-install': 'smartphone-linear',
  'ios-share': 'upload-linear',
  'android-menu': 'menu-dots-bold',

  // Navigation & UI
  'help': 'question-circle-linear',
  'check': 'check-circle-linear',
  'close': 'close-circle-linear',
  'add': 'add-circle-linear',
  'arrow-right': 'alt-arrow-right-linear',
  'arrow-left': 'alt-arrow-left-linear',

  // Fallback
  'default': 'document-linear',
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
  projects: 'case-linear',
  people: 'users-group-rounded-linear',
  journal: 'notebook-linear',
  tech: 'settings-linear',
  reading: 'book-2-linear',
  wellness: 'health-linear',
  home: 'home-2-linear',
};

/**
 * Get category icon name
 */
export function getCategoryIcon(category: string): string {
  return categoryIcons[category.toLowerCase()] || 'folder';
}
