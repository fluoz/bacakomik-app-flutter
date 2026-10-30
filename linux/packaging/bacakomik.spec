# Package the Flutter release bundle without stripping its prebuilt libraries.
%global debug_package %{nil}
%global __os_install_post %{nil}

Name:           bacakomik
Version:        %{app_version}
Release:        1
Summary:        Reader for manga, manhwa and manhua
License:        GPL-3.0-only
URL:            https://github.com/sofyan-rs/bacakomik-app-flutter
Source0:        %{name}-%{version}.tar.gz
BuildArch:      x86_64

# ELF dependencies are detected automatically. GStreamer's playback plugins
# are loaded at runtime and must be required explicitly.
Requires:       gtk3
Requires:       gstreamer1-plugins-base

%description
Browse, read and download manga, manhwa and manhua from extension sources,
with bookmarks, reading history and offline reading.

%prep
%setup -q

%build
# Already compiled by flutter build linux --release.

%install
mkdir -p %{buildroot}/opt/%{name} %{buildroot}%{_bindir}
cp -a bundle/. %{buildroot}/opt/%{name}/
ln -s /opt/%{name}/%{name} %{buildroot}%{_bindir}/%{name}
install -Dm644 bacakomik.desktop %{buildroot}%{_datadir}/applications/bacakomik.desktop
install -Dm644 bacakomik.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/bacakomik.png

%files
%license LICENSE
/opt/%{name}/
%{_bindir}/%{name}
%{_datadir}/applications/bacakomik.desktop
%{_datadir}/icons/hicolor/512x512/apps/bacakomik.png
