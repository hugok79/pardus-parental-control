project('pardus-parental-control', license: 'GPL-3.0')

# Dependencies
gnome = import('gnome')
gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)

# Set Install Paths
prefix = get_option('prefix')
share = join_paths(prefix, 'share')

binary_dir = join_paths(prefix, 'bin')
source_dir = join_paths(share, 'pardus', meson.project_name()) # /usr/share/pardus/pardus-parental-control

icon_dir = join_paths(share, 'icons', 'hicolor', 'scalable', 'apps')
desktop_file_dir = join_paths(share, 'applications')

# Translations
subdir('po')

# Polkit
subdir('polkit')

# Assets
install_subdir('assets', install_dir: source_dir)

# Install
## Desktop File
install_data(
  ['export/tr.org.pardus.parental-control.desktop'],
  install_dir: desktop_file_dir,
)
## Icon
install_data(['export/pardus-parental-control.svg'], install_dir: icon_dir)
## Sources
install_subdir('src', install_dir: source_dir)
install_subdir('ui', install_dir: source_dir)

## Binary
install_data(['pardus-parental-control'], install_dir: binary_dir)
