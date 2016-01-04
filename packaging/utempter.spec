Name:           utempter
%define utmpGroup utmp
Version:        0.5.5
Release:        0
License:        MIT
Summary:        A privileged helper for utmp and wtmp updates
Group:          Productivity/Security
Source:         utempter-%{version}.tar.gz
Source2:        baselibs.conf
Source1001: 	utempter.manifest

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
cp %{SOURCE1001} .

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
%manifest %{name}.manifest
%defattr(444,root,root,755)
%doc COPYING
%attr(02755, root, %{utmpGroup}) /usr/sbin/utempter
%attr(555,root,root) %{_libdir}/libutempter.so.*
%attr(444,root,root) %doc /usr/share/man/man8/*

%files devel
%manifest %{name}.manifest
%defattr(444,root,root,755)
%attr(555,root,root) %{_libdir}/libutempter.so
%attr(444,root,root) /usr/include/utempter.h

%changelog
