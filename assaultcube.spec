Name:		assaultcube
Version:	1.1.0.4
Release:	3%{?dist}

# Licensing is complex
# Details at http://packages.debian.org/changelogs/pool/contrib/a/assaultcube/assaultcube_1.1.0.4+dfsg2-1/assaultcube.copyright
# http://packages.debian.org/changelogs/pool/non-free/a/assaultcube-data/assaultcube-data_1.1.0.4+repack1-2/assaultcube-data.copyright
# Engine is under the Cube license.  Free but GPL incompatible
# https://lists.fedoraproject.org/pipermail/legal/2013-March/002104.html

License:	Cube and MIT and GPLv2+ and Redistributable
Group:		Amusements/Games
Summary:	Total conversion of Cube first person shooter
URL:		http://assault.cubers.net/index.html
Source0:	http://downloads.sourceforge.net/actiongame/AssaultCube_v%{version}_source.tar.bz2
Source1:   http://downloads.sourceforge.net/actiongame/AssaultCube_v%{version}.tar.bz2
Source2:	AssaultCube-startscript.sh
Source3:	AssaultCube-server.sh
Patch0:		001-assaultcube_1.1.0.4-mga-add_X11_lib_to_linker.patch
BuildRequires:	SDL-devel
BuildRequires:	SDL_image-devel
BuildRequires:	zlib-devel
BuildRequires:	mesa-libGL-devel
BuildRequires:	openal-devel
BuildRequires:	libvorbis-devel
BuildRequires:  gettext
BuildRequires:  desktop-file-utils

%description
AssaultCube is a total conversion of Wouter van Oortmerssen's FPS called Cube.
Set in a realistic looking environment, gameplay is fast and arcade. This game
is all about team oriented multiplayer fun. Similar to counterstrike.

%prep
%setup -q -n %{version}
%setup -q -T -D -b 1 -n %{version}
%patch0 -p1

chmod -x source/enet/include/enet/unix.h
chmod -x source/enet/host.c
chmod -x source/enet/include/enet/list.h
chmod -x source/enet/protocol.c
chmod -x source/enet/unix.c
chmod -x source/enet/packet.c
chmod -x source/enet/list.c
chmod -x source/enet/include/enet/protocol.h
chmod -x source/enet/include/enet/enet.h
chmod -x source/enet/include/enet/types.h
chmod -x source/enet/peer.c
chmod -x docs/colouredtext.txt

iconv --from=ISO-8859-1 --to=UTF-8 docs/package_copyrights.txt > docs/package_copyrights.txt.new 
touch -r docs/package_copyrights.txt docs/package_copyrights.txt.new
mv docs/package_copyrights.txt.new docs/package_copyrights.txt


%build
pushd source/src
# flags for enet:
#export CFLAGS="%rpmoptflags"
#export CXXFLAGS="%rpmoptflags"
# flags for engine:
#make CXXOPTFLAGS="%rpmoptflags"
make
popd




%install

pwd

install -dm 755 %{buildroot}%{_libexecdir}
install -m 755 source/src/ac_client \
	%{buildroot}%{_libexecdir}/assaultcube_client.real
install -m 755 source/src/ac_server \
	%{buildroot}%{_libexecdir}/assaultcube_server.real

install -dm 755 %{buildroot}%{_datadir}
install -dm 755 %{buildroot}%{_datadir}/%{name}
for i in config packages; do
	cp -R $i \
		%{buildroot}%{_datadir}/%{name}
	find %{buildroot}%{_datadir}/%{name}/$i -type f -exec chmod 644 {} \;
done

# chmod o+rwt %{buildroot}%{_datadir}/%{name}/packages/maps

# startscripts
install -dm 755 %{buildroot}%{_bindir}
install -m 755 %{SOURCE2} %{buildroot}%{_bindir}/%{name}
install -m 755 %{SOURCE3} %{buildroot}%{_bindir}/%{name}_server

# icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/{16x16,32x32,48x48}/apps
install -m644 docs/pics/%{name}.png -D %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{name}.png


cat > %{name}.desktop << EOF
[Desktop Entry]
Name=AssualtCube
Comment=AssaultCube is a total conversion of Wouter van Oortmerssen's FPS called Cube
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
%doc source/*.txt README.html
%doc docs
%{_bindir}/assaultcube
%{_bindir}/assaultcube_server
%{_libexecdir}/assaultcube_client.real
%{_libexecdir}/assaultcube_server.real
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*

%{_datadir}/applications/%{name}*.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png

%changelog
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
