## Singleton Pattern

The `Config` class in `src/core/config.py` implements the singleton pattern. This ensures that only one instance of the `Config` class exists throughout the application.

**Implementation Details:**

*   The `_instance` class-level attribute stores the singleton instance.
*   The `__new__(cls)` method overrides the default `__new__` method to control instance creation.
*   If `_instance` is `None`, a new instance is created and assigned to `_instance`.
*   Otherwise, the existing `_instance` is returned.

## Mixin Pattern

The `ThemeManagementMixin` class in `src/gui/theme/theme_management.py` implements the mixin pattern. This allows to add theme management capabilities to different widgets.

**Implementation Details:**

*   The `ThemeManagementMixin` class inherits from `object`.
*   The `update_theme` method updates the theme for the current component and its children.
*   The `_apply_theme_style` method applies theme-specific styling to the component.
*   The `_update_child_themes` method recursively update themes for child widgets.
*   The `set_theme_mode` method is a convenience method to update theme mode.
