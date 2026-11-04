"""Original line-art category and page icons (no company logos, no stock art)."""

_ICON_ATTRS = 'width="64" height="64" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"'

CATEGORY_ICONS = {
    "retail": '<svg viewBox="0 0 120 120" {attrs}><path d="M30 40 L34 20 Q36 12 44 12 H76 Q84 12 86 20 L90 40"/><rect x="24" y="40" width="72" height="60" rx="4"/><path d="M44 52 Q44 64 60 64 Q76 64 76 52"/></svg>',
    "social": '<svg viewBox="0 0 120 120" {attrs}><path d="M20 30 H100 Q108 30 108 38 V74 Q108 82 100 82 H50 L28 100 V82 H20 Q12 82 12 74 V38 Q12 30 20 30 Z"/><circle cx="45" cy="56" r="3" fill="currentColor" stroke="none"/><circle cx="60" cy="56" r="3" fill="currentColor" stroke="none"/><circle cx="75" cy="56" r="3" fill="currentColor" stroke="none"/></svg>',
    "email": '<svg viewBox="0 0 120 120" {attrs}><rect x="14" y="30" width="92" height="64" rx="4"/><path d="M18 34 L60 68 L102 34"/></svg>',
    "streaming": '<svg viewBox="0 0 120 120" {attrs}><rect x="14" y="20" width="92" height="64" rx="6"/><path d="M52 36 L74 52 L52 68 Z" fill="currentColor" stroke="none"/><path d="M40 96 H80"/></svg>',
    "telecom": '<svg viewBox="0 0 120 120" {attrs}><path d="M40 36 Q60 20 80 36"/><path d="M30 46 Q60 16 90 46"/><path d="M60 20 V36"/><circle cx="60" cy="14" r="4" fill="currentColor" stroke="none"/><rect x="48" y="60" width="24" height="40" rx="3"/></svg>',
    "shipping": '<svg viewBox="0 0 120 120" {attrs}><path d="M60 16 L104 38 V82 L60 104 L16 82 V38 Z"/><path d="M16 38 L60 58 L104 38"/><path d="M60 58 V104"/></svg>',
    "airlines": '<svg viewBox="0 0 120 120" {attrs}><path d="M10 92 L105 55 L10 18 V48 L75 55 L10 62 Z" fill="currentColor" stroke="none"/></svg>',
    "rideshare": '<svg viewBox="0 0 120 120" {attrs}><path d="M22 68 L30 46 Q33 38 42 38 H78 Q87 38 90 46 L98 68" fill="none"/><rect x="14" y="68" width="92" height="22" rx="4"/><circle cx="34" cy="92" r="9" fill="currentColor" stroke="none"/><circle cx="86" cy="92" r="9" fill="currentColor" stroke="none"/></svg>',
    "payments": '<svg viewBox="0 0 120 120" {attrs}><rect x="14" y="30" width="92" height="62" rx="8"/><path d="M14 48 H106"/><path d="M28 74 H52"/><circle cx="86" cy="74" r="7"/></svg>',
    "tech": '<svg viewBox="0 0 120 120" {attrs}><rect x="24" y="24" width="72" height="50" rx="6"/><path d="M12 92 H108 L98 74 H22 Z"/><path d="M52 84 H68"/></svg>',
    "insurance": '<svg viewBox="0 0 120 120" {attrs}><path d="M60 14 L98 28 V56 Q98 88 60 106 Q22 88 22 56 V28 Z"/><path d="M42 58 L55 71 L80 44" fill="none"/></svg>',
}
for _k in CATEGORY_ICONS:
    CATEGORY_ICONS[_k] = CATEGORY_ICONS[_k].format(attrs=_ICON_ATTRS)

ABOUT_ICON = '<svg viewBox="0 0 120 120" {attrs}><circle cx="52" cy="52" r="32"/><path d="M76 76 L100 100"/><path d="M38 52 L48 62 L68 40"/></svg>'.format(attrs=_ICON_ATTRS)

HOW_IT_WORKS_ICON = '<svg viewBox="0 0 200 60" width="180" height="54" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="20" cy="30" r="10"/><path d="M30 30 H90"/><circle cx="100" cy="30" r="10"/><path d="M110 30 H170"/><circle cx="180" cy="30" r="10"/></svg>'
