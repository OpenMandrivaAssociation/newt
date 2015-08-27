%define	major 0.52
%define	libname	%mklibname %{name} %{major}
%define	devname	%mklibname %{name} -d

%bcond_without dietlibc
%bcond_with uclibc

Summary:	A development library for text mode user interfaces
Name:		newt
Version:	0.52.18
Release:	5
License:	LGPLv2+
Group:		System/Libraries
Url:		https://fedorahosted.org/newt/
Source0:	https://fedorahosted.org/releases/n/e/newt/%{name}-%{version}.tar.gz
Patch1: 	newt-0.52.6-mdvconf.patch
Patch2: 	newt-0.51.4-fix-wstrlen-for-non-utf8-strings.patch
Patch3: 	newt-0.51.14-assorted-fixes.patch

BuildRequires:	glibc-static-devel
BuildRequires:	slang-static-devel
BuildRequires:	slang-source
BuildRequires:	gettext-devel
BuildRequires:	pkgconfig(popt)
BuildRequires:	pkgconfig(python3)
BuildRequires:	pkgconfig(slang)
%if %{with diet}
BuildRequires:	dietlibc-devel
%endif
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-9
BuildRequires:	uclibc-popt-devel
BuildRequires:	uclibc-slang-devel
# need to make these automatic..
# we prefer linking statically against this to avoid pulling in the
# "huge" libslang library..
#BuildRequires:	uclibc-%{_lib}slang0
%endif

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

%package -n	uclibc-%{devname}
Summary:	Newt windowing toolkit development files
Group:		Development/C
Requires:	uclibc-%{libname} = %{EVRD}
Requires:	%{devname} = %{EVRD}
Provides:	uclibc-%{name}-devel = %{EVRD}
Conflicts:	%{devname} < 0.52.18-2

%description -n uclibc-%{devname}
This package contains the development files for uclibc-%{name}.
%endif

%package -n	%{devname}
Summary:	Newt windowing toolkit development files
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{_lib}%{name}0.52-devel

%description -n %{devname}
This package contains the development files for %{name}.

%prep
%setup -q
%apply_patches
autoreconf -fiv

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
ln -s ../*.ac .
popd
%endif

%build
export PYTHON=%{__python}

%if %{with diet}
pushd diet
../configure \
	--without-gpm-support \
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
%configure \
	--prefix=%{uclibc_root} \
	--libdir=%{uclibc_root}%{_libdir} \
	--with-gpm-support \
	--without-python \
	--without-tcl \
	--enable-nls \
	CC="%{uclibc_cc}" CFLAGS="-fPIC %{uclibc_cflags}" \
	LDFLAGS="%{ldflags} -Wl,-O2 -flto"
%make sharedlib GNU_LD=1 WHOLE_PROGRAM=1
%make libnewt.a
popd
%endif

CONFIGURE_TOP=. \
%configure \
	--with-gpm-support \
	--without-tcl \
	CFLAGS="-fPIC %{optflags}" \
%ifnarch %armx %ix86
	LDFLAGS="%{ldflags} -Wl,-O2 -flto"
%else
	LDFLAGS="%{ldflags} -Wl,-O2"
%endif
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

%files -n uclibc-%{devname}
%{uclibc_root}%{_libdir}/libnewt.so
%{uclibc_root}%{_libdir}/libnewt.a
%endif

%files -n %{devname}
%doc tutorial.sgml
%{_includedir}/newt.h
%{_libdir}/libnewt.a
%if %{with diet}
%{_prefix}/lib/dietlibc/lib-%{_arch}/libnewt.a
%endif
%{_libdir}/libnewt.so
%{_libdir}/pkgconfig/libnewt.pc
