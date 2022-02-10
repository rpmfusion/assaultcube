%global commit 752950989b4e286459ca9aee3d61a868d7b20fa4
%global date 20160227
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name: assaultcube
Version: 1.2.0.3
Release: 0.15.%{date}git%{shortcommit}%{?dist}

# Licensing is complex
# Details at http://packages.debian.org/changelogs/pool/contrib/a/assaultcube/assaultcube_1.1.0.4+dfsg2-1/assaultcube.copyright
# http://packages.debian.org/changelogs/pool/non-free/a/assaultcube-data/assaultcube-data_1.1.0.4+repack1-2/assaultcube-data.copyright
# Engine is under the Cube license.  Free but GPL incompatible
# https://lists.fedoraproject.org/pipermail/legal/2013-March/002104.html

License: Cube and MIT and GPLv2+ and Redistributable
Group: Amusements/Games
Summary: Total conversion of Cube first person shooter
URL: http://assault.cubers.net
Source0: https://github.com/assaultcube/AC/archive/%{commit}.zip#/AC-%{shortcommit}.zip
Source1: %{name}.png
Source2: AssaultCube-startscript.sh
Source3: AssaultCube-server.sh

BuildRequires: pkgconfig(sdl)
BuildRequires: pkgconfig(SDL_image)
BuildRequires: pkgconfig(zlib)
BuildRequires: pkgconfig(gl)
BuildRequires: pkgconfig(openal)
BuildRequires: pkgconfig(vorbis)
BuildRequires: pkgconfig(libcurl)
BuildRequires: gcc-c++
BuildRequires: gettext
BuildRequires: pkgconfig
BuildRequires: desktop-file-utils

%description
AssaultCube is a total conversion of Wouter van Oortmerssen's FPS called Cube.
Set in a realistic looking environment, gameplay is fast and arcade. This game
is all about team oriented multiplayer fun. Similar to counterstrike.

%prep
%setup -q -n AC-%{commit}

# Remove precompiled files for Windows
rm -rf bin_win32

##Remove spurious executable permissions
for i in `find . -type f \( -name "*.h" -o -name "*.c" -name "*.txt" \)`; do
chmod a-x $i
done

iconv --from=ISO-8859-1 --to=UTF-8 docs/package_copyrights.txt > docs/package_copyrights.txt.new
touch -r docs/package_copyrights.txt docs/package_copyrights.txt.new
mv docs/package_copyrights.txt.new docs/package_copyrights.txt

# Update enet to fix ppc64le build
rm -f ./source/enet/config.guess
rm -f ./source/enet/config.sub
cp -fv /usr/lib/rpm/redhat/config.guess ./source/enet/config.guess
cp -fv /usr/lib/rpm/redhat/config.sub ./source/enet/config.sub

%build
# https://github.com/assaultcube/AC/issues/148
%if 0%{?fedora} > 23
sed -e 's|-Wall||g' -i source/src/Makefile
AC_FLAGS=$(echo "%{optflags}" | sed -e 's/-Wall/-Wno-misleading-indentation -Wformat/g')
%else
AC_FLAGS="%{optflags}"
%endif
make -C source/src %{?_smp_mflags} \
 CXX=g++ CC=gcc \
 CXXFLAGS="$AC_FLAGS -fPIC -pie" \
 CXXFLAGS+="-fsigned-char -ffast-math -rdynamic" \
 CFLAGS="$AC_FLAGS -Wl,-z,relro -fPIC -pie -Wl,-z,now" \
 CXXOPTFLAGS="$AC_FLAGS -fPIC -pie" \
 LDFLAGS="%{__global_ldflags} -fPIC -pie -Wl,-z,now"

%install
install -dm 755 %{buildroot}%{_libexecdir}
install -pm 755 source/src/ac_client \
	%{buildroot}%{_libexecdir}/assaultcube_client.real
install -pm 755 source/src/ac_server \
	%{buildroot}%{_libexecdir}/assaultcube_server.real

install -dp packages/audio %{buildroot}%{_datadir}/%{name}
install -dp packages/crosshairs %{buildroot}%{_datadir}/%{name}
install -dp packages/maps %{buildroot}%{_datadir}/%{name}
install -dp packages/misc %{buildroot}%{_datadir}/%{name}
install -dp packages/models %{buildroot}%{_datadir}/%{name}
install -dp packages/textures %{buildroot}%{_datadir}/%{name}
install -dp packages/locale %{buildroot}%{_datadir}/%{name}
for i in config packages; do
	cp -R $i \
		%{buildroot}%{_datadir}/%{name}
	find %{buildroot}%{_datadir}/%{name}/$i -type f -exec chmod 644 {} \;
done

# startscripts
install -dpm 755 %{buildroot}%{_bindir}
install -pm 755 %{SOURCE2} %{buildroot}%{_bindir}/%{name}
install -pm 755 %{SOURCE3} %{buildroot}%{_bindir}/%{name}_server

# icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/{16x16,32x32,48x48}/apps
install -pm 644 %{SOURCE1} -D %{buildroot}%{_datadir}/icons/hicolor/48x48/apps

# Set exe permission
chmod a+x %{buildroot}%{_datadir}/%{name}/config/convert_mapconfig.sh
rm -f %{buildroot}%{_datadir}/%{name}/packages/locale/AC.lang

# Make .desktop files
cat > %{name}.desktop << EOF
[Desktop Entry]
Name=AssualtCube
Comment=AssaultCube is a total conversion of Wouter van Oortmerssen s FPS called Cube
Exec=%{_bindir}/%{name}
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=false
Categories=Game;ArcadeGame;
EOF

cat > %{name}_server.desktop << EOF
[Desktop Entry]
Name=AssaultCube-Server
Comment=AssaultCube Server
Exec=%{_bindir}/%{name}_server
Icon=%{name}
Terminal=true
Type=Application
StartupNotify=true
Categories=Game;ArcadeGame;
EOF

cat > %{name}_server_lan.desktop << EOF
[Desktop Entry]
Name=AssaultCube-Server-Lan
Comment=AssaultCube Server (private)
Exec=%{_bindir}/%{name}_server -mlocalhost
Icon=%{name}
Terminal=true
Type=Application
StartupNotify=true
Categories=Game;ArcadeGame;
EOF

mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install --dir=%{buildroot}%{_datadir}/applications/ %{name}.desktop
desktop-file-install --dir=%{buildroot}%{_datadir}/applications/ %{name}_server.desktop
desktop-file-install --dir=%{buildroot}%{_datadir}/applications/ %{name}_server_lan.desktop

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%doc source/README.txt
%license source/README_CUBEENGINE.txt
%{_bindir}/assaultcube
%{_bindir}/assaultcube_server
%{_libexecdir}/assaultcube_client.real
%{_libexecdir}/assaultcube_server.real
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}*.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png

%changelog
* Thu Feb 10 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 1.2.0.3-0.15.20160227git7529509
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Tue Aug 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.2.0.3-0.14.20160227git7529509
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Thu Feb 04 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.2.0.3-0.13.20160227git7529509
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Aug 19 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.2.0.3-0.12.20160227git7529509
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Feb 05 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.2.0.3-0.11.20160227git7529509
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sat Aug 10 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.2.0.3-0.10.20160227git7529509
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Mar 05 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.2.0.3-0.9.20160227git7529509
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sun Aug 19 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 1.2.0.3-0.8.20160227git7529509
- Rebuilt for Fedora 29 Mass Rebuild binutils issue

* Fri Jul 27 2018 RPM Fusion Release Engineering <sergio@serjux.com> - 1.2.0.3-0.7.20160227git7529509
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Mar 02 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 1.2.0.3-0.6.20160227git7529509
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 1.2.0.3-0.5.20160227git7529509
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Apr 17 2017 Leigh Scott <leigh123linux@googlemail.com> - 1.2.0.3-0.4.20160227git7529509
- Fix ppc64le build

* Sat Mar 25 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 1.2.0.3-0.3.20160227git7529509
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sun Feb 28 2016 Sérgio Basto <sergio@serjux.com> - 1.2.0.3-0.2.20160227git7529509
- Minor improvements

* Sat Feb 27 2016 Antonio Trande <sagitter@fedoraproject.org> - 1.2.0.3-0.1.20160227git7529509
- Update to commit 7529509
- Patched for GCC6
- Disable 'misleading-indentation' warning with GCC6
- Packaged assaultcube.png icon

* Fri Feb 26 2016 Antonio Trande <sagitter@fedoraproject.org> - 1.2.0.2-1
- Update to 1.2.0.2
- Set GCC as compiler
- Set compiler flags
- Set PIE flag

* Sun Aug 31 2014 Sérgio Basto <sergio@serjux.com> - 1.1.0.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue May 21 2013 Rahul Sundaram <sundaram@fedoraproject.org> - 1.1.0.4-3
- add build requires on desktop-file-utils

* Sat Apr 20 2013 Rahul Sundaram <sundaram@fedoraproject.org> - 1.1.0.4-2
- replace Expat with MIT as license tag
- fix sf url to follow guidelines
- fix spurious executable permission in several files
- fix utf8 warning in package_copyrights.txt
- use pushd/popd instead of cd
- drop use of make_install macro and convert command
- use desktop-file-install to install the three desktop files

* Sun Mar 03 2013 Rahul Sundaram <sundaram@fedoraproject.org> - 1.1.0.4-1
- initial spec, largely based on Mageia
