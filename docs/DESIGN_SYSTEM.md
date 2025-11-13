# Connect Design System

## Luxury Color Palette

Inspired by Linear's minimalist aesthetic with luxury brand colors. Uses pure black (#000000) for dark mode.

### Primary Colors

```css
--primary-50: #F5F3FF    /* Lightest Purple */
--primary-100: #EDE9FE   /* Very Light Purple */
--primary-200: #DDD6FE   /* Light Purple */
--primary-300: #C4B5FD   /* Medium Light Purple */
--primary-400: #A78BFA   /* Medium Purple */
--primary-500: #8B5CF6   /* Primary Purple */
--primary-600: #7C3AED   /* Dark Purple */
--primary-700: #6D28D9   /* Darker Purple */
--primary-800: #5B21B6   /* Deep Purple */
--primary-900: #4C1D95   /* Deepest Purple */
```

### Secondary Colors (Emerald)

```css
--secondary-50: #ECFDF5   /* Lightest Emerald */
--secondary-100: #D1FAE5  /* Very Light Emerald */
--secondary-200: #A7F3D0  /* Light Emerald */
--secondary-300: #6EE7B7  /* Medium Light Emerald */
--secondary-400: #34D399  /* Medium Emerald */
--secondary-500: #10B981  /* Primary Emerald */
--secondary-600: #059669  /* Dark Emerald */
--secondary-700: #047857  /* Darker Emerald */
--secondary-800: #065F46  /* Deep Emerald */
--secondary-900: #064E3B  /* Deepest Emerald */
```

### Accent Colors (Gold)

```css
--accent-50: #FFFBEB    /* Lightest Gold */
--accent-100: #FEF3C7   /* Very Light Gold */
--accent-200: #FDE68A   /* Light Gold */
--accent-300: #FCD34D   /* Medium Light Gold */
--accent-400: #FBBF24   /* Medium Gold */
--accent-500: #F59E0B   /* Primary Gold */
--accent-600: #D97706   /* Dark Gold */
--accent-700: #B45309   /* Darker Gold */
--accent-800: #92400E   /* Deep Gold */
--accent-900: #78350F   /* Deepest Gold */
```

### Navy Blue (Professional)

```css
--navy-50: #F0F4F8     /* Lightest Navy */
--navy-100: #D9E2EC    /* Very Light Navy */
--navy-200: #BCCCDC    /* Light Navy */
--navy-300: #9FB3C8    /* Medium Light Navy */
--navy-400: #829AB1    /* Medium Navy */
--navy-500: #627D98    /* Primary Navy */
--navy-600: #486581    /* Dark Navy */
--navy-700: #334E68    /* Darker Navy */
--navy-800: #243B53    /* Deep Navy */
--navy-900: #102A43    /* Deepest Navy */
```

### Neutral Colors

#### Light Mode
```css
--gray-50: #F9FAFB     /* Lightest Gray */
--gray-100: #F3F4F6    /* Very Light Gray */
--gray-200: #E5E7EB    /* Light Gray */
--gray-300: #D1D5DB    /* Medium Light Gray */
--gray-400: #9CA3AF    /* Medium Gray */
--gray-500: #6B7280    /* Primary Gray */
--gray-600: #4B5563    /* Dark Gray */
--gray-700: #374151    /* Darker Gray */
--gray-800: #1F2937    /* Deep Gray */
--gray-900: #111827    /* Deepest Gray */
```

#### Dark Mode (Pure Black Base)
```css
--dark-bg: #000000         /* Pure Black Background */
--dark-surface: #0A0A0A    /* Surface */
--dark-elevated: #141414   /* Elevated Surface */
--dark-border: #1F1F1F     /* Borders */
--dark-hover: #262626      /* Hover State */
--dark-text-primary: #FFFFFF     /* Primary Text */
--dark-text-secondary: #A1A1A1   /* Secondary Text */
--dark-text-tertiary: #737373    /* Tertiary Text */
```

### Semantic Colors

```css
--success-light: #D1FAE5
--success: #10B981
--success-dark: #065F46

--warning-light: #FEF3C7
--warning: #F59E0B
--warning-dark: #92400E

--error-light: #FEE2E2
--error: #EF4444
--error-dark: #991B1B

--info-light: #DBEAFE
--info: #3B82F6
--info-dark: #1E40AF
```

## Typography

### Font Families

```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', 'Monaco', monospace;
--font-display: 'Cabinet Grotesk', 'Inter', sans-serif;
```

### Font Sizes (Tailwind-compatible)

```css
--text-xs: 0.75rem;      /* 12px */
--text-sm: 0.875rem;     /* 14px */
--text-base: 1rem;       /* 16px */
--text-lg: 1.125rem;     /* 18px */
--text-xl: 1.25rem;      /* 20px */
--text-2xl: 1.5rem;      /* 24px */
--text-3xl: 1.875rem;    /* 30px */
--text-4xl: 2.25rem;     /* 36px */
--text-5xl: 3rem;        /* 48px */
```

### Font Weights

```css
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;
```

### Line Heights

```css
--leading-none: 1;
--leading-tight: 1.25;
--leading-snug: 1.375;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
--leading-loose: 2;
```

## Spacing

Using 4px base unit (Tailwind default):

```css
--spacing-1: 0.25rem;    /* 4px */
--spacing-2: 0.5rem;     /* 8px */
--spacing-3: 0.75rem;    /* 12px */
--spacing-4: 1rem;       /* 16px */
--spacing-5: 1.25rem;    /* 20px */
--spacing-6: 1.5rem;     /* 24px */
--spacing-8: 2rem;       /* 32px */
--spacing-10: 2.5rem;    /* 40px */
--spacing-12: 3rem;      /* 48px */
--spacing-16: 4rem;      /* 64px */
--spacing-20: 5rem;      /* 80px */
--spacing-24: 6rem;      /* 96px */
```

## Border Radius

```css
--radius-sm: 0.25rem;    /* 4px - Small elements */
--radius-md: 0.375rem;   /* 6px - Default */
--radius-lg: 0.5rem;     /* 8px - Cards, modals */
--radius-xl: 0.75rem;    /* 12px - Large cards */
--radius-2xl: 1rem;      /* 16px - Hero sections */
--radius-full: 9999px;   /* Full rounded */
```

## Shadows

### Light Mode
```css
--shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
--shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
```

### Dark Mode
```css
--shadow-dark-sm: 0 1px 3px 0 rgb(0 0 0 / 0.5);
--shadow-dark-md: 0 4px 6px -1px rgb(0 0 0 / 0.5);
--shadow-dark-lg: 0 10px 15px -3px rgb(0 0 0 / 0.5);
--shadow-dark-xl: 0 20px 25px -5px rgb(0 0 0 / 0.7);
```

## Animations & Transitions

```css
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);

--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

## Z-Index Scale

```css
--z-dropdown: 1000;
--z-sticky: 1020;
--z-fixed: 1030;
--z-modal-backdrop: 1040;
--z-modal: 1050;
--z-popover: 1060;
--z-tooltip: 1070;
```

## Component Guidelines

### Buttons

- Primary: Purple gradient, white text
- Secondary: Navy outline, navy text
- Ghost: Transparent, colored text on hover
- Height: 36px (default), 40px (lg), 32px (sm)
- Border radius: 6px
- Font weight: 500 (medium)

### Inputs

- Height: 40px
- Border: 1px solid gray-300 (light) / dark-border (dark)
- Border radius: 6px
- Focus: Primary color ring
- Padding: 12px 16px

### Cards

- Background: White (light) / dark-elevated (dark)
- Border: 1px solid gray-200 (light) / dark-border (dark)
- Border radius: 8px
- Padding: 16px-24px
- Shadow: sm (light) / dark-sm (dark)

### Modals

- Max width: 600px (default), 900px (lg)
- Border radius: 12px
- Backdrop: rgba(0, 0, 0, 0.5) (light) / rgba(0, 0, 0, 0.8) (dark)
- Padding: 24px

## Accessibility

- Minimum contrast ratio: 4.5:1 for normal text
- Minimum contrast ratio: 3:1 for large text (18px+)
- Focus indicators: 2px solid primary color with 2px offset
- Interactive elements: Minimum 44×44px touch target

## Responsive Breakpoints

```css
--screen-sm: 640px;
--screen-md: 768px;
--screen-lg: 1024px;
--screen-xl: 1280px;
--screen-2xl: 1536px;
```

## Icon System

- Default size: 20px
- Small: 16px
- Large: 24px
- Library: Lucide React (latest)
- Stroke width: 2px
- Color: Inherits from parent
