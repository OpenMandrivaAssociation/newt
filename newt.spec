%define	major	0.52
%define	libname	%mklibname %{name} %{major}
%define	devname	%mklibname %{name} -d

%bcond_without diet
%bcond_without uclibc

Summary:	A development library for text mode user interfaces
Name:		newt
Version:	0.52.14
Release:	7
License:	LGPLv2+
Group:		System/Libraries
URL:		https://fedorahosted.org/newt/
Source0:	https://fedorahosted.org/releases/n/e/newt/%{name}-%{version}.tar.gz

Patch1: 	newt-0.52.6-mdvconf.patch
Patch2: 	newt-0.51.4-fix-wstrlen-for-non-utf8-strings.patch
Patch3: 	newt-0.51.14-assorted-fixes.patch
Patch4:		newt-0.52.14-fix-aliasing-violations.patch
Patch5:		newt-0.52.14-whole-program.patch
BuildRequires:	glibc-static-devel
BuildRequires:	popt-devel
BuildRequires:	python-devel >= 2.2
BuildRequires:	slang-devel
%if %{with diet}
BuildRequires:	dietlibc-devel
%endif
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-9
# need to make these automatic..
# we prefer linking statically against this to avoid pulling in the
# "huge" libslang library..
#BuildRequires:	uclibc-%{_lib}slang0
%endif
BuildRequires:	slang-static-devel
BuildRequires:	slang-source
BuildRequires:	gettext-devel

Provides:	python-snack
# for newt_syrup
Provides:	pythonegg(newt-python) = %{version}-%{release}
Provides:	whiptail

%description
Newt is a programming library for color text mode, widget based user
interfaces. Newt can be used to add stacked windows, entry widgets, checkboxes,
radio buttons, labels, plain text fields, scrollbars, etc., to text mode user
interfaces.  This package contains a /usr/bin/dialog replacement called
whiptail. Newt is based on the slang library.

%package -n	%{libname}
Summary:	Newt windowing toolkit development files library
Group:		Development/C

%description -n %{libname}
This package contains the shared library for %{name}.

%if %{with uclibc}
%package -n	uclibc-%{libname}
Summary:	Newt windowing toolkit development files library
Group:		Development/C

%description -n uclibc-%{libname}
This package contains the shared library for %{name}, linked against uClibc.
%endif

%package -n	%{devname}
Summary:	Newt windowing toolkit development files
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
%if %{with uclibc}
Requires:	uclibc-%{libname} = %{version}-%{release}
%endif
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{_lib}%{name}0.52-devel

%description -n %{devname}
This package contains the development files for %{name}.

%prep
%setup -q
%apply_patches

%if %{with diet}
mkdir diet
pushd diet
ln -s ../*.[ch] ../newt.spec ..*/ver .
popd
%endif

%if %{with uclibc}
mkdir uclibc
pushd uclibc
ln -s ../*.[ch] ../newt.spec ../*ver .
popd
%endif

%build
%if %{with diet}
pushd diet
../configure	--without-gpm-support \
		--without-tcl \
		--without-python \
		--disable-nls \
		CC="diet gcc" CFLAGS="-Os -g"
%make libnewt.a
popd
%endif

%if %{with uclibc}
pushd uclibc
CONFIGURE_TOP=.. \
%configure2_5x	--prefix=%{uclibc_root} \
		--libdir=%{uclibc_root}%{_libdir} \
		--with-gpm-support \
		--without-python \
		--without-tcl \
		--enable-nls \
		CC="%{uclibc_cc}" CFLAGS="%{uclibc_cflags}" \
		LDFLAGS="%{ldflags} -Wl,-O2 -flto"
%make sharedlib GNU_LD=1 WHOLE_PROGRAM=1
%make libnewt.a
popd
%endif

CONFIGURE_TOP=. \
%configure2_5x \
	--with-gpm-support \
	--without-tcl \
	CFLAGS="%{optflags} -Os" \
	LDFLAGS="%{ldflags} -Wl,-O2 -flto"
# libnewt dynamically linked against libslang:
# -rwxr-xr-x 1 root root 92520 mai   26 00:49 /usr/lib64/libnewt.so.0.52.14*
# -rwxr-xr-x 1 root root 1124544 juni   6 03:36 /usr/lib64/libslang.so.2.2.4*

# libnewt statically linked against libslang:
# -rwxr-xr-x 1 peroyvind proyvind 358000 aug.  18 11:29 libnewt.so.0.52.14*

# doing dynamic linking against libslang pulls in a dependency on a library
# that's quite huge in size, so by statically linking and only pulling in
# exactly what we need we'll save quite a lot of space
%make sharedlib GNU_LD=1 WHOLE_PROGRAM=1
%make GNU_LD=1

%install
%makeinstall_std
ln -snf lib%{name}.so.%{version} %{buildroot}%{_libdir}/lib%{name}.so.%{major}

%if %{with diet}
install -m644 diet/libnewt.a -D %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}/libnewt.a
%endif

%if %{with uclibc}
install -m644 uclibc/libnewt.a -D %{buildroot}%{uclibc_root}%{_libdir}/libnewt.a
cp -a uclibc/libnewt.so* %{buildroot}%{uclibc_root}%{_libdir}
%endif

%find_lang %{name}

%files -f %{name}.lang
%doc CHANGES COPYING
%{_bindir}/whiptail
%{py_platsitedir}/*
%{_mandir}/man1/whiptail.1*

%files -n %{libname}
%{_libdir}/libnewt.so.%{major}*

%if %{with uclibc}
%files -n uclibc-%{libname}
%{uclibc_root}%{_libdir}/libnewt.so.%{major}*
%endif

%files -n %{devname}
%doc tutorial.sgml
%{_includedir}/newt.h
%{_libdir}/libnewt.a
%if %{with diet}
%{_prefix}/lib/dietlibc/lib-%{_arch}/libnewt.a
%endif
%if %{with uclibc}
%{uclibc_root}%{_libdir}/libnewt.so
%{uclibc_root}%{_libdir}/libnewt.a
%endif
%{_libdir}/libnewt.so
%{_libdir}/pkgconfig/libnewt.pc

%changelog
* Mon Oct 29 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.52.14-7
- rebuild on ABF

* Mon Oct 29 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.52.14-6
+ Revision: 820557
- add dependency on gettext-devel
- fix uclibc library dependency
- compile in slang with -fwhole-program (P5)
- fix aliasing violations (P4)
- rebuild against latest uClibc for locale support
- statically link uClibc build of libnewt against libslang as well
- enable gpm support for uclibc build
- regenerate relevant parts of assorted fixes patch (P3)
- add buildrequires
- compile shared glibc linked library with '-Os'
- link with '-Wl,-O2 -flto'
- fix soname getting lost
- statically link in libslang as dynamically linking it in will pull in a
  dependency that's way more bigger than what we prefer for drakx installer
- do dynamically linked uclibc build as well

* Sat May 26 2012 Guilherme Moro <guilherme@mandriva.com> 0.52.14-3
+ Revision: 800758
- Add provides pythonegg(newt-python)

* Thu May 24 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.52.14-2
+ Revision: 800351
- disable NLS support for dietlibc & uclibc builds
- minor cleanups
- build static library version against uclibc & diet

* Sat Mar 31 2012 Matthew Dawkins <mattydaw@mandriva.org> 0.52.14-1
+ Revision: 788497
- new version 0.52.14
- cleaned up spec
- gpm patch upstreamed
- ldflags patch no longer needed
- assorted fixes patch no used
- dropped major from devel pkg

* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 0.52.11-4
+ Revision: 666615
- mass rebuild

* Tue Nov 02 2010 Jani Välimaa <wally@mandriva.org> 0.52.11-3mdv2011.0
+ Revision: 592225
- rebuild for python 2.7

* Sun Mar 14 2010 Oden Eriksson <oeriksson@mandriva.com> 0.52.11-2mdv2010.1
+ Revision: 519047
- rebuild

  + Sandro Cazzaniga <kharec@mandriva.org>
    - re-update to 0.52.11 after an error
    - update to 0.52.4

* Fri Sep 25 2009 Frederik Himpe <fhimpe@mandriva.org> 0.52.11-1mdv2010.0
+ Revision: 449267
- Update to new version 0.52.11 (fixes CVE-2009-2905)
- Remove patches integrated upstream
- Rediff LDFLAGS patch

* Sat Dec 27 2008 Funda Wang <fwang@mandriva.org> 0.52.6-8mdv2009.1
+ Revision: 319757
- rebuild for new python

* Wed Dec 24 2008 Oden Eriksson <oeriksson@mandriva.com> 0.52.6-7mdv2009.1
+ Revision: 318198
- use %%ldflags

* Tue Jun 17 2008 Thierry Vignaud <tv@mandriva.org> 0.52.6-5mdv2009.0
+ Revision: 223345
- rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Tue Jan 15 2008 Thierry Vignaud <tv@mandriva.org> 0.52.6-4mdv2008.1
+ Revision: 153283
- rebuild
- kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Pixel <pixel@mandriva.com>
    - rename the "snack" provide into "python-snack"
      (there is a package named libsnack which provides snack)

* Mon Aug 13 2007 Pixel <pixel@mandriva.com> 0.52.6-3mdv2008.0
+ Revision: 62757
- provide whiptail (it's clearer for a package to require "whiptail" instead of "newt")

* Mon Aug 13 2007 Pixel <pixel@mandriva.com> 0.52.6-2mdv2008.0
+ Revision: 62756
- the library should not provide newt (#32315)

* Wed May 30 2007 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 0.52.6-1mdv2008.0
+ Revision: 32788
- Added upstream/fedora patches entry, countitems, cursor, memleaks.
- Updated to version 0.52.6.
- Redid mdkconf patch -> newt-0.52.6-mdvconf.patch
- Removed allow-textbox-to-take-focus patch, not needed anymore (#15067,
  #31012).
- libnewt0.52-devel, soname change: added needed Conflicts for
  libnewt0.51-devel.

* Thu May 24 2007 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 0.51.6-14mdv2008.0
+ Revision: 30894
- Removed listbox part of patch
  do-not-ignore-EARLY-events-in-listbox--and-allow-textbox-to-take-focus
  and Renamed it to allow-textbox-to-take-focus, because it's breaking
  listbox NEWT_FLAG_RETURNEXIT feature here; with the listbox part of
  the patch applied, the newtFormRun function on exit never return the
  listbox when it's selected and Enter is pressed. From the changelogs,
  this patch is for ticket #15067, I tested it here without the listbox
  part and seems to be ok. Same description and also a testcase reported
  on bugzilla also (#31012).


* Wed Nov 22 2006 Oden Eriksson <oeriksson@mandriva.com> 0.51.6-13mdv2007.0
+ Revision: 86416
- spec file massage

  + bcornec <bcornec>
    - import newt-0.51.6-12mdk

* Mon Dec 12 2005 Gwenole Beauchesne <gbeauchesne@mandriva.com> 0.51.6-12mdk
- assorted bug fixes from code review, others are in DrakX

* Wed Apr 27 2005 Pixel <pixel@mandriva.com> 0.51.6-11mdk
- do not ignore EARLY events in listbox and allow textbox to take focus
  => this fixes drakauth which has a scrollbar for the text and also for the entries
  (bugzilla #15067)

* Sun Dec 05 2004 Michael Scherer <misc@mandrake.org> 0.51.6-10mdk
- Rebuild for new python
- fix dir ownership

* Sat Jul 24 2004 Marcel Pol <mpol@mandrake.org> 0.51.6-9mdk
- again build against new slang

* Thu Jul 22 2004 Marcel Pol <mpol@mandrake.org> 0.51.6-8mdk
- build against new slang

* Wed Jan 28 2004 Warly <warly@mandrakesoft.com> 0.51.6-7mdk
- new version
