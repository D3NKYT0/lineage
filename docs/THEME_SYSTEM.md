# Theme and Template System

## Overview
The theme system allows you to customize the site's appearance by uploading ZIP packages containing templates, styles, scripts, and assets. Each theme can be activated/deactivated and has customizable variables for internationalization and visual personalization.

---

## How it works
- **Main model:** `Theme` (apps.main.administrator.models)
- **Upload:** The admin uploads a ZIP file containing the theme.
- **Validation:** The ZIP must contain a `theme.json` file with required metadata (`name`, `slug`, etc).
- **Extraction:** Files are extracted to `themes/installed/<slug>/`.
- **Activation:** Only one theme can be active at a time. When a theme is activated, others are automatically deactivated.
- **Removal:** When deleting a theme, the ZIP and the extracted folder are removed.

---

## Expected ZIP Structure
- Allowed files: `.html`, `.css`, `.js`, images, fonts, etc.
- Required file: `theme.json` with metadata and variables.
- Example of `theme.json`:
  ```json
  {
    "name": "Example Theme",
    "slug": "example-theme",
    "version": "1.0",
    "author": "Your Name",
    "description": "Theme description.",
    "variables": [
      {"name": "Primary Color", "tipo": "string", "valor_pt": "#123456", "valor_en": "#123456", "valor_es": "#123456"}
    ]
  }
  ```

---

## Theme Variables
- Defined in `theme.json` and saved as `ThemeVariable`.
- Support internationalization (`valor_pt`, `valor_en`, `valor_es`).
- Available in template context via context processor.
- Example of usage in template:
  ```django
  <style>body { background: {{ example_theme_primary_color }}; }</style>
  ```

---

## Template Context
- The `active_theme` context processor injects into the context:
  - `active_theme`: slug of the active theme
  - `base_template`: path to the theme's base.html
  - `theme_slug`, `path_theme`, `theme_files`
- The `theme_variables` context processor injects all theme variables.
- The `background_setting` context processor injects the active background image.

---

## Page Rendering
- Function `render_theme_page` (in `utils/render_theme_page.py`):
  - Tries to render the template from the active theme.
  - If it does not exist, falls back to the default template.
- Example of usage:
  ```python
  return render_theme_page(request, 'public', 'index.html', context)
  ```

---

## Serving Theme Files
- The `serve_theme_file` view allows serving HTML files from the active theme securely.
- Checks for file existence and returns 404 if not found.

---

## Security
- Only files with allowed extensions are extracted.
- Paths are validated to prevent path traversal.
- Maximum ZIP size: 30MB.

---

## Tips
- Always include a `base.html` in the theme for template inheritance.
- Use variables to facilitate customization without editing files.
- Test the theme in multiple languages. 