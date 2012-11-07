#
# spec file for package utempter
#
# Copyright (c) 2011 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#



Name:           utempter
%define utmpGroup utmp
Version:        0.5.5
Release:        152
License:        MIT
Summary:        A privileged helper for utmp and wtmp updates
Group:          Productivity/Security
# bug437293
%ifarch ppc64
Obsoletes:      utempter-64bit
%endif
Source:         utempter-%{version}.tar.gz
Source2:        baselibs.conf
Patch0:         utempter.eal3.diff
Patch1:         utempter-0.5.5-pie.diff
Patch2:         utempter-ppc64.patch
#
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%description
Utempter is a utility that allows non-privileged applications such as
terminal emulators to modify the utmp database without having to be
setuid root.

%package devel
License:        MIT
Summary:        Development files for utempter
Group:          Development/Libraries/C and C++
Requires:       %{name} = %{version}

%description devel
Utempter is a privileged helper for utmp and wtmp updates.  This
package contains the development files needed.

%prep
%setup -q
%patch0 -p1
%patch1
%patch2 -p1

%build
make %{?_smp_mflags} RPM_OPT_FLAGS="%{optflags}" CC="gcc"

%install
export DESTDIR=%{buildroot}
make PREFIX=$DESTDIR LIBDIR=%{_libdir} install
chmod 755 $DESTDIR%{_libdir}/libutempter.so*
/sbin/ldconfig -n $DESTDIR%{_libdir}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(444,root,root,755)
%doc COPYING
%attr(02755, root, %{utmpGroup}) /usr/sbin/utempter
%attr(555,root,root) %{_libdir}/libutempter.so.*
%attr(444,root,root) %doc /usr/share/man/man8/*

%files devel
%defattr(444,root,root,755)
%attr(555,root,root) %{_libdir}/libutempter.so
%attr(444,root,root) /usr/include/utempter.h

%changelog
