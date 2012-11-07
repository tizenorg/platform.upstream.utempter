Summary:   A privileged helper for utmp/wtmp updates.
Name:      utempter
Version:   0.5.5
Release:   1
License:   MIT/LGPL
Group:     System Environment/Base
Source:    utempter-%{version}.tar.gz
Prereq:    /usr/sbin/groupadd, /sbin/ldconfig, fileutils
BuildRoot: %{_tmppath}/%{name}-%{version}-root

%description
Utempter is a utility which allows some non-privileged programs to
have required root access without compromising system
security. Utempter accomplishes this feat by acting as a buffer
between root and the programs.

%prep
%setup  -q

%build
make RPM_OPT_FLAGS="$RPM_OPT_FLAGS"

%install
rm -rf $RPM_BUILD_ROOT
make PREFIX=$RPM_BUILD_ROOT LIBDIR=%{_libdir} install
/sbin/ldconfig -n $RPM_BUILD_ROOT/%{_libdir}

%clean
rm -rf $RPM_BUILD_ROOT

%pre 
%{_sbindir}/groupadd -g 22 -r -f utmp || :

%post
{
    /sbin/ldconfig
    for file in /var/log/wtmp /var/run/utmp ; do
        if [ -f $file ]; then
            chown root:utmp $file
            chmod 664 $file
        fi
    done
}

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%attr(02755, root, utmp) %{_sbindir}/utempter
%doc COPYING
%{_libdir}/libutempter.so*
%{_includedir}/utempter.h

%changelog
* Mon Apr 19 2004 Mike A. Harris <mharris@redhat.com> 0.5.5-1
- [SECURITY] Fix CAN-2004-0233 utempter directory traversal symlink attack
  issue for immediate erratum release.
- Build all-arch test package 0.5.5-1 in dist-fc2-scratch

* Mon Feb 23 2004 Mike A. Harris <mharris@redhat.com> 0.5.4-1
- Rewrote post install script to be a bit cleaner and rebuilt in rawhide to
  pick up twaugh's chown change
- Added 'srpm-x' target to Makefile for package maintainer SRPM building

* Mon Feb 23 2004 Tim Waugh <twaugh@redhat.com>
- Use ':' instead of '.' as separator for chown.

* Fri May 30 2003 Mike A. Harris <mharris@redhat.com> 0.5.3-1
- Bump version and release and rebuild to strip debug info into .debuginfo
  package, as the Red Hat Linux 9 package shipped unstripped (#91664)
- Updated license field to reflect dual license MIT style + LGPL
- Changed spec file Copyright tag to proper License tag
- Removed stupid crackrock "version" macro define

* Tue Feb 18 2003 Matt Wilson <msw@redhat.com> 0.5.2-16
- get the second SIGCHLD SIG_IGN case too (#84571)

* Tue Feb 11 2003 Bill Nottingham <notting@redhat.com> 0.5.2-15
- don't set SIGCHLD handler to SIG_IGN and then wait

* Tue Feb 04 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- add symlink to shared lib
- internal sync

* Tue Oct  8 2002 Mike A. Harris <mharris@redhat.com> 0.5.2-12
- All-arch rebuild
- Removed dumb usage of {version} in Version: tag

* Thu Sep  5 2002 Mike A. Harris <mharris@redhat.com> 0.5.2-11hammer
- Updated BuildRoot line to meet Red Hat standards
- Updated filelist to use rpm macros for _libdir, etc.
- Added comment to top of specfile to remind people to check utempter changes
  into CVS, since utempter IS managed by CVS afterall...  I will fix the
  missing bits in CVS soon once the package is reassigned to me
- Added 'LIBDIR=%{_libdir}' to make commandline for proper x86_64 build
- Added libdir patch to Makefile

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu Jun 20 2002 Elliot Lee <sopwith@redhat.com> 0.5.2-9
- Don't strip binary

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sun Jun 24 2001 Elliot Lee <sopwith@redhat.com>
- Bump release + rebuild.

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Sat Jun 17 2000 Matt Wilson <msw@redhat.com>
- defattr root

* Thu Feb 24 2000 Erik Troan <ewt@redhat.com>
- added LGPL notice

* Mon Sep 13 1999 Bill Nottingham <notting@redhat.com>
- strip utempter

* Mon Aug 30 1999 Bill Nottingham <notting@redhat.com>
- add utmp as group 22

* Fri Jun  4 1999 Jeff Johnson <jbj@redhat.com>
- ignore SIGCHLD while processing utmp.
